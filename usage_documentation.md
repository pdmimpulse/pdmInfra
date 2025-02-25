# PDM Infrastructure - Usage Documentation

## Table of Contents
1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
   - [Provider Selection](#provider-selection)
   - [Basic Chat](#basic-chat)
   - [Structured Output](#structured-output)
   - [Function Calling](#function-calling)
   - [Chat History](#chat-history)
   - [Streaming](#streaming)
   - [Provider-Specific Features](#provider-specific-features)

## Installation

```bash
pip install git+https://github.com/pdmimpulse/pdmInfra.git@0.2.0
```

## Basic Usage

### Provider Selection

The library supports multiple LLM providers through a unified interface:

```python
from pdmInfra.ai import InferenceClass

# Initialize the inference class
llm = InferenceClass()
llm.system_message = "You are a helpful assistant."

# Use OpenAI
llm.model = "gpt-4o"
response = llm.infer(
    api_key="your-openai-key",
    user_message="What is the capital of France?"
)

# Switch to Anthropic
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

### Basic Chat

Simple chat interactions work consistently across providers:

```python
llm = InferenceClass()
llm.system_message = "You are a helpful assistant."

# With OpenAI
llm.model = "gpt-4o"
response = llm.infer(
    api_key="your-openai-key",
    user_message="What is the capital of France?"
)
print(response)  # Paris

# With Anthropic
llm.model = "claude-3-5-sonnet-20241022"
response = llm.infer(
    api_key="your-anthropic-key",
    user_message="What is the capital of France?"
)
print(response)  # Paris
```

### Structured Output

Define schemas that work across all providers:

```python
from pdmInfra.ai.json_schema import structuredOutputBaseModel, Field

class PersonInfo(structuredOutputBaseModel):
    """Schema for extracting person information"""
    name = Field(description="Person's full name")
    age = Field(description="Person's age", field_type="integer")
    hobbies = Field(
        description="Person's hobbies",
        field_type="array",
        array_type="string"
    )

# Use with any provider
llm = InferenceClass()
llm.system_message = "You are a helpful information extractor."

# With OpenAI
llm.model = "gpt-4o"
response = llm.infer(
    api_key="your-openai-key",
    user_message="John Doe is 30 years old and enjoys reading and hiking.",
    structured_output=PersonInfo
)

# With Anthropic
llm.model = "claude-3-7-sonnet-20250219"
response = llm.infer(
    api_key="your-anthropic-key",
    user_message="Jane Smith is 25 years old and enjoys painting and music.",
    structured_output=PersonInfo
)

# Response format is consistent across providers:
# {
#     "name": "John Doe",
#     "age": 30,
#     "hobbies": ["reading", "hiking"]
# }
```

### Function Calling

Define functions that work across providers:

```python
from pdmInfra.ai.json_schema import functionCallingBaseModel, Field

class WeatherLookup(functionCallingBaseModel):
    """Look up weather information for a location"""
    location = Field(description="City name")
    unit = Field(
        description="Temperature unit",
        enum=["celsius", "fahrenheit"],
        optional=True
    )

class NewsLookup(functionCallingBaseModel):
    """Look up news headlines"""
    topic = Field(description="News topic")
    count = Field(
        description="Number of headlines",
        field_type="integer",
        optional=True
    )

# Use single or multiple functions
llm = InferenceClass()
llm.system_message = "You are a helpful assistant."

# Single function with OpenAI
llm.model = "gpt-4o"
llm.tool_pack = WeatherLookup
response = llm.infer(
    api_key="your-openai-key",
    user_message="What's the weather in Paris?"
)

# Multiple functions with Anthropic
llm.model = "claude-3-7-sonnet-20250219"
llm.tool_pack = [WeatherLookup, NewsLookup]
response = llm.infer(
    api_key="your-anthropic-key",
    user_message="What's the weather and news in London?"
)
```

### Chat History

Manage conversation history consistently across providers:

```python
from pdmInfra.ai.LLM_inference.openai_tools import openai_message_history

# Initialize history
history = openai_message_history()

# Add messages
history.add_user_message("What's the weather in Paris?")
history.add_assistant_message("It's currently sunny and 22°C in Paris.")
history.add_user_message("And what about London?")

# Use history with any provider
llm = InferenceClass()
llm.system_message = "You are a weather assistant."

# With OpenAI
llm.model = "gpt-4o"
response = llm.infer(
    api_key="your-openai-key",
    chat_history=history
)

# With Mistral
llm.model = "mistral-large-latest"
response = llm.infer(
    api_key="your-mistral-key",
    chat_history=history
)
```

### Streaming

Enable streaming for real-time responses (provider-dependent):

```python
llm = InferenceClass()
llm.system_message = "You are a helpful assistant."
llm.streaming = True

# With OpenAI
llm.model = "gpt-4o"
for chunk in llm.infer(
    api_key="your-openai-key",
    user_message="Tell me a long story about a dragon."
):
    print(chunk, end='', flush=True)

# With Anthropic
llm.model = "claude-3-7-sonnet-20250219"
for chunk in llm.infer(
    api_key="your-anthropic-key",
    user_message="Tell me a long story about a dragon."
):
    print(chunk, end='', flush=True)
```

Note: Streaming cannot be used with structured output or function calling.

### Provider-Specific Features

#### OpenAI

1. Reasoning Models with Effort Control:
```python
llm = InferenceClass()
llm.model = "o1-2024-12-17"
llm.reasoning_effort = "high"  # Options: low, medium, high
response = llm.infer(
    api_key="your-openai-key",
    user_message="Solve this complex math problem"
)
```

2. Cost Tracking:
```python
llm = InferenceClass()
llm.model = "gpt-4o"
llm.cost_tracker = True

response, usage = llm.infer(
    api_key="your-openai-key",
    user_message="What is quantum computing?"
)

print(f"Response: {response}")
print(f"Token usage: {usage}")
```

#### Anthropic

High Token Limit:
```python
llm = InferenceClass()
llm.model = "claude-3-7-sonnet-20250219"
response = llm.infer(
    api_key="your-anthropic-key",
    user_message="Write a detailed analysis of War and Peace"
)
```

#### Mistral

Temperature Control:
```python
llm = InferenceClass()
llm.model = "mistral-large-latest"
llm.temperature = 0.7
response = llm.infer(
    api_key="your-mistral-key",
    user_message="Generate creative story ideas"
)
```

## Error Handling

Handle common errors gracefully:

```python
from pdmInfra.ai import InferenceClass

llm = InferenceClass()
llm.system_message = "You are a helpful assistant."

try:
    # Invalid API key
    llm.model = "gpt-4o"
    response = llm.infer(
        api_key="invalid-key",
        user_message="Hello"
    )
except ValueError as e:
    print(f"Authentication error: {e}")

try:
    # Incompatible feature
    llm.streaming = True
    llm.structured_output = PersonInfo
    response = llm.infer(
        api_key="your-api-key",
        user_message="Extract info"
    )
except ValueError as e:
    print(f"Compatibility error: {e}")
```

For more detailed information about the implementation and architecture, please refer to the [Design Documentation](design_documentation.md).