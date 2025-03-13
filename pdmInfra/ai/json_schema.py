"""
This replaces langchain function calling pydantics package with a custom implimentation. This allows the same ease and visual in development and reduces the need to write boilerplate structure every time. 
"""

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
        if field_type == "object" and not children:
            raise TypeError("Object type must have children")
        if field_type == "object" and array_type:
            raise TypeError("Object type cannot have array_type")
        

class structuredOutputBaseModel:
    """
    This class represents a base model for generating JSON schemas for LLM structured outputs. 
    Supports different providers: openai, anthropic, mistral, groq
    """

    @classmethod
    def generate_structured_output(cls, provider="openai"):
        if provider not in ["openai", "anthropic", "mistral", "groq"]:
            raise ValueError("Provider must be one of: openai, anthropic, mistral, groq")

        # Initialize schema based on provider
        if provider == "openai":
            schema = {
                "type": "json_schema",
                "json_schema": {
                    "name": cls.__name__,
                    "description": cls.__doc__.strip() if cls.__doc__ else "",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False,
                        "required": []
                    },
                    "strict": True
                }
            }
        elif provider == "mistral":
            schema = {
                "type": "json_schema",
                "json_schema": {
                    "name": cls.__name__.lower(),
                    "strict": True,
                    "schema": {
                        "title": cls.__name__,
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False,
                        "required": []
                    }
                }
            }
        elif provider == "anthropic":
            schema = {
                "name": cls.__name__,
                "description": cls.__doc__.strip() if cls.__doc__ else "",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        elif provider == "groq":
            schema = {
                "type": "function",
                "function": {
                    "name": cls.__name__,
                    "description": cls.__doc__.strip() if cls.__doc__ else "",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False,
                        "required": []
                    }
                }
            }

        for attr_name, attr_value in cls.__dict__.items():
            if isinstance(attr_value, Field):
                # Base property schema
                if provider == "mistral":
                    property_schema = {
                        "type": attr_value.field_type,
                        "title": attr_name.capitalize()
                    }
                else:
                    property_schema = {
                        "type": attr_value.field_type
                    }

                if attr_value.description and provider != "mistral":
                    property_schema["description"] = attr_value.description

                if attr_value.enum:
                    property_schema["enum"] = attr_value.enum

                # Handle optional fields differently per provider
                if attr_value.optional:
                    if provider == "openai" or provider == "anthropic":
                        property_schema["type"] = [attr_value.field_type, "null"]
                        if provider == "openai":
                            schema["json_schema"]["schema"]["required"].append(attr_name)
                        elif provider == "anthropic":
                            schema["input_schema"]["required"].append(attr_name)
                        # For Mistral, we just don't add it to required list
                else:
                    # Only add non-optional fields to required list
                    if provider in ["openai", "mistral"]:
                        schema["json_schema"]["schema"]["required"].append(attr_name)
                    elif provider == "anthropic":
                        schema["input_schema"]["required"].append(attr_name)
                    elif provider == "groq":
                        schema["function"]["parameters"]["required"].append(attr_name)

                if attr_value.field_type == "array":
                    try: 
                        children_schema = attr_value.children
                    except: 
                        children_schema = None
                    try: 
                        array_type = attr_value.array_type
                    except: 
                        array_type = None
                    if children_schema and array_type:
                        raise TypeError("Cannot have both children and array_type")
                    if not children_schema and not array_type:
                        raise TypeError("Array type must have either children or array_type")
                    if children_schema:
                        if isinstance(attr_value.children, type) and issubclass(attr_value.children, structuredOutputBaseModel):
                            nested_schema = attr_value.children.generate_structured_output(provider=provider)
                            if provider == "openai":
                                property_schema["items"] = nested_schema["json_schema"]["schema"]
                            elif provider == "mistral":
                                property_schema["items"] = nested_schema["json_schema"]["schema"]
                            elif provider == "anthropic":
                                property_schema["items"] = nested_schema["input_schema"]
                        else:
                            raise ValueError("Children attribute must be a subclass of structuredOutputBaseModel")
                    elif array_type:
                        property_schema["items"] = {"type": array_type}
                elif attr_value.field_type == "object":
                    if not isinstance(attr_value.children, type) or not issubclass(attr_value.children, structuredOutputBaseModel):
                        raise ValueError("Object children must be a subclass of structuredOutputBaseModel")
                    nested_schema = attr_value.children.generate_structured_output(provider=provider)
                    if provider == "openai":
                        property_schema = nested_schema["json_schema"]["schema"]
                    elif provider == "mistral":
                        property_schema = nested_schema["json_schema"]["schema"]
                    elif provider == "anthropic":
                        property_schema = nested_schema["input_schema"]

                # Add property to schema
                if provider in ["openai", "mistral"]:
                    schema["json_schema"]["schema"]["properties"][attr_name] = property_schema
                elif provider == "anthropic":
                    schema["input_schema"]["properties"][attr_name] = property_schema
                elif provider == "groq":
                    schema["function"]["parameters"]["properties"][attr_name] = property_schema

        return schema

class functionCallingBaseModel:
    """
    This class represents a base model for generating function calling tools.
    Supports different providers: openai, anthropic, mistral, groq
    """
    @classmethod
    def generate_function_tool(cls, provider):
        if provider not in ["openai", "anthropic", "mistral", "groq"]:
            raise ValueError("Provider must be one of: openai, anthropic, mistral, groq")

        # Initialize the base schema based on provider
        if provider == "openai":
            schema = {
                "type": "function",
                "function": {
                    "name": cls.__name__,
                    "description": cls.__doc__.strip() if cls.__doc__ else "",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False,
                        "required": []
                    }
                }
            }
        elif provider == "anthropic":
            schema = {
                "name": cls.__name__,
                "description": cls.__doc__.strip() if cls.__doc__ else "",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        elif provider == "mistral":
            schema = {
                "type": "function",
                "function": {
                    "name": cls.__name__,
                    "description": cls.__doc__.strip() if cls.__doc__ else "",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        elif provider == "groq":
            schema = {
                "type": "function",
                "function": {
                    "name": cls.__name__,
                    "description": cls.__doc__.strip() if cls.__doc__ else "",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }

        for attr_name, attr_value in cls.__dict__.items():
            if isinstance(attr_value, Field):
                property_schema = {
                    "type": attr_value.field_type,
                    "description": attr_value.description
                }

                if attr_value.enum:
                    property_schema["enum"] = attr_value.enum

                if attr_value.optional:
                    property_schema["type"] = [attr_value.field_type, "null"]

                if attr_value.field_type == "array":
                    try: 
                        children_schema = attr_value.children
                    except: 
                        children_schema = None
                    try: 
                        array_type = attr_value.array_type
                    except: 
                        array_type = None
                    if children_schema and array_type:
                        raise TypeError("Cannot have both children and array_type")
                    if not children_schema and not array_type:
                        raise TypeError("Array type must have either children or array_type")
                    if children_schema:
                        if isinstance(attr_value.children, type) and issubclass(attr_value.children, functionCallingBaseModel):
                            nested_schema = attr_value.children.generate_function_tool(provider=provider)
                            if provider == "openai":
                                property_schema["items"] = nested_schema["function"]["parameters"]
                            elif provider == "anthropic":
                                property_schema["items"] = nested_schema["input_schema"]
                            elif provider == "mistral":
                                property_schema["items"] = nested_schema["function"]["parameters"]
                        else:
                            raise ValueError("Children attribute must be a subclass of functionCallingBaseModel")
                    elif array_type:
                        property_schema["items"] = {"type": array_type}
                elif attr_value.field_type == "object":
                    if not isinstance(attr_value.children, type) or not issubclass(attr_value.children, functionCallingBaseModel):
                        raise ValueError("Object children must be a subclass of functionCallingBaseModel")
                    nested_schema = attr_value.children.generate_function_tool(provider=provider)
                    if provider == "openai":
                        property_schema = nested_schema["function"]["parameters"]
                    elif provider == "anthropic":
                        property_schema = nested_schema["input_schema"]
                    elif provider == "mistral":
                        property_schema = nested_schema["function"]["parameters"]

                # Add to required list if not optional
                if not attr_value.optional:
                    if provider in ["openai", "groq"]:
                        schema["function"]["parameters"]["required"].append(attr_name)
                    elif provider == "anthropic":
                        schema["input_schema"]["required"].append(attr_name)
                    elif provider == "mistral":
                        schema["function"]["parameters"]["required"].append(attr_name)

                # Add property to schema
                if provider in ["openai", "groq"]:
                    schema["function"]["parameters"]["properties"][attr_name] = property_schema
                elif provider == "anthropic":
                    schema["input_schema"]["properties"][attr_name] = property_schema
                elif provider == "mistral":
                    schema["function"]["parameters"]["properties"][attr_name] = property_schema

        return schema