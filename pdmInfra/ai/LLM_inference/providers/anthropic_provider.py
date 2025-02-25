"""
This module handles inference requests to Anthropic's API.
"""
import requests
import json
from pdmInfra.ai.json_schema import structuredOutputBaseModel, functionCallingBaseModel
from pdmInfra.ai.LLM_inference.openai_tools import openai_message_history

def anthropic_inference(
    system_message: str,
    model: str,
    api_key: str,
    user_message=None,
    chat_history=None,
    streaming: bool = False,
    tool_pack=None,
    structured_output=None
):
    """Handle inference requests specifically for Anthropic models."""
    url = "https://api.anthropic.com/v1/messages"
    
    payload = {
        "model": model,
        "messages": None,
        "max_tokens": 64000,
        "stream": streaming
    }
    
    if system_message:
        payload["system"] = system_message
        
    if chat_history:
        if isinstance(chat_history, openai_message_history):
            chat_history = chat_history.chat_history
        payload["messages"] = chat_history
        if user_message:
            payload["messages"].append({"role": "user", "content": user_message})
    else: 
        if user_message:
            payload["messages"] = [
                {"role": "user", "content": user_message}
            ]
            
    if tool_pack:
        if isinstance(tool_pack, list):
            if len(tool_pack) == 0:
                raise ValueError("Tool pack cannot be empty")
            if not all(issubclass(tool, functionCallingBaseModel) for tool in tool_pack):
                raise ValueError("Tool pack must be a list of dictionaries")
            payload["tools"] = [tool.generate_function_tool("anthropic") for tool in tool_pack]
        elif issubclass(tool_pack, functionCallingBaseModel):
            payload["tools"] = [tool_pack.generate_function_tool("anthropic")]
        else:
            raise ValueError("Tool pack must be a list or dictionary")
        
    if structured_output:
        if not issubclass(structured_output, structuredOutputBaseModel):
            raise ValueError("Structured output must be a structuredOutputBaseModel")
        payload["tools"] = [structured_output.generate_structured_output("anthropic")]
        payload["tool_choice"] = {"name": structured_output.__name__, "type": "tool"}
        
    
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers, stream=streaming)
    
    if streaming:
        def generate():
            for line in response.iter_lines():
                # print(line)
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        line = line[6:]  # Remove 'data: ' prefix
                        try:
                            chunk = json.loads(line)
                            if chunk["type"] == "content_block_delta":
                                if "text" in chunk["delta"]:
                                    yield chunk["delta"]["text"]
                                elif "input_json_delta" in chunk["delta"]["type"]:
                                    yield chunk["delta"]["partial_json"]
                            elif chunk["type"] == "message_delta":
                                if "content" in chunk["delta"] and chunk["delta"]["content"]:
                                    for block in chunk["delta"]["content"]:
                                        if block["type"] == "text":
                                            yield block["text"]
                                        elif block["type"] == "tool_use":
                                            yield json.dumps(block["input"])
                        except json.JSONDecodeError:
                            print(f"Error decoding JSON: {line}")
        return generate()
        
        
        
    return response.json() 