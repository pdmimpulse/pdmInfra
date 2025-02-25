"""
This module handles inference requests to OpenAI's API.
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
from pdmInfra.ai.param import *

def openai_inference(
    system_message: str,
    model: str,
    api_key: str,
    user_message=None,
    chat_history=None,
    temperature: float = 0,
    streaming: bool = False,
    tool_pack=None,
    structured_output=None,
    seed: int = None,
    cost_tracker: bool = False,
    reasoning_effort: str = None
):
    """Handle inference requests specifically for OpenAI models."""
    url = "https://api.openai.com/v1/chat/completions"
    
    # Add validation for streaming incompatibility
    if streaming and (structured_output or tool_pack):
        raise ValueError("Streaming is not compatible with structured output or function calling in OpenAI models")

    # Prepare the payload
    payload = {
        "model": model,
        "messages": None,
        "stream": streaming
    }

    # Combine messages
    if model not in openaiReasoningLLMList:  # Normal models
        messages = [
            {"role": "system", "content": system_message}
        ]
        payload["temperature"] = temperature
    else:  # Reasoning models
        messages = [
            {"role": "developer", "content": system_message},
        ]
        if reasoning_effort:
            if reasoning_effort not in ["low", "medium", "high"]:
                raise ValueError("Reasoning effort must be one of: low, medium, high")
            else:   
                payload["reasoning_effort"] = reasoning_effort

    # Add chat history
    if chat_history:
        if isinstance(chat_history, openai_message_history):
            chat_history = chat_history.chat_history
        messages.extend(chat_history)
    
    # Add user message
    if user_message:
        messages.append({"role": "user", "content": user_message})
        
    payload["messages"] = messages

    if seed:
        payload["seed"] = seed

    if structured_output:
        if not issubclass(structured_output, structuredOutputBaseModel):
            raise ValueError("Structured output must be a structuredOutputBaseModel")
        payload["response_format"] = structured_output.generate_structured_output("openai")

    if tool_pack:
        if isinstance(tool_pack, list):
            if len(tool_pack) == 0:
                raise ValueError("Tool pack cannot be empty")
            if not all(issubclass(tool, functionCallingBaseModel) for tool in tool_pack):
                raise ValueError("Tool pack must be a list of dictionaries")
            payload["tools"] = [tool.generate_function_tool("openai") for tool in tool_pack]
        elif issubclass(tool_pack, functionCallingBaseModel):
            payload["tools"] = [tool_pack.generate_function_tool("openai")]
        else:
            raise ValueError("Tool pack must be a list or dictionary")

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
                    if line != '[DONE]':
                        try:
                            chunk = json.loads(line)
                            delta = chunk['choices'][0]['delta']
                            if 'content' in delta:
                                yield delta['content']
                        except json.JSONDecodeError:
                            print(f"Error decoding JSON: {line}")
        return generate()

    if tool_pack:
        try: 
            response.json()['choices'][0]['message']['tool_calls']
            output = openai_function_call_extraction(response.json())
        except:
            output = openai_chat_content_extraction(response.json())
    elif structured_output:
        output = openai_structured_output_extraction(response.json())
    else: 
        output = openai_chat_content_extraction(response.json())
    
    if cost_tracker:
        usage = response.json()['usage']
        output = (output, usage)

    return output 