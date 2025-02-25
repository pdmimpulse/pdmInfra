"""
This module handles inference requests to Mistral's API.
"""
import requests
import json
from pdmInfra.ai.json_schema import structuredOutputBaseModel, functionCallingBaseModel
from pdmInfra.ai.LLM_inference.openai_tools import openai_message_history

def mistral_inference(
    system_message: str,
    model: str,
    api_key: str,
    user_message=None,
    chat_history=None,
    temperature: float = 0,
    streaming: bool = False,
    structured_output=None,
    tool_pack=None,
    max_tokens: int = None
):
    """Handle inference requests specifically for Mistral models."""
    url = "https://api.mistral.ai/v1/chat/completions"
    
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
        schema_dict = structured_output.generate_structured_output("mistral")
        payload["response_format"] = schema_dict
        
    if tool_pack:
        if isinstance(tool_pack, list):
            if len(tool_pack) == 0:
                raise ValueError("Tool pack cannot be empty")
            if not all(issubclass(tool, functionCallingBaseModel) for tool in tool_pack):
                raise ValueError("Tool pack must be a list of dictionaries")
            payload["tools"] = [tool.generate_function_tool("mistral") for tool in tool_pack]
        elif issubclass(tool_pack, functionCallingBaseModel):
            payload["tools"] = [tool_pack.generate_function_tool("mistral")]
        else:
            raise ValueError("Tool pack must be a list or dictionary")
        
        
    if max_tokens:
        payload["max_tokens"] = max_tokens

    if streaming:
        payload["stream"] = True

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}"
    }
    
    response = requests.post(url, json=payload, headers=headers, stream=streaming)

    if streaming:
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
                            delta = chunk['choices'][0]['delta']
                            # Skip the initial message that only contains role
                            if len(delta) == 1 and 'role' in delta:
                                continue
                            if 'content' in delta:
                                yield delta['content']
                        except json.JSONDecodeError:
                            print(f"Error decoding JSON: {line}")
        return generate()

    response_json = response.json()
    
    # Extract the content from the response
    if structured_output:
        try:
            return json.loads(response_json['choices'][0]['message']['content'])
        except (KeyError, json.JSONDecodeError):
            print("Warning: Failed to parse structured output as JSON")
            return response_json['choices'][0]['message']['content']
    if tool_pack:
        try:    
            print("Successfully parsed tool calls as JSON")
            return response_json['choices'][0]['message']['tool_calls']
        except:
            print("Warning: Failed to parse tool calls as JSON")
            return response_json['choices'][0]['message']['content']
    else:
        return response_json['choices'][0]['message']['content']
