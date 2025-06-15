import json
import os
from idlelib.run import flush_stdout

from tooled_llm_structured import get_current_weather,get_current_time
from tooled_llm_structured import call_with_messages,get_response
from tooled_llm_structured import tools
import requests

tools_append = [
    {
        'type' : 'function',
        'function' :{
            'name' : 'get_movie_info',
            'description':'当你想查询电影的资料的时候非常有用。',
            'parameters' : {
                'type' : 'object',
                'properties' : {
                    'name':{
                        'type' : 'string',
                        'description' : '中文的电影名，如果是其他语言先转化成中文再提交。'
                    }
                },
                'required' : [
                    'name',
                ]
            }
        }
    },
    {
        'type' : 'function',
        'function' :{
            'name' : 'calculator_tool',
            'description' : '当你想进行计算的时候非常有用。里面已经加载math模块。',
            'parameters' : {
                'type' : 'object',
                'properties' : {
                    'expression' :{
                        'type' : 'string',
                        'description' : '符合Python语法的计算式，比如2+2、3*4、10/2、2.5+3.5、（1+2）*3，1e7+3。'
                    },
                },
            'required' : [
                'expression',
            ]
            } ,
        }
    },
    {
        'type' : 'function',
        'function' :{
            'name' : 'get_share',
            'description' : '当你需要知道股票信息的时候非常有用。查询前必须知道证券代码和具体时间。',
            'parameters' : {
                'type' : 'object',
                'properties' : {
                    'code' : {
                        'type' : 'string',
                        'description' : '用户要查询股票证券的代码。如果用户没有提供需要向用户询问。证券代码兼容多种格式：通达信，同花顺，聚宽，如sh000001 (000001.XSHG)    sz399006 (399006.XSHE)   sh600519 ( 600519.XSHG ) '
                    },
                    'end_date' : {
                        'type' : 'string',
                        'description' : '用户要查询时段的终止日期，如2021-04-30、2023-11-07。'
                    },
                    'frequency' : {
                        'type' : 'string',
                        'description' : '用户要查询时间的间隔，从end_date向后依次推count个，如1d, 1w, 1M,1m,5m,15m,30m,60m。d表示天，w表示周，M表示月，m表示分钟。'
                    },
                    'count' : {
                        'type' : 'int',
                        'description' : '用户要查询时间点的个数，如5，10，3，4。表示从end_date开始向后每隔frequency为一个查询时间。'
                    },
                },
                'required' : [
                    'code',
                    'end_date',
                ]
            },
        },
    },
    {
        'type' : 'function',
        'function' :{
            'name' : 'gui_calculator',
            'description' : '当用户想自己使用计算器时非常有用，可以提供给用户一个计算器。',
            'parameters' : {},
        },
    },
    {
        'type' : 'function',
        'function' :{
            'name' : 'see_screen',
            'description' : '当你想获取用户屏幕上的内容时很有用。获取的结果可能有乱码，请自己筛选。',
            'parameters' : {},
        },
    },
    {
        'type' : 'function',
        'function' :{
            'name' : 'get_weather_anytime',
            'description' : '当你想获得特定时间的天气时很有用。',
            'parameters' : {
                'type' : 'object',
                'properties' : {
                    'time':{
                        'type' : 'string',
                        'description': '需要的日期，如2025-01-02，2023-11-09，2014-05-13'
                    },
                    'location':{
                        'type' : 'string',
                        'decription' : '需要查询的地，如南京，上海，天津。'
                    }
                }
            },
        }
    },
    {
        'type' : 'function',
        'function' :{
            'name' : 'get_current_location',
            'description' : '当你想获取当前位置信息时很有用。',
            'parameters' : {},
        }
    },
]


tools.extend(tools_append)


#FUNCTIONS----------------------------------------
def get_weather_anytime(para):
    location = para['location']
    time = para['time']
    params = {
        "key": "So8QqzdeTxup9prhM",
        "location": location,
        "language": "zh-Hans",
        "unit": "c",
        "start" : 0,
        'days' : 15
    }

    url = "https://api.seniverse.com/v3/weather/daily.json"
    r = requests.get(url, params=params)
    data = r.json()["results"][0]['daily']
    for i in data:
        if i['date'] == time:
            data = i
            break
    print(data)
    # TODO： 完成对天气、温度等的信息提取，并返回一段message
    return str(data)
    #return f"{location}在{time}是{data['text_day']}天，气温最低{data['low']}度,最高{data['high']}度。"


def get_movie_info(para):
    name = para['name']
    movie_list = ['肖申克的救赎','霸王别姬','泰坦尼克号','阿甘正传','千与千寻','美丽人生','这个杀手不太冷','星际穿越','盗梦空间','楚门的世界']
    if name not in movie_list:
        return "这部电影不在豆瓣前十，暂无信息。"
    index = movie_list.index(name)
    with open(f'dataJsonDir/{index}_movie.json','r') as file:
        movie_dict = json.load(file)
    return str(movie_dict)


def calculator_tool(para) :
    """
    计算数学表达式的值

    Args:
        expression (str): 要计算的数学表达式字符串

    Returns:
        float: 计算结果

    Raises:
        ValueError: 当表达式无效或包含非法字符时
    """

    import math

    #转化参数
    expression = para['expression']
    # 移除所有空格
    expression = expression.replace(" ", "")

    # 删除。 检查表达式是否只包含允许的字符
    #allowed_chars = set("0123456789+-*/().")
    #if not all(char in allowed_chars for char in expression):
    #   return "表达式包含非法字符"

    try:
        # 使用 eval 计算表达式
        result = eval(expression)
        return f"结果是{result}。"
    except Exception as e:
        return f"表达式计算错误: {str(e)}"


def get_share(para):
    share_code = para['code']
    end_date = para['end_date']
    frequency = para['frequency'] if 'frequency' in para.keys() else "1d"
    count = para['count'] if 'count' in para.keys() else "5"

    #importing
    from tempt.Ashare.Ashare import get_price as gp

    res = gp(code=share_code, end_date=end_date, frequency=frequency, count=count)
    return str(res)


def gui_calculator():
    import tkinter as tk
    from tkinter import ttk
    import math

    class CalculatorGUI:
        def __init__(self, root):
            self.root = root
            self.root.title("科学计算器")
            self.root.geometry("500x700")
            self.root.resizable(False, False)

            # 设置主题颜色
            self.bg_color = "#f0f0f0"
            self.button_bg = "#ffffff"
            self.operator_bg = "#e6e6e6"
            self.function_bg = "#d9d9d9"
            self.equal_bg = "#4d94ff"
            self.equal_fg = "#ffffff"

            self.root.configure(bg=self.bg_color)

            # 设置样式
            self.style = ttk.Style()
            self.style.configure("Display.TEntry",
                                 padding=15,
                                 font=('Arial', 32),
                                 fieldbackground=self.bg_color)

            # 创建显示框
            self.display = ttk.Entry(root,
                                     justify="right",
                                     style="Display.TEntry")
            self.display.grid(row=0, column=0, columnspan=5,
                              padx=15, pady=20, sticky="nsew")

            # 创建按钮框架
            self.button_frame = tk.Frame(root, bg=self.bg_color)
            self.button_frame.grid(row=1, column=0, columnspan=5,
                                   padx=10, pady=10, sticky="nsew")

            # 按钮布局
            self.create_buttons()

            # 配置网格权重
            self.root.grid_rowconfigure(0, weight=1)
            self.root.grid_rowconfigure(1, weight=5)
            for i in range(5):
                self.root.grid_columnconfigure(i, weight=1)

            # 配置按钮框架的网格权重
            for i in range(6):
                self.button_frame.grid_rowconfigure(i, weight=1)
            for i in range(5):
                self.button_frame.grid_columnconfigure(i, weight=1)

        def create_button(self, parent, text, command, row, col,
                          bg=None, fg="black", width=6, height=2):
            """创建统一样式的按钮"""
            if bg is None:
                bg = self.button_bg

            btn = tk.Button(parent, text=text, command=command,
                            bg=bg, fg=fg,
                            font=('Arial', 16, 'bold'),
                            width=width, height=height,
                            relief=tk.RAISED, bd=3)
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            return btn

        def create_buttons(self):
            # 功能按钮
            functions = [
                ('sin', lambda: self.click('sin')),
                ('log', lambda: self.click('log')),
                ('tan', lambda: self.click('tan')),
                ('√', lambda: self.click('√')),
                ('^', lambda: self.click('^'))
            ]

            for i, (text, cmd) in enumerate(functions):
                self.create_button(self.button_frame, text, cmd, 0, i,
                                   bg=self.function_bg, width=8)

            # 数字和运算符按钮
            buttons = [
                ('7', lambda: self.click('7')), ('8', lambda: self.click('8')),
                ('9', lambda: self.click('9')), ('/', lambda: self.click('/')),
                ('C', lambda: self.click('C')),

                ('4', lambda: self.click('4')), ('5', lambda: self.click('5')),
                ('6', lambda: self.click('6')), ('*', lambda: self.click('*')),
                ('←', lambda: self.click('←')),

                ('1', lambda: self.click('1')), ('2', lambda: self.click('2')),
                ('3', lambda: self.click('3')), ('-', lambda: self.click('-')),
                ('(', lambda: self.click('(')),

                ('0', lambda: self.click('0')), ('.', lambda: self.click('.')),
                ('π', lambda: self.click('π')), ('+', lambda: self.click('+')),
                (')', lambda: self.click(')')),

                ('e', lambda: self.click('e')), ('**', lambda: self.click('**')),
                ('(', lambda: self.click('(')), (')', lambda: self.click(')')),
                ('=', lambda: self.click('='))
            ]

            row = 1
            col = 0
            for button in buttons:
                text, cmd = button
                if text == '=':
                    bg, fg = self.equal_bg, self.equal_fg
                elif text in '+-*/^':
                    bg = self.operator_bg
                    fg = "black"
                else:
                    bg = self.button_bg
                    fg = "black"

                width = 8 if text == '=' else 6
                height = 2

                self.create_button(self.button_frame, text, cmd, row, col,
                                   bg=bg, fg=fg, width=width, height=height)

                col += 1
                if col > 4:
                    col = 0
                    row += 1

        def calculate(self, expression: str) -> float:
            """
            计算数学表达式的值

            Args:
                expression (str): 要计算的数学表达式字符串

            Returns:
                float: 计算结果

            Raises:
                ValueError: 当表达式无效或包含非法字符时
            """
            # 移除所有空格
            expression = expression.replace(" ", "")

            # 检查表达式是否只包含允许的字符
            allowed_chars = set("0123456789+-*/().eπsinlogtan√^")
            if not all(char in allowed_chars for char in expression):
                raise ValueError("表达式包含非法字符")

            # 替换特殊字符
            expression = expression.replace("π", str(math.pi))
            expression = expression.replace("^", "**")
            expression = expression.replace("√", "math.sqrt")

            # 处理特殊函数
            if "sin" in expression:
                expression = expression.replace("sin", "math.sin")
            if "log" in expression:
                expression = expression.replace("log", "math.log10")
            if "tan" in expression:
                expression = expression.replace("tan", "math.tan")

            try:
                # 使用 eval 计算表达式
                result = eval(expression)
                return float(result)
            except Exception as e:
                raise ValueError(f"表达式计算错误: {str(e)}")

        def click(self, key):
            if key == '=':
                # 计算结果
                try:
                    result = self.calculate(self.display.get())
                    self.display.delete(0, tk.END)
                    self.display.insert(tk.END, str(result))
                except ValueError as e:
                    self.display.delete(0, tk.END)
                    self.display.insert(tk.END, "错误")
            elif key == 'C':
                # 清除显示
                self.display.delete(0, tk.END)
            elif key == '←':
                # 删除最后一个字符
                current = self.display.get()
                self.display.delete(0, tk.END)
                self.display.insert(0, current[:-1])
            elif key in ['sin', 'log', 'tan', '√']:
                # 添加函数和括号
                self.display.insert(tk.END, f"{key}(")
            elif key == 'π':
                self.display.insert(tk.END, "π")
            elif key == 'e':
                self.display.insert(tk.END, "e")
            elif key == '^':
                self.display.insert(tk.END, "^")
            else:
                # 添加按钮文本到显示框
                self.display.insert(tk.END, key)


    """
    创建并运行计算器GUI

    Returns:
        None
    """
    print("已生成计算器界面！请查看。")
    root = tk.Tk()
    app = CalculatorGUI(root)
    root.mainloop()



    return "用户已结束使用计算器。"




def see_screen():
    from PIL import ImageGrab
    def screen_shot():
        # security
        if os.path.isfile('original.png'):
            os.remove('original.png')
        if os.path.isfile('translated.png'):
            os.remove('translated.png')

        # execute
        screenshot = ImageGrab.grab()
        screenshot.save("original.png")

        return 'original.png'

    def png2doc(filename):
        import cv2
        import pytesseract

        # 读取图片
        image = cv2.imread(filename)

        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 二值化处理
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # 识别文字
        text = pytesseract.image_to_string(thresh, lang='chi_sim+eng')

        print(text)

        return text


    text = png2doc(screen_shot())

    return f"屏幕上的文字转化成文本为：\n\n\n{text}"



def get_current_location():
    """
    获取当前位置信息
    
    Returns:
        str: 当前位置信息
    """
    import requests
    
    try:
        # 使用ip-api.com的免费API获取位置信息
        response = requests.get('http://ip-api.com/json/')
        data = response.json()
        
        if data['status'] == 'success':
            location_info = {
                'country': data.get('country', 'Unknown'),
                'region': data.get('regionName', 'Unknown'),
                'city': data.get('city', 'Unknown'),
                'isp': data.get('isp', 'Unknown'),
                'ip': data.get('query', 'Unknown')
            }
            return f"当前位置信息：\n国家：{location_info['country']}\n地区：{location_info['region']}\n城市：{location_info['city']}\n网络服务商：{location_info['isp']}\nIP地址：{location_info['ip']}"
        else:
            return "无法获取位置信息"
    except Exception as e:
        return f"获取位置信息时出错：{str(e)}"

#----------------------------------------------------------------



#MAPPER-----------------------------------------------------------
function_mapper = {
    'get_weather_anytime' : get_weather_anytime,
    'get_current_time' : get_current_time,
    'get_current_weather' : get_current_weather,
    'get_movie_info' : get_movie_info,
    'calculator_tool' : calculator_tool,
    'get_share' : get_share,
    'gui_calculator' : gui_calculator,
    'see_screen' : see_screen,
    'get_current_location' : get_current_location,
}

#-----------------------------------------------------------------

#EXECUTION--------------------------------------------------------

def llm_action(messages):
    #Config
    api_key = "sk-46f61c60859f4d19a1de714803d10f3e"
    url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'
    headers = {'Content-Type': 'application/json',
               'Authorization': f'Bearer {api_key}'}
    body = {
        'model': 'qwen-turbo',
        "input": {
            "messages": messages
        },
        "parameters": {
            "result_format": "message",
            "tools": tools
        }
    }

    #Get response
    print(messages)
    response = requests.post(url, headers=headers, json=body)
    print(response.json(),flush=True)

    #Process response
    choice = response.json()['output']['choices'][0]
    messages.append(choice['message'])

    #Diverge
    if choice['finish_reason'] == 'tool_calls':
        #config
        tool_info = {"name": choice['message']['tool_calls'][0]['function']['name'], "role": "tool"}
        arguments = eval(choice['message']['tool_calls'][0]['function']['arguments'])
        if arguments:
            tool_info["content"] = function_mapper[tool_info['name']](arguments)
        else:
            tool_info["content"] = function_mapper[tool_info['name']]()
        messages.append(tool_info)

        #continue
        return llm_action(messages)


    elif choice['finish_reason'] == 'stop':
        #continue
        return choice['message']['content'],messages




def converse(messages):
    #query对话
    print("请与大模型对话:",flush=True)
    query = str(input())

    #退出
    if query == 'exit':
        print('goodbye!')
        return None

    #测试作业第一项
    if query == '$test_1':
        call_with_messages()
        converse(
            [
                {
                    'role': 'system',
                    'content': f'You\' re a helpful assistant. {get_current_time()}'
                }
            ]
        )


    #进行递归对话
    messages.append({"content":query,
                     "role":"user"
    })
    response = llm_action(messages)
    print(response[0],flush=True)
    converse(response[1])





#---------------------------------------------------------------

if __name__ == '__main__':
    converse(
        [
            {
                'role':'system',
                'content' :f'You\' re a helpful assistant. {get_current_time()}'
            }
        ]
    )




