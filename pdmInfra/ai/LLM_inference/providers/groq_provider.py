"""
This module handles inference requests to Groq's API.
"""
import requests
import json
from pdmInfra.ai.json_schema import structuredOutputBaseModel, functionCallingBaseModel
from pdmInfra.ai.LLM_inference.openai_tools import (
    openai_function_call_extraction,
    openai_structured_output_extraction,
    openai_chat_content_extraction,
    openai_message_history
)

def groq_inference(
    system_message: str,
    model: str,
    api_key: str,
    user_message=None,
    chat_history=None,
    temperature: float = 0.0,
    streaming: bool = False,
    tool_pack=None,
    structured_output=None,
    max_tokens: int = None
):
    """Handle inference requests specifically for Groq models."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    # Prepare the payload
    payload = {
        "model": model,
        "messages": [],
        "temperature": temperature
    }

    # Add system message if provided
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
        
        # In Groq, implement structured output as a forced function call
        payload["tools"] = [structured_output.generate_structured_output("groq")]
        payload["tool_choice"] = {"type": "function", "function": {"name": structured_output.__name__}}
        
    # Handle function calling tools
    if tool_pack:
        if isinstance(tool_pack, list):
            if len(tool_pack) == 0:
                raise ValueError("Tool pack cannot be empty")
            if not all(issubclass(tool, functionCallingBaseModel) for tool in tool_pack):
                raise ValueError("Tool pack must be a list of functionCallingBaseModel classes")
            payload["tools"] = [tool.generate_function_tool("groq") for tool in tool_pack]
        elif issubclass(tool_pack, functionCallingBaseModel):
            payload["tools"] = [tool_pack.generate_function_tool("groq")]
        else:
            raise ValueError("Tool pack must be a list or dictionary")
        
    # Add max tokens if specified
    if max_tokens:
        payload["max_tokens"] = max_tokens

    # Configure streaming if requested
    if streaming:
        payload["stream"] = True

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    response = requests.post(url, json=payload, headers=headers, stream=streaming)

    if streaming:
        def generate():
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        line = line[6:]  # Remove 'data: ' prefix
                    if line != '[DONE]':
                        try:
                            chunk = json.loads(line)
                            delta = chunk['choices'][0]['delta']
                            if 'content' in delta:
                                yield delta['content']
                        except json.JSONDecodeError:
                            print(f"Error decoding JSON: {line}")
        return generate()

    # Process the response based on request type
    if tool_pack:
        try:
            response.json()['choices'][0]['message']['tool_calls']
            output = openai_function_call_extraction(response.json())
        except:
            output = openai_chat_content_extraction(response.json())
    elif structured_output:
        output = openai_function_call_extraction(response.json())[0]["arguments"] # Hot patch for groq structured output since it returns a list of tool calls
    else: 
        output = openai_chat_content_extraction(response.json())

    return output
