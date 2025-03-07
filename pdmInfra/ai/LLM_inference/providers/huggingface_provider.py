"""
This module handles inference requests to HuggingFace's hosted endpoints.
"""
import requests
import json
import re
from pdmInfra.ai.json_schema import structuredOutputBaseModel, functionCallingBaseModel
from pdmInfra.ai.LLM_inference.openai_tools import openai_message_history
from pdmInfra.ai.param import huggingfaceEndpoints, huggingfaceLLMList

def huggingface_structured_output_extraction(response):
    """Extract structured output content from HuggingFace response"""
    try:
        content = response['choices'][0]['message']['content']
        
        # Try to extract JSON from potential markdown code blocks
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
        if json_match and json_match.group(1):
            return json.loads(json_match.group(1).strip())
        
        # Try parsing the content directly as JSON
        return json.loads(content)
    except Exception as e:
        print(f"Failed to parse structured output JSON: {e}")
        return content

def extract_function_call_from_text(text):
    """Extract function call from text content"""
    try:
        # Look for function call patterns like "function_name(args)"
        func_match = re.search(r'(\w+)\(({.*?})\)', text, re.DOTALL)
        if func_match:
            func_name = func_match.group(1)
            args_json = func_match.group(2)
            return {
                "name": func_name,
                "arguments": json.loads(args_json)
            }
        
        # Look for Tool/Function format in JSON blocks
        tool_match = re.search(r'```(?:json)?\s*({[\s\S]*?})\s*```', text, re.DOTALL)
        if tool_match:
            tool_json = json.loads(tool_match.group(1))
            if "name" in tool_json and "arguments" in tool_json:
                return tool_json
        
        return None
    except Exception as e:
        print(f"Error extracting function call: {e}")
        return None

def huggingface_function_call_extraction(response):
    """Extract function call content from HuggingFace response"""
    content = response['choices'][0]['message']['content']
    
    # HuggingFace endpoints might return function calls in different formats
    # Try to extract from text content
    extracted_call = extract_function_call_from_text(content)
    if extracted_call:
        return extracted_call
    
    # If no function call format detected, return the raw content
    return content

def huggingface_chat_content_extraction(response):
    """Extract chat content from HuggingFace response"""
    return response['choices'][0]['message']['content']

def huggingface_inference(
    system_message: str,
    model: str,
    api_key: str,
    user_message=None,
    chat_history=None,
    temperature: float = 0,
    streaming: bool = False,
    structured_output=None,
    max_tokens=None,
    tool_pack=None
):
    """Handle inference requests specifically for HuggingFace models."""
    
    # Get the endpoint URL for the model
    if model not in huggingfaceLLMList:
        raise ValueError(f"Model {model} is not supported by HuggingFace endpoints")
    
    url = huggingfaceEndpoints[model]
    
    # Prepare the payload
    payload = {
        "model": "tgi",
        "messages": [],
        "temperature": temperature
    }
    
    # Add system message
    if system_message:
        payload["messages"].append({
            "role": "system",
            "content": system_message
        })
    
    # Add chat history
    if chat_history:
        if isinstance(chat_history, openai_message_history):
            chat_history = chat_history.chat_history
        payload["messages"].extend(chat_history)
    
    # Add user message
    if user_message:
        payload["messages"].append({
            "role": "user",
            "content": user_message
        })
    
    # Handle structured output
    if structured_output:
        if not issubclass(structured_output, structuredOutputBaseModel):
            raise ValueError("Structured output must be a structuredOutputBaseModel")
        
        # Add instructions for structured output
        schema_str = json.dumps(structured_output.generate_structured_output("openai"), indent=2)
        payload["messages"][-1]["content"] += f"\n\nPlease format your response as a JSON object according to this schema:\n{schema_str}"
    
    # Handle function calling tools
    if tool_pack:
        if isinstance(tool_pack, list):
            if len(tool_pack) == 0:
                raise ValueError("Tool pack cannot be empty")
            if not all(issubclass(tool, functionCallingBaseModel) for tool in tool_pack):
                raise ValueError("Tool pack must be a list of functionCallingBaseModel classes")
            
            # Format tools similar to OpenAI format
            tools_json = [tool.generate_function_tool("openai") for tool in tool_pack]
            tool_instructions = json.dumps(tools_json, indent=2)
            payload["messages"][-1]["content"] += f"\n\nYou have access to the following tools:\n{tool_instructions}\nUse the tools when appropriate."
        
        elif issubclass(tool_pack, functionCallingBaseModel):
            tool_json = tool_pack.generate_function_tool("openai")
            tool_instructions = json.dumps(tool_json, indent=2)
            payload["messages"][-1]["content"] += f"\n\nYou have access to the following tool:\n{tool_instructions}\nUse the tool when appropriate."
        
        else:
            raise ValueError("Tool pack must be a functionCallingBaseModel class or an array of such classes")
    
    # Add max tokens if specified
    if max_tokens:
        payload["max_tokens"] = max_tokens
    
    # Configure streaming if requested
    if streaming:
        payload["stream"] = True
    
    # Set up headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Handle streaming response
    if streaming:
        response = requests.post(url, json=payload, headers=headers, stream=True)
        
        def generate():
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        line = line[6:]  # Remove 'data: ' prefix
                        if line == '[DONE]':
                            break
                        try:
                            chunk = json.loads(line)
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                if 'content' in delta and delta['content']:
                                    yield delta['content']
                        except json.JSONDecodeError:
                            continue
        
        return generate()
    
    # Handle non-streaming response
    response = requests.post(url, json=payload, headers=headers)
    response_json = response.json()
    
    # Process response based on request type
    if structured_output:
        return huggingface_structured_output_extraction(response_json)
    elif tool_pack:
        return huggingface_function_call_extraction(response_json)
    else:
        return huggingface_chat_content_extraction(response_json) 