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


    Attributes:
        generate_json_schema (class method): A class method to generate a JSON schema for the model.
    """

    @classmethod
    def generate_structured_output(cls):
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

        for attr_name, attr_value in cls.__dict__.items():
            if isinstance(attr_value, Field):
                property_schema = {
                    "type": attr_value.field_type
                }

                if attr_value.description:
                    property_schema["description"] = attr_value.description

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
                        if isinstance(attr_value.children, type) and issubclass(attr_value.children, structuredOutputBaseModel):
                            property_schema["items"] = attr_value.children.generate_structured_output()["json_schema"]["schema"]
                        else:
                            raise ValueError("Children attribute must be a subclass of JsonSchemaBaseModel")
                    elif array_type:
                        property_schema["items"] = {"type": array_type}
                elif attr_value.field_type == "object":
                    if not isinstance(attr_value.children, type) or not issubclass(attr_value.children, structuredOutputBaseModel):
                        raise ValueError("Object children must be a subclass of structuredOutputBaseModel")
                    property_schema = attr_value.children.generate_structured_output()["json_schema"]["schema"]

                schema["json_schema"]["schema"]["required"].append(attr_name)

                schema["json_schema"]["schema"]["properties"][attr_name] = property_schema

        return schema

class functionCallingBaseModel:
    """
    This class represents a base model for generating function calling tools.
    """
    @classmethod
    def generate_function_tool(cls):
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
                            property_schema["items"] = attr_value.children.generate_function_tool()["function"]["parameters"]
                        else:
                            raise ValueError("Children attribute must be a subclass of JsonSchemaBaseModel")
                    elif array_type:
                        property_schema["items"] = {"type": array_type}
                elif attr_value.field_type == "object":
                    if not isinstance(attr_value.children, type) or not issubclass(attr_value.children, functionCallingBaseModel):
                        raise ValueError("Object children must be a subclass of functionCallingBaseModel")
                    property_schema = attr_value.children.generate_function_tool()["function"]["parameters"]
                        
                if not attr_value.optional:
                    schema["function"]["parameters"]["required"].append(attr_name)

                schema["function"]["parameters"]["properties"][attr_name] = property_schema

        return schema