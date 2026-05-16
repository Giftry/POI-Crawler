"""
POI爬虫配置文件

集中管理所有可配置的参数，支持灵活的自定义设置
"""

import os
from typing import List, Optional, Dict, Any
from pathlib import Path


BASE_DIR = Path(__file__).parent

AMAP_API_KEY = os.environ.get("AMAP_API_KEY", "084c0d377f123b24c85061ee312fd0c5")

CRAWLER_CONFIG = {
    "page_size": 25,
    "max_retries": 3,
    "retry_interval": 2,
    "request_interval": 0.2,
    "timeout": 30
}

CRAWLER_MODE = {
    "mode": "grid_polygon",
    "keyword_config": {
        "keyword": "",
        "city": "",
        "types": None
    },
    "polygon_config": {
        "polygon": "",
        "boundary_file": "",
        "types": None
    },
    "grid_polygon_config": {
        "polygon": "",
        "boundary_file": "",
        "types": None,
        "grid_size": 0.005,
        "keyword": ""
    }
}

OUTPUT_CONFIG = {
    "format": "csv",
    "output_dir": str(BASE_DIR / "outputs"),
    "file_prefix": "poi_data"
}

from utils.poi_types import POI_TYPES, get_all_type_codes


class GridPolygonConfig:
    """网格化多边形爬取配置类"""

    DEFAULT_GRID_SIZE = 0.005

    GRID_SIZE_OPTIONS = {
        "粗略 (0.01° ≈ 1km)": 0.01,
        "标准 (0.005° ≈ 500m)": 0.005,
        "精细 (0.002° ≈ 200m)": 0.002,
        "超精细 (0.001° ≈ 100m)": 0.001,
    }

    def __init__(self,
                 api_key: Optional[str] = None,
                 polygon: Optional[str] = None,
                 boundary_file: Optional[str] = None,
                 types: Optional[List[str]] = None,
                 grid_size: Optional[float] = None,
                 keyword: Optional[str] = None,
                 page_size: int = 25,
                 max_retries: int = 3,
                 retry_interval: float = 2.0,
                 request_interval: float = 0.2,
                 timeout: int = 30,
                 extensions: str = "all"):
        """
        初始化网格化多边形爬取配置

        Args:
            api_key: 高德地图API密钥
            polygon: 多边形边界坐标字符串，格式为 "lon1,lat1|lon2,lat2"
            boundary_file: 边界文件路径（支持Shapefile、GeoJSON）
            types: POI类型编码列表，None表示所有类型
            grid_size: 网格大小（经纬度单位），默认为0.005
            keyword: 搜索关键词
            page_size: 每页结果数，最大25
            max_retries: 最大重试次数
            retry_interval: 重试间隔（秒）
            request_interval: 请求间隔（秒），避免QPS限制
            timeout: 请求超时时间（秒）
            extensions: 返回结果控制，"base"或"all"
        """
        self.api_key = api_key or AMAP_API_KEY
        self.polygon = polygon
        self.boundary_file = boundary_file
        self.types = types
        self.grid_size = grid_size or self.DEFAULT_GRID_SIZE
        self.keyword = keyword
        self.page_size = min(page_size, 25)
        self.max_retries = max_retries
        self.retry_interval = retry_interval
        self.request_interval = request_interval
        self.timeout = timeout
        self.extensions = extensions

    def validate(self) -> List[str]:
        """
        验证配置的合法性

        Returns:
            错误信息列表，空列表表示配置合法
        """
        errors = []

        if not self.api_key:
            errors.append("API密钥不能为空")

        if not self.polygon and not self.boundary_file:
            errors.append("必须提供多边形坐标或边界文件")

        if self.polygon:
            try:
                coords = self.polygon.split("|")
                if len(coords) < 2:
                    errors.append("多边形坐标至少需要两个点")
                for coord in coords:
                    lon, lat = coord.split(",")
                    lon, lat = float(lon), float(lat)
                    if not (-180 <= lon <= 180):
                        errors.append(f"经度{lon}超出有效范围")
                    if not (-90 <= lat <= 90):
                        errors.append(f"纬度{lat}超出有效范围")
            except Exception as e:
                errors.append(f"多边形坐标格式错误: {e}")

        if self.boundary_file and not os.path.exists(self.boundary_file):
            errors.append(f"边界文件不存在: {self.boundary_file}")

        if self.grid_size <= 0 or self.grid_size > 0.1:
            errors.append(f"网格大小{self.grid_size}超出合理范围(0.001~0.1)")

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "api_key": self.api_key[:8] + "****" if self.api_key else None,
            "polygon": self.polygon,
            "boundary_file": self.boundary_file,
            "types": self.types,
            "grid_size": self.grid_size,
            "keyword": self.keyword,
            "page_size": self.page_size,
            "max_retries": self.max_retries,
            "retry_interval": self.retry_interval,
            "request_interval": self.request_interval,
            "timeout": self.timeout,
            "extensions": self.extensions
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GridPolygonConfig":
        """从字典创建配置"""
        return cls(**{k: v for k, v in data.items() if k in cls.__init__.__code__.co_varnames})

    @classmethod
    def from_env(cls) -> "GridPolygonConfig":
        """从环境变量创建配置"""
        return cls(
            api_key=os.environ.get("AMAP_API_KEY"),
            polygon=os.environ.get("AMAP_POLYGON"),
            boundary_file=os.environ.get("AMAP_BOUNDARY_FILE"),
            types=os.environ.get("AMAP_TYPES", "").split(",") if os.environ.get("AMAP_TYPES") else None,
            grid_size=float(os.environ.get("AMAP_GRID_SIZE", cls.DEFAULT_GRID_SIZE)),
            keyword=os.environ.get("AMAP_KEYWORD")
        )


class KeywordSearchConfig:
    """关键词搜索配置类"""

    def __init__(self,
                 api_key: Optional[str] = None,
                 keyword: str = "",
                 city: str = "",
                 types: Optional[str] = None,
                 page_size: int = 25,
                 max_retries: int = 3,
                 retry_interval: float = 2.0,
                 request_interval: float = 1.0,
                 timeout: int = 30,
                 extensions: str = "all"):
        """
        初始化关键词搜索配置

        Args:
            api_key: 高德地图API密钥
            keyword: 搜索关键词
            city: 城市名称或编码
            types: POI类型编码
            page_size: 每页结果数
            max_retries: 最大重试次数
            retry_interval: 重试间隔
            request_interval: 请求间隔
            timeout: 请求超时
            extensions: 返回结果控制
        """
        self.api_key = api_key or AMAP_API_KEY
        self.keyword = keyword
        self.city = city
        self.types = types
        self.page_size = min(page_size, 25)
        self.max_retries = max_retries
        self.retry_interval = retry_interval
        self.request_interval = request_interval
        self.timeout = timeout
        self.extensions = extensions

    def validate(self) -> List[str]:
        """验证配置合法性"""
        errors = []

        if not self.api_key:
            errors.append("API密钥不能为空")

        if not self.keyword:
            errors.append("搜索关键词不能为空")

        return errors


def get_default_grid_polygon_config() -> GridPolygonConfig:
    """获取默认的网格化多边形爬取配置"""
    return GridPolygonConfig(
        api_key=AMAP_API_KEY,
        grid_size=GridPolygonConfig.DEFAULT_GRID_SIZE,
        request_interval=CRAWLER_CONFIG["request_interval"]
    )


def get_output_path(file_prefix: str = None, format: str = "csv") -> str:
    """
    生成输出文件路径

    Args:
        file_prefix: 文件名前缀
        format: 输出格式

    Returns:
        完整的输出文件路径
    """
    import datetime

    prefix = file_prefix or OUTPUT_CONFIG["file_prefix"]
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.{format}"

    output_dir = OUTPUT_CONFIG["output_dir"]
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    return os.path.join(output_dir, filename)
