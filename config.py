# 配置文件

# 高德地图 API 密钥（需要替换为实际的 API 密钥）
AMAP_API_KEY = "084c0d377f123b24c85061ee312fd0c5"

# 爬取配置
CRAWLER_CONFIG = {
    # 每页返回结果数（最大 25）
    "page_size": 25,
    # 最大重试次数
    "max_retries": 3,
    # 重试间隔（秒）
    "retry_interval": 2,
    # 请求间隔（秒），避免触发频率限制
    "request_interval": 1
}

# 爬取配置
CRAWLER_MODE = {
    # 爬取模式：'keyword' 或 'polygon'
    "mode": "polygon",
    # 关键词搜索配置
    "keyword_config": {
        "keyword": "餐厅",
        "city": "北京",
        "types": None
    },
    # 多边形搜索配置
    "polygon_config": {
        # 多边形边界坐标，格式为 "lon1,lat1|lon2,lat2|...|lonN,latN"
        "polygon": "116.3,39.9|116.4,39.9|116.4,40.0|116.3,40.0|116.3,39.9",
        # 边界文件路径（优先级高于 polygon）
        "boundary_file": None,
        "types": None
    }
}

# 数据输出配置
OUTPUT_CONFIG = {
    # 输出格式：'csv' 或 'json'
    "format": "csv",
    # 输出文件路径
    "output_dir": "output",
    # 输出文件名前缀
    "file_prefix": "poi_data"
}
