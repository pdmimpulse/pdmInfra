
# PDM Infrastructure Library

A Python infrastructure library for AI application development, providing tools for LLM integration and AWS services.

## Installation

Install via pip:

```bash
pip install pdmInfra
```

## Features

### 1. AI Module

#### LLM Inference
- Unified interface for LLM API calls
- Currently supports OpenAI models
- Features include:
  - Chat completions
  - Function calling
  - Structured output generation
  - Streaming responses
  - Cost tracking
  - Chat history management

#### JSON Schema Generation
- Custom implementation replacing langchain's function calling pydantics
- Two base models:
  - `structuredOutputBaseModel`: For generating JSON schema outputs
  - `functionCallingBaseModel`: For generating function calling tools

Example usage:

```python
from pdmInfra.ai import InferenceClass
from pdmInfra.ai.json_schema import structuredOutputBaseModel, Field

# Define a structured output schema
class UserProfile(structuredOutputBaseModel):
    """Schema for user profile information"""
    name = Field(description="User's full name")
    age = Field(description="User's age", field_type="integer")
    interests = Field(description="User's interests", field_type="array", array_type="string")

# Create an inference instance
llm = InferenceClass()
llm.system_message = "You are a helpful assistant."
llm.model = "gpt-4o"

# Make an inference call with structured output
response = llm.infer(
    api_key="your-api-key",
    user_message="Extract user profile from: John Doe, 30 years old, likes reading and hiking",
    structured_output=UserProfile
)
```

### 2. AWS Module

#### S3 Operations
- Simple interface for common S3 operations:
  - Create/delete buckets
  - Upload/download objects
  - List buckets and objects
  - Delete objects

Example usage:

```python
from pdmInfra.aws.s3 import s3_put_object, s3_get_object

# Upload data to S3
s3_put_object("my-bucket", "data.json", {"key": "value"})

# Retrieve data from S3
data = s3_get_object("my-bucket", "data.json")
```

## Configuration

The library includes configuration parameters for:
- Valid LLM models
- API endpoints
- AWS region settings

## Requirements

- Python 3.6+
- boto3 for AWS operations
- requests for API calls

## License

This project is maintained by PDM Impulse Team.

## Contributing

For contributions, please contact: y.lu@pdm-solutions.com

