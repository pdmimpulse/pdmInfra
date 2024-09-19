import json

class openai_message_history:
    """all messages except the system message"""
    def __init__(self):
        self.chat_history = []
    
    def add_user_message(self, user_message):
        if len(self.chat_history) == 0:
            self.chat_history.append({'role': 'user', 'content': user_message})
        elif len(self.chat_history) > 0 and self.chat_history[-1]['role'] == 'assistant':
            self.chat_history.append({'role': 'user', 'content': user_message})
        else: 
            raise TypeError("User message must be added after assistant message or before the first assistant message.")
    
    def add_assistant_message(self, assistant_message): 
        if len(self.chat_history) == 0:
            self.chat_history.append({'role': 'assistant', 'content': assistant_message})
        elif len(self.chat_history) > 0 and self.chat_history[-1]['role'] != 'assistant':
            self.chat_history.append({'role': 'assistant', 'content': assistant_message})
        else:
            raise TypeError("Assistant message must not be added after another assistant message.")
        
    def add_function_call(self, function_call):
        if len(self.chat_history) == 0:
            raise TypeError("Function call cannot be the first message.")
        elif len(self.chat_history) > 0 and self.chat_history[-1]['role'] == 'user':
            self.chat_history.append({'role': 'assistant', 'content': None, 'tool_calls': [{'id': call['id'], 'type': 'function', 'function': {'name': call['name'], 'arguments': json.dumps(call['arguments'])}} for call in function_call]})
        else:
            raise TypeError("Function call must be added after user message.")
    
    def add_tool_responses(self, tool_responses):
        if not isinstance(tool_responses, list):
            raise TypeError("tool_responses must be a list of all responses.")
        for response in tool_responses:
            try: tool_call_id_check = response['id']
            except: raise TypeError("Tool responses must have id.")
            try: tool_content_check = response['arguments']
            except: raise TypeError(f"Tool response must have content. Content missing for tool call id: {tool_call_id_check}")

        if len(self.chat_history) == 0:
            raise TypeError("Tool response cannot be the first message.")
        
        elif len(self.chat_history) > 0 and self.chat_history[-1]['role'] == 'assistant':
            try: 
                is_function_call = self.chat_history[-1]['tool_calls']
                for response in tool_responses:
                    tool_content = response['arguments']
                    response_to_add = {
                        "role": "tool",
                        "content": json.dumps(tool_content),
                        "tool_call_id": response['id']
                    }
                    self.chat_history.append(response_to_add)
            except: 
                raise TypeError("Tool response must be added after function call.")
            
        elif len(self.chat_history) > 0 and self.chat_history[-1]['role'] == 'tool':
            for response in tool_responses:
                tool_content = response['content']
                response_to_add = {
                    "role": "tool",
                    "content": json.dumps(tool_content),
                    "tool_call_id": response['id']
                }
                self.chat_history.append(response_to_add)

        else:
            raise TypeError("Tool response must be added after assistant message or other tool responses.")






def openai_chat_content_extraction(response):
    try:
        if isinstance(response, str):
            response = json.loads(response)

        output = response['choices'][0]['message']['content']

        return output
    except Exception as e:
        try:
            if response['error']:
                raise RuntimeError(response['error']['message'])
        except:
            print(f"OpenAI Response: {response}")
            raise RuntimeError(f"Error extracting function call from OpenAI response: {e}")
        
def openai_function_call_extraction(response):
    try:
        if isinstance(response, str):
            response = json.loads(response)

        tool_calls = response['choices'][0]['message']['tool_calls']
        output = []
        for call in tool_calls:
            output.append({'id': call['id'], "name": call['function']['name'], "arguments": json.loads(call['function']['arguments'])})   
        return output
    except Exception as e:
        try:
            if response['error']:
                raise RuntimeError(response['error']['message'])
        except:
            print(f"OpenAI Response: {response}")
            raise RuntimeError(f"Error extracting function call from OpenAI response: {e}")
        
def openai_structured_output_extraction(response):
    try:
        if isinstance(response, str):
            response = json.loads(response)

        output = response['choices'][0]['message']['content']

        return json.loads(output)
    except Exception as e:
        try:
            if response['error']:
                raise RuntimeError(response['error']['message'])
        except:
            print(f"OpenAI Response: {response}")
            raise RuntimeError(f"Error extracting function call from OpenAI response: {e}")
        
def openai_token_usage_tracker(response):
    try:
        if isinstance(response, str):
            response = json.loads(response)

        cost = response['usage']

        return json.loads(cost)
    except Exception as e:
        try:
            if response['error']:
                raise RuntimeError(response['error']['message'])
        except:
            raise RuntimeError(f"Error extracting function call from OpenAI response: {e}")