import requests



class Agent():
    def __init__(self,messages,url='https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation',key='sk-46f61c60859f4d19a1de714803d10f3e',):
        #chat history for prediction
        self.messages = messages
        #api key for llm on website
        self.api_key = key
        #llm website url
        self.llm_url = url
        #llm tools related
        self.tools = []
        self.func = []
        self.mapper = {}


    def call_via_sdk(self):
        api_key = self.api_key
        url = self.llm_url
        tools = self.tools
        function_mapper = self.mapper
        headers = {'Content-Type': 'application/json',
                   'Authorization': f'Bearer {api_key}'}
        body = {
            'model': 'qwen-turbo',
            "input": {
                "messages": self.messages
            },
            "parameters": {
                "result_format": "message",
                "tools": tools
            }
        }

        #get response
        response = requests.post(url, headers=headers, json=body)

        #Process response
        choice = response.json()['output']['choices'][0]
        self.messages.append(choice['message'])

        # Diverge
        if choice['finish_reason'] == 'tool_calls':
            # config
            tool_info = {"name": choice['message']['tool_calls'][0]['function']['name'], "role": "tool"}
            arguments = eval(choice['message']['tool_calls'][0]['function']['arguments'])
            if arguments:
                if tool_info['name'] == 'python_interactive_execute_tool':
                    arguments['message'] = self.messages
                tool_info["content"] = function_mapper[tool_info['name']](arguments)
            else:
                tool_info["content"] = function_mapper[tool_info['name']]()
            self.messages.append(tool_info)

            # continue
            return self.call_via_sdk()


        elif choice['finish_reason'] == 'stop':
            # continue
            return choice['message']['content']



    def register_func(self,func,tool_desc):
        self.func.append(func)
        self.mapper[func.__name__] = func
        self.tools.append(tool_desc)
        # {
        #     'type': 'function',
        #     'function': {
        #         'name': func.__name__,
        #         'description': '',
        #         'parameters': {
        #             'type': 'object',
        #             'properties': {
        #                 '': {
        #                     'type': 'string',
        #                     'description': ''
        #                 }
        #             },
        #             'required': [
        #                 '',
        #             ]
        #         }
        #     }
        # },


