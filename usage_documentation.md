# PDM Infrastructure - Usage Documentation

## Table of Contents
1. [Installation](#installation)
2. [AI Module](#ai-module)
   - [Basic Chat](#basic-chat)
   - [Structured Output](#structured-output)
   - [Function Calling](#function-calling)
   - [Chat History](#chat-history)
   - [Streaming](#streaming)
   - [Cost Tracking](#cost-tracking)
3. [AWS Module](#aws-module)

## Installation

```bash
pip install pdmInfra
```

## AI Module

### Basic Chat

The simplest way to use the AI module is through basic chat:

```python
from pdmInfra.ai import InferenceClass

# Initialize the inference class
llm = InferenceClass()
llm.system_message = "You are a helpful assistant."
llm.model = "gpt-4o"

# Make a simple inference
response = llm.infer(
    api_key="your-api-key",
    user_message="What is the capital of France?"
)
print(response)  # Paris
```

### Structured Output

For structured responses, define a schema using `structuredOutputBaseModel`:

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

# Use the schema
llm = InferenceClass()
llm.system_message = "You are a helpful information extractor."
llm.model = "gpt-4o"

response = llm.infer(
    api_key="your-api-key",
    user_message="John Doe is 30 years old and enjoys reading and hiking.",
    structured_output=PersonInfo
)

print(response)
# {
#     "name": "John Doe",
#     "age": 30,
#     "hobbies": ["reading", "hiking"]
# }
```

### Function Calling

Define functions using `functionCallingBaseModel`:

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

# Use function calling
llm = InferenceClass()
llm.system_message = "You are a weather assistant."
llm.model = "gpt-4o"

response = llm.infer(
    api_key="your-api-key",
    user_message="What's the weather in Paris?",
    tool_pack=WeatherLookup
)
```

### Chat History

Manage conversation history using `openai_message_history`:

```python
from pdmInfra.ai.LLM_inference.openai_tools import openai_message_history

# Initialize history
history = openai_message_history()

# Add messages
history.add_user_message("What's the weather in Paris?")
history.add_assistant_message("It's currently sunny and 22°C in Paris.")
history.add_user_message("And what about London?")

# Use history in inference
llm = InferenceClass()
llm.system_message = "You are a weather assistant."
llm.model = "gpt-4o"

response = llm.infer(
    api_key="your-api-key",
    chat_history=history
)
```

### Streaming

Enable streaming for real-time responses:

```python
llm = InferenceClass()
llm.system_message = "You are a helpful assistant."
llm.model = "gpt-4o"
llm.streaming = True

# Stream the response
for chunk in llm.infer(
    api_key="your-api-key",
    user_message="Tell me a long story about a dragon."
):
    print(chunk, end='', flush=True)
```

Note: Streaming cannot be used with structured output or function calling.

### Cost Tracking

Track token usage:

```python
llm = InferenceClass()
llm.system_message = "You are a helpful assistant."
llm.model = "gpt-4o"
llm.cost_tracker = True

response, usage = llm.infer(
    api_key="your-api-key",
    user_message="What is quantum computing?"
)

print(f"Response: {response}")
print(f"Token usage: {usage}")
```

## AWS Module

### S3 Operations

Basic S3 operations:

```python
from pdmInfra.aws.s3 import (
    create_bucket,
    s3_put_object,
    s3_get_object,
    s3_list_objects,
    s3_delete_object
)

# Create a bucket
create_bucket("my-test-bucket")

# Upload data
data = {"key": "value"}
s3_put_object("my-test-bucket", "data.json", data)

# Read data
content = s3_get_object("my-test-bucket", "data.json")

# List objects
objects = s3_list_objects("my-test-bucket")

# Delete object
s3_delete_object("my-test-bucket", "data.json")
```

## Error Handling

The library includes a retry mechanism for API calls:


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


Common errors to handle:
- API key validation
- Model availability
- Rate limiting
- Network issues
- Malformed responses

## Configuration

Available models:


```7:10:pdmInfra/ai/param.py
validLLMList = ['gpt-4o-2024-08-06', 'gpt-4o-mini-2024-07-18', 'gpt-4o', 'gpt-4o-mini']
openaiLLMList = ['gpt-4o-2024-08-06', 'gpt-4o-mini-2024-07-18', 'gpt-4o', 'gpt-4o-mini']
pplxLLMList = []
mistralLLMList = []
```


The library is designed to be extensible for future model additions.

For more detailed information about the implementation details, please refer to the design documentation.