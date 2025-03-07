"""
This modules sends a request to LLM APIs across different providers. This aims to provide a unified interface for different LLM APIs.
The best practice is to create a InferenceClass object for individual use cases and name the object as per the use case.

Currently supports OpenAI, Anthropic, and Mistral.
"""
import requests
import json

from pdmInfra.ai.param import *
from pdmInfra.ai.LLM_inference.openai_tools import openai_message_history
from pdmInfra.ai.json_schema import structuredOutputBaseModel, functionCallingBaseModel
from pdmInfra.ai.LLM_inference.providers import openai_inference, anthropic_inference, mistral_inference, huggingface_inference

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
    max_tokens (int): The maximum number of tokens to generate. Default is None.

    Returns:
    dict: The completion response from the API.
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
    reasoning_effort : str = None
    api_key: str
    max_tokens: int = None

    def infer(self, api_key: str = None, user_message: str = None, chat_history = None, temperature: float = None, streaming: bool = None, tool_pack = None, structured_output = None, seed: int = None, cost_tracker: bool = None, reasoning_effort: str = None, max_tokens: int = None):
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
        if reasoning_effort:
            self.reasoning_effort = reasoning_effort
        if max_tokens:
            self.max_tokens = max_tokens

        if not self.system_message:
            raise ValueError("System message is required")
        if not self.api_key:
            raise ValueError("API Key is required")
        if not self.user_message and not self.chat_history:
            raise ValueError("User message or Chat History is required")
        if not self.model:
            raise ValueError(f"LLM model name is required, available models are: {validLLMList}")
        if self.model in openaiReasoningLLMList:
            if not isinstance(self.reasoning_effort, str):
                raise ValueError("Reasoning effort must be a string")
            else:   
                if self.reasoning_effort not in ["low", "medium", "high"]:
                    raise ValueError("Reasoning effort must be one of: low, medium, high")
            if temperature:
                print("Warning: Temperature is not supported for OpenAI Reasoning Models. If you wish to use temperature, please configure reasoning_effort instead.")
        else:
            if self.reasoning_effort:
                print("Warning: Reasoning effort is not supported for this model. Reasoning effort is only for OpenAI Reasoning Models.")
        
        # Input variable conflict check
        if self.structured_output and self.tool_pack:
            raise ValueError("Tool packs and structured output cannot be enabled at the same time.")

        # Route to appropriate provider
        if self.model in openaiLLMList:
            if not self.api_key.startswith("sk-"):
                raise ValueError("Invalid OpenAI API key. OpenAI API keys should start with 'sk-'")
            return openai_inference(
                system_message=self.system_message,
                user_message=self.user_message,
                model=self.model,
                api_key=self.api_key,
                chat_history=self.chat_history,
                temperature=self.temperature,
                streaming=self.streaming,
                tool_pack=self.tool_pack,
                structured_output=self.structured_output,
                seed=self.seed,
                cost_tracker=self.cost_tracker,
                reasoning_effort=self.reasoning_effort
            )
        elif self.model in anthropicLLMList:
            if not self.api_key.startswith("sk-ant"):
                raise ValueError("Invalid Anthropic API key. Anthropic API keys should start with 'sk-ant'")
            return anthropic_inference(
                system_message=self.system_message,
                user_message=self.user_message,
                model=self.model,
                api_key=self.api_key,
                chat_history=self.chat_history,
                streaming=self.streaming,
                tool_pack=self.tool_pack,
                structured_output=self.structured_output
            )
        elif self.model in mistralLLMList:
            return mistral_inference(
                system_message=self.system_message,
                user_message=self.user_message,
                model=self.model,
                api_key=self.api_key,
                chat_history=self.chat_history,
                temperature=self.temperature,
                streaming=self.streaming,
                structured_output=self.structured_output,
                tool_pack=self.tool_pack,
                max_tokens=self.max_tokens
            )
        elif self.model in huggingfaceLLMList:
            return huggingface_inference(
                system_message=self.system_message,
                user_message=self.user_message,
                model=self.model,
                api_key=self.api_key,
                chat_history=self.chat_history,
                temperature=self.temperature,
                streaming=self.streaming,
                tool_pack=self.tool_pack,
                structured_output=self.structured_output,
                seed=self.seed,
                cost_tracker=self.cost_tracker,
                max_tokens=self.max_tokens
            )
        else:
            raise ValueError(f"Model {self.model} is not yet supported")