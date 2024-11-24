"""
This modules sends a request to LLM APIs across different providers. This aims to provide a unified interface for different LLM APIs.
The best practice is to create a InferenceClass object for individual use cases and name the object as per the use case.

Currently only supports OpenAI, which offers the most capability from their models. 
We aim to emulate these capabilities in other models through prompt engineering and other techniques here.
"""
import requests
import json


from pdmInfra.ai.param import validLLMList, openaiLLMList, openaiURL
from pdmInfra.ai.LLM_inference.openai_tools import openai_function_call_extraction, openai_structured_output_extraction, openai_chat_content_extraction, openai_token_usage_tracker, openai_message_history
from pdmInfra.ai.json_schema import structuredOutputBaseModel, functionCallingBaseModel

class InferenceClass:
    """
    This class is used to create a llm module. It allows you to set the parameters and reuse the same setting by recalling the object. 

    Args:
    system_message (str): The system message to start the conversation.
    user_message (str): The user message to continue the conversation.
    model (str): The model to use for the completion.
    chat_history (list): The chat history to include in the completion.
    temperature (float): The temperature to use for the completion. Default is 0.
    streaming (bool): Whether to stream the completion. Default is False.
    tool_pack (list): The tool pack to use for the completion.
    structured_output (dict): The structured output to use for the completion.
    cost_tracker (bool): Whether to track the cost of the completion. Default is False.
    seed (int): The seed to use for the completion.

    Returns:
    dict: The completion response from the OpenAI API.
    """
    system_message : str
    user_message : str = None
    model : str
    chat_history = None
    temperature : float = 0.0
    streaming : bool = False
    tool_pack = None
    structured_output = None
    seed : int = None
    cost_tracker : bool = False
    api_key: str

    def infer(self, api_key: str = None, user_message: str = None, chat_history = None, temperature: float = None, streaming: bool = None, tool_pack = None, structured_output = None, seed: int = None, cost_tracker: bool = None):
        if api_key:
            self.api_key = api_key
        if user_message:
            self.user_message = user_message
        if chat_history:
            if isinstance(chat_history, openai_message_history):
                chat_history = chat_history.chat_history
            self.chat_history = chat_history
        if temperature:
            self.temperature = temperature
        if streaming:
            self.streaming = streaming
        if tool_pack:
            self.tool_pack = tool_pack
        if structured_output:
            self.structured_output = structured_output
        if seed:
            self.seed = seed
        if cost_tracker:
            self.cost_tracker = cost_tracker

        if not self.system_message:
            raise ValueError("System message is required")
        if not self.api_key:
            raise ValueError("API Key is required")
        if not self.user_message and not self.chat_history:
            raise ValueError("User message or Chat History is required")
        if not self.model:
            raise ValueError(f"LLM model name is required, available models are: {validLLMList}")
        output = inference(
            system_message = self.system_message, 
            user_message = self.user_message, 
            model = self.model, 
            api_key = self.api_key,
            chat_history = self.chat_history, 
            temperature = self.temperature, 
            streaming = self.streaming, 
            tool_pack = self.tool_pack, 
            structured_output = self.structured_output, 
            seed = self.seed, 
            cost_tracker = self.cost_tracker)
        return output

    

def retry(func):
    def wrapper(*args, **kwargs):
        for i in range(3):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(e)
                continue
    return wrapper

def inference(system_message, model: str, api_key: str, user_message = None, chat_history: list = None, temperature : float = 0, streaming: bool = False, tool_pack = None, structured_output = None, seed: int = None, cost_tracker: bool = False):
    """
    This function sends a request to the OpenAI API to generate a completion for a given model.
    
    Args:
    system_message (str): The system message to start the conversation.
    user_message (str): The user message to continue the conversation.
    model (str): The model to use for the completion.
    chat_history (list): The chat history to include in the completion.
    temperature (float): The temperature to use for the completion. Default is 0.
    streaming (bool): Whether to stream the completion. Default is False.
    tool_pack (list): The tool pack to use for the completion.
    structured_output (dict): The structured output to use for the completion.

    Returns:
    dict: The completion response from the OpenAI API.
    """
    # =-=-=-=-=-=-=-=-=-=-=- Input Validation =-=-=-=-=-=-=-=-=-=-=-=

    ## Model name check and url routing
    if model not in validLLMList:
        raise ValueError(f"Invalid model: {model}. Valid models are: {validLLMList}")
    else:
        if model in openaiLLMList:
            isopenai = True
            url = openaiURL
            key = api_key
        else: # Temporarily raise error for other models, add if statements once they are supported
            raise ValueError(f"Model {model} is not yet supported by this function")
        
    ## Input variable conflict check
    if streaming and structured_output:
        raise ValueError("Streaming and structured output cannot be enabled at the same time.")
    if tool_pack and streaming:
        raise ValueError("Function Calling and streaming cannot be enabled at the same time.")
    if structured_output and not isopenai:
        raise ValueError("Structured output is only supported for OpenAI models.")
    if structured_output and tool_pack:
        raise ValueError("Tool packs and structured output cannot be enabled at the same time.")
    


    # =-=-=-=-=-=-=-=-=-=-=- OpenAI API Request =-=-=-=-=-=-=-=-=-=-=-=         
    if isopenai:
        
        # Prepare the payload
        ## combine messages
        if model not in ['o1-mini', 'o1-preview']:
            messages = [
                {"role": "system", "content": system_message}
            ]
            # Add chat history
            if chat_history:
                if isinstance(chat_history, openai_message_history):
                    chat_history = chat_history.chat_history
                messages.extend(chat_history)
            # Add user message
            if user_message:
                messages.append({"role": "user", "content": user_message})
        else: 
            if structured_output:
                raise ValueError("Structured output is not supported for o1-mini and o1-preview")
            if tool_pack:
                raise ValueError("Tool packs are not supported for o1-mini and o1-preview")
            if chat_history:
                if isinstance(chat_history, openai_message_history):
                    chat_history = chat_history.chat_history
                messages = chat_history
                if user_message:
                    messages = [{"role": "user", "content": user_message}]
            else:
                if user_message:
                    messages = [{"role": "user", "content": system_message + "\n" + user_message}]

        payload = {
            "model": model,
            "temperature": temperature,
            "messages": messages,
            "stream": streaming
        }

        if seed:
            payload["seed"] = seed

        if structured_output:
            if not issubclass(structured_output, structuredOutputBaseModel):
                raise ValueError("Structured output must be a structuredOutputBaseModel")
            payload["response_format"] = structured_output.generate_structured_output()

        if tool_pack:
            if isinstance(tool_pack, list):
                if len(tool_pack) == 0:
                    raise ValueError("Tool pack cannot be empty")
                if not all(issubclass(tool, functionCallingBaseModel) for tool in tool_pack):
                    raise ValueError("Tool pack must be a list of dictionaries")
                payload["tools"] = [tool.generate_function_tool() for tool in tool_pack]
            elif issubclass(tool_pack, functionCallingBaseModel):
                payload["tools"] = [tool_pack.generate_function_tool()]
            else:
                raise ValueError("Tool pack must be a list or dictionary")

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {key}"
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
            # return response.json()
            output = openai_structured_output_extraction(response.json())
        else: 
            output = openai_chat_content_extraction(response.json())
        
        if cost_tracker:
            usage = response.json()['usage']
            output = (output, usage)

        return output
