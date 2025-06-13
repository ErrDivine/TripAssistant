import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class CtripAPI:
    def __init__(self):
        self.api_key = os.getenv('CTRIP_API_KEY')
        self.base_url = "https://open.ctrip.com/api"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def search_hotels(self, city_code, check_in, check_out, adults=2, children=0):
        """
        搜索酒店信息
        :param city_code: 城市代码
        :param check_in: 入住日期 (YYYY-MM-DD)
        :param check_out: 离店日期 (YYYY-MM-DD)
        :param adults: 成人数量
        :param children: 儿童数量
        :return: 酒店列表
        """
        endpoint = f"{self.base_url}/hotel/search"
        params = {
            'cityCode': city_code,
            'checkIn': check_in,
            'checkOut': check_out,
            'adults': adults,
            'children': children
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"搜索酒店时发生错误: {e}")
            return None

    def search_flights(self, from_city, to_city, departure_date, return_date=None):
        """
        搜索航班信息
        :param from_city: 出发城市代码
        :param to_city: 到达城市代码
        :param departure_date: 出发日期 (YYYY-MM-DD)
        :param return_date: 返程日期 (YYYY-MM-DD)，可选
        :return: 航班列表
        """
        endpoint = f"{self.base_url}/flight/search"
        params = {
            'fromCity': from_city,
            'toCity': to_city,
            'departureDate': departure_date,
            'returnDate': return_date
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"搜索航班时发生错误: {e}")
            return None

    def get_city_attractions(self, city_code):
        """
        获取城市景点信息
        :param city_code: 城市代码
        :return: 景点列表
        """
        endpoint = f"{self.base_url}/attraction/list"
        params = {
            'cityCode': city_code
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"获取景点信息时发生错误: {e}")
            return None

    def get_weather(self, city_code):
        """
        获取城市天气信息
        :param city_code: 城市代码
        :return: 天气信息
        """
        endpoint = f"{self.base_url}/weather/forecast"
        params = {
            'cityCode': city_code
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"获取天气信息时发生错误: {e}")
            return None

def main():
    # 使用示例
    ctrip = CtripAPI()
    
    # 示例：搜索北京的酒店
    hotels = ctrip.search_hotels(
        city_code='110000',  # 北京的城市代码
        check_in='2024-04-01',
        check_out='2024-04-03'
    )
    
    if hotels:
        print("酒店搜索结果：")
        print(json.dumps(hotels, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main() 