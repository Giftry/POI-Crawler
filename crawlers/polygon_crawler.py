import requests
import time
import json
from config import AMAP_API_KEY, CRAWLER_CONFIG

class PolygonCrawler:
    def __init__(self):
        self.api_key = AMAP_API_KEY
        self.page_size = CRAWLER_CONFIG["page_size"]
        self.max_retries = CRAWLER_CONFIG["max_retries"]
        self.retry_interval = CRAWLER_CONFIG["retry_interval"]
        self.request_interval = CRAWLER_CONFIG["request_interval"]
    
    def search_by_polygon(self, polygon, keyword="", types=None, extensions="all"):
        """
        基于多边形边界搜索 POI 数据
        :param polygon: 多边形边界坐标，格式为 "lon1,lat1|lon2,lat2|...|lonN,latN"
        :param keyword: 搜索关键词，默认为空字符串
        :param types: POI 类型，可选
        :param extensions: 返回结果控制，"base" 或 "all"
        :return: POI 数据列表
        """
        # 尝试使用矩形边界格式
        # 提取第一个和第三个坐标作为矩形的左下角和右上角
        coords = polygon.split("|")
        if len(coords) >= 4:
            # 使用矩形边界格式: rectangle(左下角经度,左下角纬度;右上角经度,右上角纬度)
            boundary = f"rectangle({coords[0]};{coords[2]})"
            print(f"使用矩形边界: {boundary}")
            return self._search(boundary, keyword, types, extensions)
        else:
            # 构建多边形边界参数
            formatted_polygon = polygon.replace("|", ";")
            boundary = f"polygon({formatted_polygon})"
            print(f"使用多边形边界: {boundary}")
            return self._search(boundary, keyword, types, extensions)
    
    def search_by_file(self, file_path, keyword="", types=None, extensions="all"):
        """
        基于文件中的边界搜索 POI 数据
        :param file_path: 边界文件路径
        :param keyword: 搜索关键词，默认为空字符串
        :param types: POI 类型，可选
        :param extensions: 返回结果控制，"base" 或 "all"
        :return: POI 数据列表
        """
        # 加载边界
        polygon = self._load_boundary_from_file(file_path)
        if not polygon:
            print("边界加载失败，无法继续爬取")
            return []
        
        # 使用多边形边界搜索
        return self.search_by_polygon(polygon, keyword, types, extensions)
    
    def _search(self, boundary, keyword="", types=None, extensions="all"):
        """
        执行搜索
        :param boundary: 边界参数
        :param keyword: 搜索关键词，默认为空字符串
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
                "types": types,
                "extensions": extensions,
                "page": page,
                "offset": self.page_size,
                "output": "csv",
                "boundary": boundary
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
    
    def _load_boundary_from_file(self, file_path):
        """
        从文件中加载边界坐标
        :param file_path: 边界文件路径
        :return: 边界坐标字符串，格式为 "lon1,lat1|lon2,lat2|...|lonN,latN"
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # 支持 JSON 和文本格式
                if file_path.endswith('.json'):
                    data = json.load(f)
                    # 假设 JSON 格式为 {"coordinates": [[lon1, lat1], [lon2, lat2], ...]}
                    if "coordinates" in data:
                        coordinates = data["coordinates"]
                        # 转换为字符串格式
                        polygon = "|".join([f"{coord[0]},{coord[1]}" for coord in coordinates])
                        return polygon
                    else:
                        raise ValueError("JSON 文件格式不正确，缺少 'coordinates' 字段")
                else:
                    # 文本格式，每行一个坐标对，格式为 "lon,lat"
                    coordinates = []
                    for line in f:
                        line = line.strip()
                        if line:
                            coordinates.append(line)
                    return "|".join(coordinates)
        except Exception as e:
            print(f"加载边界文件失败: {e}")
            return None
    
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
