# PDM Infrastructure - AI Module Documentation

## Overview
The AI module provides a unified interface for interacting with Large Language Models (LLMs), with a focus on structured outputs and function calling capabilities.

## Core Components

### 1. InferenceClass
The primary interface for LLM interactions.

#### Basic Usage
```python
from pdmInfra.ai import InferenceClass

llm = InferenceClass()
llm.system_message = "You are a helpful assistant."
llm.model = "gpt-4o"

response = llm.infer(
    api_key="your-api-key",
    user_message="Hello, world!"
)
```

#### Key Parameters
Reference to full parameter list:

```17:34:pdmInfra/ai/LLM_inference/__init__.py
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
```


### 2. Message History Management
The `openai_message_history` class manages conversation history with strict ordering rules.

#### Features:
- Maintains message order integrity
- Supports user messages, assistant responses, function calls, and tool responses
- Validates message sequence

Example:
```python
from pdmInfra.ai.LLM_inference.openai_tools import openai_message_history

history = openai_message_history()
history.add_user_message("What's the weather?")
history.add_assistant_message("Let me check that for you.")
```

### 3. Schema Management

#### Field Class
Base class for defining schema fields:

```5:27:pdmInfra/ai/json_schema.py
class Field:
    """
    This class represents a field in a JSON schema.

    Attributes:
        description (str): The description of the field.
        field_type (str): The type of the field. By default it is "string". Other possible types: ['string', 'number', 'integer', 'boolean', 'array', 'object'].
        optional (bool): Whether the field is an optional field. By default it is False.
        enum (list): The list of possible values for the field. By default it is None.
        children ($customBaseModel): The children schema for the field. By default it is None.
    """

    def __init__(self, description = None, field_type="string", optional=False, enum=None, children=None, array_type = None):
        self.description = description
        self.field_type = field_type
        self.optional = optional
        self.enum = enum
        self.children = children
        self.array_type = array_type
        if field_type == "array" and not children and not array_type:
            raise TypeError("Array type must have either children or array_type")
        if field_type == "array" and children and array_type:
            raise TypeError("Cannot have both children and array_type")
```


#### Available Field Types
- string (default)
- number
- integer
- boolean
- array
- object

#### structuredOutputBaseModel
Base class for creating structured output schemas.

Example:
```python
from pdmInfra.ai.json_schema import structuredOutputBaseModel, Field

class WeatherResponse(structuredOutputBaseModel):
    """Schema for weather information"""
    temperature = Field(
        description="Current temperature",
        field_type="number"
    )
    conditions = Field(
        description="Weather conditions",
        enum=["sunny", "rainy", "cloudy"]
    )
    hourly_forecast = Field(
        description="Hourly temperature forecast",
        field_type="array",
        array_type="number"
    )
```

#### functionCallingBaseModel
Base class for defining function calling tools.

Example:
```python
from pdmInfra.ai.json_schema import functionCallingBaseModel, Field

class SearchDatabase(functionCallingBaseModel):
    """Search the database for specific records"""
    query = Field(
        description="Search query string",
        field_type="string"
    )
    limit = Field(
        description="Maximum number of results",
        field_type="integer",
        optional=True
    )
```

## Advanced Features

### 1. Response Extraction
Specialized extractors for different response types:
- `openai_chat_content_extraction`: Basic chat responses
- `openai_function_call_extraction`: Function calling responses
- `openai_structured_output_extraction`: JSON schema responses
- `openai_token_usage_tracker`: Usage tracking

### 2. Error Handling
Built-in retry mechanism for API calls:

```93:101:pdmInfra/ai/LLM_inference/__init__.py
def retry(func):
    def wrapper(*args, **kwargs):
        for i in range(3):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(e)
                continue
    return wrapper
```


### 3. Streaming Support
Streaming capabilities for real-time responses:

```198:213:pdmInfra/ai/LLM_inference/__init__.py
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
```


## Configuration

### Supported Models
Current model support:

```7:10:pdmInfra/ai/param.py
validLLMList = ['gpt-4o-2024-08-06', 'gpt-4o-mini-2024-07-18', 'gpt-4o', 'gpt-4o-mini']
openaiLLMList = ['gpt-4o-2024-08-06', 'gpt-4o-mini-2024-07-18', 'gpt-4o', 'gpt-4o-mini']
pplxLLMList = []
mistralLLMList = []
```


### API Endpoints

```12:12:pdmInfra/ai/param.py
openaiURL = "https://api.openai.com/v1/chat/completions"
```


## Best Practices

1. **Message History Management**
   - Always maintain proper message order
   - Use the `openai_message_history` class for complex conversations
   - Validate function calls and tool responses

2. **Schema Definition**
   - Use descriptive field names and descriptions
   - Leverage optional fields when appropriate
   - Use enums to restrict possible values
   - Implement proper validation for array types

3. **Error Handling**
   - Always handle API errors gracefully
   - Use the built-in retry mechanism for transient failures
   - Implement proper logging for production environments

4. **Performance Optimization**
   - Use streaming for long responses
   - Implement proper timeout handling
   - Monitor token usage with cost tracking

## Limitations

1. **Model Support**
   - Currently only supports OpenAI models
   - Future support planned for:
     - Anthropic Claude
     - Mistral AI
     - Local models

2. **Streaming Limitations**
   - Cannot be used with structured output
   - Cannot be used with function calling
   - Limited error handling in streaming mode

## Future Enhancements

1. **Additional Model Support**
   - Integration with more LLM providers
   - Support for local model deployment
   - Custom model fine-tuning support

2. **Enhanced Features**
   - Improved error handling
   - Advanced retry strategies
   - Better streaming support
   - Enhanced schema validation

3. **Performance Improvements**
   - Caching mechanisms
   - Batch processing
   - Parallel inference
   - Response optimization