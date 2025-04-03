# PDM Infrastructure Library

A Python infrastructure library for AI application development, providing a light-weight unified interface for interacting with multiple Large Language Model (LLM) providers through a consistent API. Incrementally built-up based on needs of pdm AI applications. 

## Installation

Install via pip:

```bash
pip install git+https://github.com/pdmimpulse/pdmInfra.git@main
```

## Features

### AI Module

#### Multi-Provider LLM Support
- Unified interface for multiple LLM providers:
  - OpenAI (standard and reasoning models)
  - Anthropic Claude
  - Mistral AI
  - Groq
  - HuggingFace
- Provider-agnostic features:
  - Chat completions
  - Function/tool calling
  - Structured output generation
  - Streaming responses
  - Cost tracking
  - Chat history management

#### Provider-Specific Features

##### OpenAI
- Standard and reasoning models
- Reasoning effort control
- Cost tracking
- Seed support

##### Anthropic
- High token limits (64,000 tokens)
- System message handling
- Specialized message formatting

##### Mistral
- Temperature control
- Max tokens limit
- Structured output support

##### Groq
- High-performance inference
- OpenAI-compatible API
- Support for multiple open-source models

##### HuggingFace
- Hosted models integration
- Structured output extraction from text
- Tool/function call extraction from responses

#### Schema System
- Provider-agnostic schema definitions
- Two base models:
  - `structuredOutputBaseModel`: For structured outputs
  - `functionCallingBaseModel`: For function/tool definitions
- Automatic schema translation for each provider

Example usage:

```python
from pdmInfra.ai import InferenceClass
from pdmInfra.ai.json_schema import structuredOutputBaseModel, Field

# Define a structured output schema
class UserProfile(structuredOutputBaseModel):
    """Schema for user profile information"""
    name = Field(description="User's full name")
    age = Field(description="User's age", field_type="integer")
    interests = Field(
        description="User's interests",
        field_type="array",
        array_type="string"
    )

# Create an inference instance
llm = InferenceClass()
llm.system_message = "You are a helpful assistant."

# Use with OpenAI
llm.model = "gpt-4o"
response = llm.infer(
    api_key="your-openai-key",
    user_message="Extract profile: John Doe, 30, likes reading and hiking",
    structured_output=UserProfile
)

# Switch to Groq
llm.model = "llama-3.1-8b-instant-groq"
response = llm.infer(
    api_key="your-groq-key",
    user_message="Extract profile: Jane Smith, 25, enjoys painting and music",
    structured_output=UserProfile
)
```

## Supported Models

### OpenAI Models
Standard Models:
- `gpt-4o-2024-08-06`
- `gpt-4o-mini-2024-07-18`
- `gpt-4o`
- `gpt-4o-mini`

Reasoning Models:
- `o1-2024-12-17`
- `o3-mini`

### Anthropic Models
- `claude-3-7-sonnet-20250219`
- `claude-3-5-sonnet-20241022`
- `claude-3-5-haiku-20241022`

### Mistral Models
- `mistral-large-latest`
- `mistral-small`

### Groq Models
- `qwen-qwq-32b-groq`
- `qwen-2.5-coder-32b-groq`
- `qwen-2.5-32b-groq`
- `deepseek-r1-distill-qwen-32b-groq`
- `deepseek-r1-distill-llama-70b-groq`
- `llama-3.3-70b-versatile-groq`
- `llama-3.1-8b-instant-groq`


## Requirements

- Python 3.6+
- requests: For API calls
- json: For data handling

## Documentation

For detailed information, see:
- [Usage Documentation](usage_documentation.md): Comprehensive usage examples
- [Design Documentation](design_documentation.md): Technical details and architecture

## License

This project is maintained by pdm AI Innovation Team.

## Contributing

For contributions, please contact: y.lu@pdm-solutions.com

