"""
Example usage of the PDM AI Library HuggingFace integration.
This demonstrates how to use the HuggingFace provider with llama-3.1-8b-instruct.
"""
import os
import json
from dotenv import load_dotenv
from pdmInfra.ai.LLM_inference import InferenceClass
from pdmInfra.ai.json_schema import structuredOutputBaseModel, functionCallingBaseModel, Field
from pdmInfra.ai.LLM_inference.openai_tools import openai_message_history

# Load environment variables from .env file
load_dotenv()

# Get the HuggingFace API key from environment variables
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Define example structured output schemas
class Address(structuredOutputBaseModel):
    """A physical address"""
    street = Field(description="Street address")
    city = Field(description="City name")
    state = Field(description="State or province")
    zip_code = Field(description="Postal code")
    country = Field(description="Country name", optional=True)

class Education(structuredOutputBaseModel):
    """Educational background information"""
    degree = Field(description="Type of degree")
    institution = Field(description="Name of school or university")
    year = Field(description="Year completed", field_type="integer")

class UserProfile(structuredOutputBaseModel):
    """Complete user profile information"""
    name = Field(description="Full name of the user")
    age = Field(description="User's age in years", field_type="integer")
    email = Field(description="Email address", optional=True)
    bio = Field(description="Short biography", optional=True)
    is_student = Field(description="Whether the user is currently a student", field_type="boolean")
    address = Field(description="Physical address", field_type="object", children=Address)
    skills = Field(description="List of skills", field_type="array", array_type="string")
    education = Field(description="Educational background", field_type="array", children=Education)

class SearchFilters(functionCallingBaseModel):
    """Search filters"""
    date_range = Field(description="Date range for the search", optional=True)
    categories = Field(description="Categories to search in", field_type="array", array_type="string", optional=True)
    max_results = Field(description="Maximum number of results to return", field_type="integer", optional=True)

# Define example function calling schemas
class SearchFunction(functionCallingBaseModel):
    """Search for information in the database"""
    query = Field(description="The search query")
    filters = Field(description="Optional filters for the search", field_type="object", optional=True, children=SearchFilters)

class WeatherFunction(functionCallingBaseModel):
    """Get the current weather or forecast for a location"""
    location = Field(description="City and state, or city and country")
    unit = Field(description="Temperature unit", enum=["celsius", "fahrenheit"])
    forecast = Field(description="Get forecast instead of current weather", field_type="boolean", optional=True)
    days = Field(description="Number of days for forecast", field_type="integer", optional=True)


async def huggingface_structured_output_example():
    """Example of using structured output with HuggingFace"""
    print("\n=== HuggingFace Structured Output Example ===\n")
    
    # Create an inference object
    llm = InferenceClass()
    llm.system_message = "You are a helpful assistant that provides information about users."
    llm.model = "llama-3.1-8b-instruct"
    
    # Make the API call
    response = llm.infer(
        api_key=HF_API_KEY,
        user_message="Create a profile for a fictional graduate student named Emma Chen who is studying Computer Science.",
        structured_output=UserProfile
    )
    
    print(json.dumps(response, indent=2))
    return response

async def huggingface_nested_structured_output_example():
    """Example of using nested structured output with HuggingFace"""
    print("\n=== HuggingFace Nested Structured Output Example ===\n")
    
    # Create an inference object
    llm = InferenceClass()
    llm.system_message = "You are a helpful assistant that provides information about users."
    llm.model = "llama-3.1-8b-instruct"
    
    # Make the API call
    response = llm.infer(
        api_key=HF_API_KEY,
        user_message="Generate a user profile for a fictional person named John Smith who lives in New York.",
        structured_output=UserProfile
    )
    
    print(json.dumps(response, indent=2))
    return response

async def huggingface_function_calling_example():
    """Example of using function calling with HuggingFace"""
    print("\n=== HuggingFace Function Calling Example ===\n")
    
    # Create an inference object
    llm = InferenceClass()
    llm.system_message = "You are a helpful assistant with access to search functionality."
    llm.model = "llama-3.1-8b-instruct"
    
    # Make the API call
    response = llm.infer(
        api_key=HF_API_KEY,
        user_message="I need to find recent research papers on transformer models in NLP.",
        tool_pack=SearchFunction
    )
    
    print(json.dumps(response, indent=2))
    return response

async def huggingface_multi_tool_function_calling_example():
    """Example of using multiple function calling tools with HuggingFace"""
    print("\n=== HuggingFace Multi-Tool Function Calling Example ===\n")
    
    # Create an inference object
    llm = InferenceClass()
    llm.system_message = "You are a helpful assistant with access to search and weather information."
    llm.model = "llama-3.1-8b-instruct"
    
    # Make the API call
    response = llm.infer(
        api_key=HF_API_KEY,
        user_message="What's the weather like in San Francisco? And can you also search for popular tourist attractions there?",
        tool_pack=[WeatherFunction, SearchFunction]
    )
    
    print(json.dumps(response, indent=2))
    return response

async def huggingface_streaming_chat_example():
    """Example of streaming chat with HuggingFace"""
    print("\n=== HuggingFace Streaming Chat Example ===\n")
    
    # Create an inference object
    llm = InferenceClass()
    llm.system_message = "You are a knowledgeable assistant. Provide detailed responses to questions."
    llm.model = "llama-3.1-8b-instruct"
    
    # Make the API call
    response_generator = llm.infer(
        api_key=HF_API_KEY,
        user_message="Write a short paragraph explaining how transformers work in natural language processing.",
        streaming=True
    )
    
    # Process streaming response
    for chunk in response_generator:
        print(chunk, end="", flush=True)
    print("\n")

async def huggingface_chat_history_example():
    """Example of using chat history with HuggingFace"""
    print("\n=== HuggingFace Chat History Example ===\n")
    
    # Create a chat history
    chat_history = openai_message_history()
    chat_history.add_user_message("What is machine learning?")
    chat_history.add_assistant_message("Machine learning is a field of study that gives computers the ability to learn without being explicitly programmed. It focuses on algorithms that can learn from and make predictions based on data.")
    
    # Create an inference object
    llm = InferenceClass()
    llm.system_message = "You are a knowledgeable assistant specializing in AI and machine learning."
    llm.model = "llama-3.1-8b-instruct"
    
    # Make the API call with chat history
    response = llm.infer(
        api_key=HF_API_KEY,
        user_message="What's the difference between supervised and unsupervised learning?",
        chat_history=chat_history
    )
    
    print(response)
    return response

# Run all examples
if __name__ == "__main__":
    import asyncio
    
    async def main():
        await huggingface_structured_output_example()
        await huggingface_nested_structured_output_example()
        await huggingface_function_calling_example()
        await huggingface_multi_tool_function_calling_example()
        await huggingface_streaming_chat_example()
        await huggingface_chat_history_example()
    
    asyncio.run(main())