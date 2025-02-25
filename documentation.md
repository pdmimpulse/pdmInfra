# PDM Infrastructure - AI Module Documentation

## Overview
The PDM Infrastructure AI Module provides a unified interface for interacting with multiple Large Language Model (LLM) providers through a single, consistent API. The module abstracts away provider-specific implementations while maintaining full access to each provider's unique capabilities.

## Table of Contents
1. [Key Features](#key-features)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Core Components](#core-components)
5. [Advanced Usage](#advanced-usage)
6. [Provider-Specific Features](#provider-specific-features)
7. [Best Practices](#best-practices)
8. [Error Handling](#error-handling)
9. [Limitations](#limitations)
10. [Future Enhancements](#future-enhancements)

## Key Features

### 1. Multi-Provider Support
Currently supports:
- OpenAI (including specialized reasoning models)
- Anthropic Claude
- Mistral AI

### 2. Unified Interface
All providers are accessed through the same `InferenceClass`, which handles:
- Provider-specific API routing
- Message history management
- Structured output formatting
- Function/tool calling
- Streaming responses

### 3. Schema Management
- Structured output definitions
- Function/tool calling schemas
- Cross-provider compatibility

## Installation

```bash
pip install pdm-infra
```

## Quick Start

### Basic Usage
```python
from pdmInfra.ai import InferenceClass

# Initialize the LLM interface
llm = InferenceClass()
llm.system_message = "You are a helpful assistant."
llm.model = "gpt-4o"

# Get a response
response = llm.infer(
    api_key="your-api-key",
    user_message="What's the weather like today?"
)
print(response)
```

### Switching Providers
```python
# Use Anthropic
llm.model = "claude-3-7-sonnet-20250219"
response = llm.infer(
    api_key="your-anthropic-key",
    user_message="Explain quantum computing"
)

# Use Mistral
llm.model = "mistral-large-latest"
response = llm.infer(
    api_key="your-mistral-key",
    user_message="Summarize this article"
)
```

## Core Components

### 1. InferenceClass
The primary interface for all LLM interactions.

#### Key Parameters
- `system_message` (str): Initial system prompt
- `model` (str): Model identifier
- `temperature` (float): Response randomness (0-1)
- `streaming` (bool): Enable streaming responses
- `tool_pack` (list/dict): Function calling tools
- `structured_output` (dict): Output schema
- `cost_tracker` (bool): Track token usage
- `seed` (int): Reproducibility seed
- `max_tokens` (int): Response length limit

#### Supported Models

##### OpenAI Models
Standard Models:
- `gpt-4o-2024-08-06`
- `gpt-4o-mini-2024-07-18`
- `gpt-4o`
- `gpt-4o-mini`

Reasoning Models:
- `o1-2024-12-17`
- `o3-mini`

##### Anthropic Models
- `claude-3-7-sonnet-20250219`
- `claude-3-5-sonnet-20241022`
- `claude-3-5-haiku-20241022`

##### Mistral Models
- `mistral-large-latest`
- `mistral-small`

### 2. Message History Management
```python
from pdmInfra.ai.LLM_inference.openai_tools import openai_message_history

# Initialize chat history
history = openai_message_history()

# Add messages
history.add_user_message("What's the weather like?")
history.add_assistant_message("Let me check that for you.")

# Use in inference
llm.infer(
    api_key="your-api-key",
    chat_history=history
)
```

### 3. Schema Management

#### Structured Output
```python
from pdmInfra.ai.json_schema import structuredOutputBaseModel, Field

class WeatherResponse(structuredOutputBaseModel):
    """Weather information schema"""
    temperature = Field(
        description="Current temperature in Celsius",
        field_type="number"
    )
    conditions = Field(
        description="Weather conditions",
        enum=["sunny", "rainy", "cloudy", "snowy"]
    )
    forecast = Field(
        description="24-hour forecast",
        field_type="array",
        array_type="string"
    )

# Use the schema
llm.structured_output = WeatherResponse
response = llm.infer(
    api_key="your-api-key",
    user_message="What's the weather like in New York?"
)
```

#### Function/Tool Calling
```python
from pdmInfra.ai.json_schema import functionCallingBaseModel, Field

class DatabaseQuery(functionCallingBaseModel):
    """Database query function"""
    query = Field(
        description="SQL query string",
        field_type="string"
    )
    database = Field(
        description="Target database",
        enum=["users", "products", "orders"]
    )
    limit = Field(
        description="Maximum number of results",
        field_type="integer",
        optional=True
    )

# Use the function
llm.tool_pack = DatabaseQuery
response = llm.infer(
    api_key="your-api-key",
    user_message="Show me the top 5 users by order value"
)
```

## Advanced Usage

### 1. Streaming Responses
```python
llm.streaming = True
response = llm.infer(
    api_key="your-api-key",
    user_message="Write a long story"
)

for chunk in response:
    print(chunk, end="", flush=True)
```

### 2. Complex Schemas
```python
class Address(structuredOutputBaseModel):
    """Address information"""
    street = Field(description="Street address")
    city = Field(description="City name")
    country = Field(description="Country name")
    postal_code = Field(description="Postal code", optional=True)

class UserProfile(structuredOutputBaseModel):
    """User profile information"""
    name = Field(description="User's full name")
    age = Field(description="User's age", field_type="integer")
    email = Field(description="Email address")
    addresses = Field(
        description="User's addresses",
        field_type="array",
        children=Address
    )

# Use nested schema
llm.structured_output = UserProfile
response = llm.infer(
    api_key="your-api-key",
    user_message="Get user profile for ID: 12345"
)
```

### 3. Multiple Function Calls
```python
class WeatherAPI(functionCallingBaseModel):
    """Get weather data"""
    location = Field(description="City name")
    units = Field(enum=["celsius", "fahrenheit"])

class NewsAPI(functionCallingBaseModel):
    """Get news headlines"""
    topic = Field(description="News topic")
    count = Field(field_type="integer", optional=True)

# Use multiple functions
llm.tool_pack = [WeatherAPI, NewsAPI]
response = llm.infer(
    api_key="your-api-key",
    user_message="What's the weather and news in London?"
)
```

## Provider-Specific Features

### OpenAI

#### Reasoning Models
```python
llm.model = "o1-2024-12-17"
llm.reasoning_effort = "high"  # Options: low, medium, high
response = llm.infer(
    api_key="your-api-key",
    user_message="Solve this complex math problem"
)
```

#### Cost Tracking
```python
llm.cost_tracker = True
response, usage = llm.infer(
    api_key="your-api-key",
    user_message="Generate a report"
)
print(f"Tokens used: {usage}")
```

### Anthropic

#### High Token Limit
```python
llm.model = "claude-3-7-sonnet-20250219"
response = llm.infer(
    api_key="your-anthropic-key",
    user_message="Write a detailed analysis"
)
```

### Mistral

#### Temperature Control
```python
llm.model = "mistral-large-latest"
llm.temperature = 0.7
response = llm.infer(
    api_key="your-mistral-key",
    user_message="Generate creative ideas"
)
```

## Best Practices

### 1. Model Selection
Choose models based on task requirements:
- General tasks: `gpt-4o` or `claude-3-5-sonnet`
- Complex reasoning: `o1-2024-12-17` with high reasoning effort
- Efficient responses: `claude-3-5-haiku` or `mistral-small`

### 2. Schema Design
- Use clear, descriptive field names
- Provide detailed field descriptions
- Make fields optional when appropriate
- Use enums to restrict possible values
- Structure nested data logically

### 3. Error Handling
```python
try:
    response = llm.infer(
        api_key="your-api-key",
        user_message="Hello"
    )
except ValueError as e:
    print(f"Invalid input: {e}")
except RuntimeError as e:
    print(f"API error: {e}")
```

### 4. Resource Management
- Use streaming for long responses
- Enable cost tracking for production
- Set appropriate max_tokens
- Implement rate limiting

## Error Handling

### Common Errors

1. Authentication Errors
```python
# Invalid API key format
try:
    llm.model = "gpt-4o"
    response = llm.infer(
        api_key="invalid-key",
        user_message="Hello"
    )
except ValueError as e:
    print("Invalid API key format")
```

2. Model Compatibility
```python
# Streaming with structured output
try:
    llm.streaming = True
    llm.structured_output = WeatherResponse
    response = llm.infer(
        api_key="your-api-key",
        user_message="Get weather"
    )
except ValueError as e:
    print("Streaming not compatible with structured output")
```

3. Schema Validation
```python
# Invalid schema definition
try:
    class InvalidSchema(structuredOutputBaseModel):
        field = Field(field_type="invalid")
except ValueError as e:
    print("Invalid field type")
```

## Limitations

1. **Provider-Specific Features**
   - Some features are only available with specific providers
   - Streaming limitations vary by provider
   - Response formats may differ slightly between providers

2. **Authentication**
   - Each provider requires its own API key
   - Different key format validation per provider:
     - OpenAI: Must start with `sk-`
     - Anthropic: Must start with `sk-ant`
     - Mistral: No specific format requirement

3. **Streaming Limitations**
   - Not compatible with structured output
   - Not compatible with function calling
   - Provider-specific implementation differences

## Future Enhancements

1. **Additional Providers**
   - Google (Gemini)
   - Perplexity
   - Meta
   - DeepSeek
   - Hugging Face

2. **Enhanced Features**
   - Cross-provider cost optimization
   - Automatic provider fallback
   - Enhanced streaming support
   - Improved error handling

3. **Performance Improvements**
   - Response caching
   - Parallel inference
   - Rate limiting and quota management
   - Batch processing capabilities