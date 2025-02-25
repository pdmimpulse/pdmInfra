Here's a design documentation for the PDM Infrastructure Library:

# PDM Infrastructure Library - Design Documentation

## 1. System Overview

The PDM Infrastructure Library is designed to provide a unified interface for AI application development, with a primary focus on the AI Module that enables seamless integration with multiple Large Language Model (LLM) providers through a consistent API.

## 2. Architecture

### 2.1 Core Components

#### AI Module

The AI module implements a provider-agnostic architecture with three main components:

1. **LLM Inference Engine**
   - Unified interface through `InferenceClass`
   - Provider-specific implementations:
     - OpenAI (standard and reasoning models)
     - Anthropic Claude
     - Mistral AI
   - Common features across providers:
     - Streaming responses
     - Function/tool calling
     - Structured outputs
     - Message history management

2. **Schema Management**
   - Provider-agnostic schema definitions
   - Two base models:
     - `structuredOutputBaseModel`: For structured LLM outputs
     - `functionCallingBaseModel`: For function/tool definitions
   - Automatic schema translation for each provider's format

3. **Message History Management**
   - Universal chat history tracking
   - Cross-provider message format handling
   - Tool calls and response management
   - Message order validation

### 2.2 Class Structure

#### InferenceClass
Primary interface for all LLM interactions:

```python
class InferenceClass:
    """
    Unified interface for multiple LLM providers
    
    Attributes:
        system_message (str): Initial system prompt
        model (str): Provider-specific model identifier
        temperature (float, optional): Response randomness (0-1)
        streaming (bool): Enable streaming responses
        tool_pack (list/dict): Function calling tools
        structured_output (dict): Output schema
        cost_tracker (bool): Track token usage
        seed (int, optional): Reproducibility seed
        max_tokens (int, optional): Response length limit
        reasoning_effort (str, optional): For OpenAI reasoning models
    """
```

#### Provider-Specific Implementations

1. **OpenAI Provider**
   ```python
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
   )
   ```

2. **Anthropic Provider**
   ```python
   def anthropic_inference(
       system_message: str,
       model: str,
       api_key: str,
       user_message=None,
       chat_history=None,
       streaming: bool = False,
       tool_pack=None,
       structured_output=None
   )
   ```

3. **Mistral Provider**
   ```python
   def mistral_inference(
       system_message: str,
       model: str,
       api_key: str,
       user_message=None,
       chat_history=None,
       temperature: float = 0,
       streaming: bool = False,
       structured_output=None,
       tool_pack=None,
       max_tokens: int = None
   )
   ```

#### Schema System

1. **Field Class**
   ```python
   class Field:
       """
       Schema field definition
       
       Attributes:
           description (str): Field description
           field_type (str): Data type
           optional (bool): Optional flag
           enum (list): Allowed values
           children (BaseModel): Nested schema
           array_type (str): Array item type
       """
   ```

2. **Base Schema Models**
   ```python
   class structuredOutputBaseModel:
       """Base class for output schemas"""
       @classmethod
       def generate_structured_output(cls, provider="openai")

   class functionCallingBaseModel:
       """Base class for function/tool definitions"""
       @classmethod
       def generate_function_tool(cls, provider)
   ```

## 3. Key Design Decisions

### 3.1 Provider Abstraction
- Single interface (`InferenceClass`) for all providers
- Provider-specific implementations hidden from end users
- Automatic routing based on model selection
- Consistent error handling across providers

### 3.2 Schema System
- Custom implementation for cross-provider compatibility
- Automatic schema translation for each provider
- Support for nested schemas and complex types
- Validation at schema definition time

### 3.3 Message History
- Universal history format
- Automatic conversion for provider-specific formats
- Strict message ordering enforcement
- Support for all message types (chat, function calls, tool responses)

## 4. Data Flow

### 4.1 Request Flow
1. User creates `InferenceClass` instance
2. Model selection determines provider
3. Parameters validated for provider compatibility
4. Request formatted for specific provider
5. Provider-specific API called
6. Response processed and normalized
7. Results returned in consistent format

### 4.2 Schema Processing
1. Schema defined using base models
2. Provider determined at runtime
3. Schema translated to provider format
4. Response validated against schema
5. Normalized output returned

## 5. Provider-Specific Features

### 5.1 OpenAI
- Standard and reasoning models
- Reasoning effort levels
- Cost tracking
- Seed support

### 5.2 Anthropic
- High token limits (64,000)
- System message handling
- Specialized message formatting

### 5.3 Mistral
- Temperature control
- Max tokens limit
- Structured output support

## 6. Error Handling

### 6.1 Validation Layers
1. Input Validation
   - API key format
   - Model compatibility
   - Parameter constraints

2. Runtime Validation
   - API responses
   - Schema compliance
   - Message ordering

3. Provider-Specific Validation
   - Feature compatibility
   - Response formats
   - Error messages

### 6.2 Error Categories
1. Authentication Errors
   - Invalid API keys
   - Missing credentials
   - Provider-specific formats

2. Compatibility Errors
   - Unsupported features
   - Invalid combinations
   - Provider limitations

3. Schema Errors
   - Invalid definitions
   - Validation failures
   - Format mismatches

## 7. Configuration

### 7.1 Supported Models
```python
# OpenAI Models
openaiNormalLLMList = [
    'gpt-4o-2024-08-06',
    'gpt-4o-mini-2024-07-18',
    'gpt-4o',
    'gpt-4o-mini'
]
openaiReasoningLLMList = [
    "o1-2024-12-17",
    "o3-mini"
]

# Anthropic Models
anthropicLLMList = [
    "claude-3-7-sonnet-20250219",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-haiku-20241022"
]

# Mistral Models
mistralLLMList = [
    "mistral-large-latest",
    "mistral-small"
]
```

### 7.2 API Endpoints
```python
openaiURL = "https://api.openai.com/v1/chat/completions"
anthropicURL = "https://api.anthropic.com/v1/messages"
mistralURL = "https://api.mistral.ai/v1/chat/completions"
```

## 8. Security Considerations

### 8.1 API Key Management
- No key storage in code
- Provider-specific key validation
- Per-request key usage

### 8.2 Data Handling
- No response caching by default
- Secure message history management
- Clean error messages

## 9. Future Enhancements

### 9.1 Additional Providers
- Google (Gemini)
- Perplexity
- Meta
- DeepSeek
- Hugging Face

### 9.2 Feature Enhancements
- Cross-provider cost optimization
- Automatic fallback mechanisms
- Enhanced streaming capabilities
- Improved error handling

### 9.3 Performance Improvements
- Response caching
- Parallel inference
- Rate limiting
- Batch processing

## 10. Dependencies

### Required
- requests: HTTP client
- json: JSON parsing

### Optional
- typing: Type hints
- logging: Error tracking

This design documentation reflects the current state of the PDM Infrastructure Library, with a focus on its multi-provider architecture and unified interface design. The documentation will be updated as new providers and features are added to the system.