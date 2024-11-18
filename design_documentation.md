Here's a design documentation for the PDM Infrastructure Library:

# PDM Infrastructure Library - Design Documentation

## 1. System Overview

The PDM Infrastructure Library is designed to provide a unified interface for AI application development, focusing on two main components:
- AI Module: LLM integration and structured output handling
- AWS Module: Cloud infrastructure utilities

## 2. Architecture

### 2.1 Core Components

#### AI Module

```1:7:pdmInfra/ai/LLM_inference/__init__.py
"""
This modules sends a request to LLM APIs across different providers. This aims to provide a unified interface for different LLM APIs.
The best practice is to create a InferenceClass object for individual use cases and name the object as per the use case.

Currently only supports OpenAI, which offers the most capability from their models. 
We aim to emulate these capabilities in other models through prompt engineering and other techniques here.
"""
```


The AI module consists of three main components:
1. **LLM Inference Engine**
   - Unified interface for multiple LLM providers
   - Currently supports OpenAI with plans for Mistral and Anthropic
   - Handles streaming, function calling, and structured outputs

2. **Schema Management**
   - Custom JSON schema implementation
   - Two base models:
     - `structuredOutputBaseModel`: For structured LLM outputs
     - `functionCallingBaseModel`: For function calling tools

3. **Message History Management**
   - Tracks conversation history
   - Manages tool calls and responses
   - Ensures message order consistency

#### AWS Module
Simple interface for AWS services, currently implementing:
- S3 operations (create, read, update, delete)
- Future plans for other AWS services

### 2.2 Class Structure

#### InferenceClass
Primary interface for LLM interactions:

```16:34:pdmInfra/ai/LLM_inference/__init__.py
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
```


#### Field Class
Base class for schema definition:

```5:29:pdmInfra/ai/json_schema.py
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


## 3. Key Design Decisions

### 3.1 Schema Implementation
- Custom implementation instead of Pydantic
- Reasons:
  - Reduced dependencies
  - Simplified boilerplate
  - Better control over schema generation
  - Direct integration with LLM APIs

### 3.2 Error Handling
- Implemented retry mechanism for API calls

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


### 3.3 Message History Management
- Strict message ordering enforcement
- Type checking for message additions
- Support for function calls and tool responses

## 4. Data Flow

### 4.1 LLM Request Flow
1. User creates InferenceClass instance
2. Parameters validated
3. Request formatted based on model provider
4. Response processed through appropriate extractor
5. Structured output or function calls handled
6. Results returned to user

### 4.2 Schema Generation Flow
1. User defines model class
2. Fields processed during generation
3. Nested schemas handled recursively
4. Final schema formatted for API consumption

## 5. Configuration Management

### 5.1 LLM Configuration

```7:12:pdmInfra/ai/param.py
validLLMList = ['gpt-4o-2024-08-06', 'gpt-4o-mini-2024-07-18', 'gpt-4o', 'gpt-4o-mini']
openaiLLMList = ['gpt-4o-2024-08-06', 'gpt-4o-mini-2024-07-18', 'gpt-4o', 'gpt-4o-mini']
pplxLLMList = []
mistralLLMList = []

openaiURL = "https://api.openai.com/v1/chat/completions"
```


### 5.2 AWS Configuration
- Region-based configuration
- Credential management through boto3

## 6. Future Enhancements

### 6.1 Planned Features
1. Additional LLM Providers
   - Anthropic Claude
   - Mistral AI
   - Local models

2. AWS Services
   - Lambda integration
   - DynamoDB support
   - SageMaker deployment

3. Enhanced Features
   - Automated cost optimization
   - Response caching
   - Parallel inference
   - Enhanced error handling

### 6.2 Technical Debt
1. Add comprehensive test suite
2. Implement logging system
3. Add input validation for all AWS operations
4. Enhance documentation with more examples

## 7. Dependencies

### Required
- requests: HTTP client
- boto3: AWS SDK
- json: JSON parsing

### Optional
- logging: Error tracking
- typing: Type hints

## 8. Security Considerations

1. API Key Management
   - Keys passed per request
   - No key storage in code
   - Environment variable support

2. AWS Security
   - IAM role support
   - Minimal permission principle
   - Region-specific operations

## 9. Performance Considerations

1. Retry Mechanism
   - 3 attempts for failed requests
   - Exponential backoff recommended

2. Memory Management
   - Streaming support for large responses
   - Efficient message history handling

3. Response Processing
   - Dedicated extractors for different response types
   - Error handling for malformed responses

This documentation provides a comprehensive overview of the library's design and architecture while maintaining future extensibility and security considerations.