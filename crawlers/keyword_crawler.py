import requests
import time
from config import AMAP_API_KEY, CRAWLER_CONFIG

class KeywordCrawler:
    def __init__(self):
        self.api_key = AMAP_API_KEY
        self.page_size = CRAWLER_CONFIG["page_size"]
        self.max_retries = CRAWLER_CONFIG["max_retries"]
        self.retry_interval = CRAWLER_CONFIG["retry_interval"]
        self.request_interval = CRAWLER_CONFIG["request_interval"]
    
    def search(self, keyword, city, types=None, extensions="all"):
        """
        基于关键词和城市搜索 POI 数据
        :param keyword: 搜索关键词
        :param city: 城市名称或城市编码
        :param types: POI 类型，可选
        :param extensions: 返回结果控制，"base" 或 "all"
        :return: POI 数据列表
        """
        pois = []
        page = 1
        has_more = True
        
        while has_more:
            url = "https://restapi.amap.com/v3/place/text"
            params = {
                "key": self.api_key,
                "keywords": keyword,
                "city": city,
                "types": types,
                "extensions": extensions,
                "page": page,
                "offset": self.page_size,
                "output": "json"
            }
            
            # 发送请求并处理重试
            response = self._request_with_retry(url, params)
            if not response:
                break
            
            data = response.json()
            
            # 检查请求是否成功
            if data.get("status") != "1":
                print(f"请求失败: {data.get('info')}")
                break
            
            # 提取 POI 数据
            current_pois = data.get("pois", [])
            current_count = len(current_pois)
            pois.extend(current_pois)
            
            # 检查是否还有更多数据
            count = int(data.get("count", 0))
            total = int(data.get("total", 0))
            
            # 检查是否遇到 API 限制
            if count == 0 and current_count == 0:
                print("API 调用限制，停止爬取")
                has_more = False
            # 改进分页逻辑
            elif total > 0:
                # 如果有 total 字段，使用它来判断
                if len(pois) >= total:
                    has_more = False
                else:
                    page += 1
                    # 避免触发频率限制
                    time.sleep(self.request_interval)
            else:
                # 如果 total 为 0，根据当前页返回的数据量判断
                if current_count < self.page_size:
                    # 如果返回的数据少于每页大小，说明没有更多数据
                    has_more = False
                else:
                    # 否则继续下一页
                    page += 1
                    # 避免触发频率限制
                    time.sleep(self.request_interval)
        
        return pois
    
    def _request_with_retry(self, url, params):
        """
        带重试的请求
        :param url: 请求 URL
        :param params: 请求参数
        :return: 响应对象或 None
        """
        for i in range(self.max_retries):
            try:
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    return response
                else:
                    print(f"请求失败，状态码: {response.status_code}")
            except Exception as e:
                print(f"请求异常: {e}")
            
            if i < self.max_retries - 1:
                print(f"重试中... ({i+1}/{self.max_retries})")
                time.sleep(self.retry_interval)
        
        return None
