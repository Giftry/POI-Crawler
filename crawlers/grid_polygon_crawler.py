"""
基于网格的多边形POI爬虫

实现将大区域切分为小网格进行POI爬取的策略
"""

import requests
import time
import json
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .api_endpoints import AMAP_POLYGON_API_URL
from utils.grid_generator import GridGenerator
from utils.coordinate_converter import wgs84_to_gcj02


class CrawlerStatus(Enum):
    """爬虫状态枚举"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class CrawlerConfig:
    """爬虫配置类"""
    api_key: str
    grid_size: float = 0.005
    page_size: int = 25
    max_retries: int = 3
    retry_interval: float = 2.0
    request_interval: float = 0.2
    extensions: str = "all"
    timeout: int = 30


@dataclass
class CrawlerProgress:
    """爬虫进度信息"""
    total_grids: int = 0
    processed_grids: int = 0
    current_grid: str = ""
    total_pois: int = 0
    current_type: str = ""
    status: CrawlerStatus = CrawlerStatus.IDLE
    error_message: str = ""

    def get_progress_percentage(self) -> float:
        """获取进度百分比"""
        if self.total_grids == 0:
            return 0.0
        return (self.processed_grids / self.total_grids) * 100

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "total_grids": self.total_grids,
            "processed_grids": self.processed_grids,
            "current_grid": self.current_grid,
            "total_pois": self.total_pois,
            "current_type": self.current_type,
            "status": self.status.value,
            "progress": f"{self.get_progress_percentage():.1f}%",
            "error": self.error_message
        }


class GridPolygonCrawler:
    """
    基于网格的多边形POI爬虫

    将目标区域切分为小网格，对每个网格单独进行POI爬取，
    最后合并去重得到完整区域内的POI数据
    """

    def __init__(self, config: Optional[CrawlerConfig] = None, api_key: Optional[str] = None):
        """
        初始化爬虫

        Args:
            config: 爬虫配置，如果不提供则使用默认配置
            api_key: 高德地图 API Key（便捷初始化参数）
        """
        if api_key and not config:
            self.config = CrawlerConfig(api_key=api_key)
        else:
            self.config = config or CrawlerConfig(api_key="")
        self.progress = CrawlerProgress()
        self._is_paused = False
        self._is_stopped = False
        self._poi_buffer: List[Dict[str, Any]] = []
        self._seen_ids: set = set()
        self._progress_callback: Optional[Callable[[CrawlerProgress], None]] = None
    
    def search_by_rectangle(self, min_lon: float, min_lat: float, 
                          max_lon: float, max_lat: float,
                          types: Optional[str] = None,
                          keyword: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        基于矩形区域爬取POI（单次调用，不拆分网格）
        
        Args:
            min_lon: 最小经度
            min_lat: 最小纬度
            max_lon: 最大经度
            max_lat: 最大纬度
            types: POI类型编码
            keyword: 搜索关键词
            
        Returns:
            POI列表
        """
        grid_str = f"{min_lon:.6f},{min_lat:.6f}|{max_lon:.6f},{max_lat:.6f}"
        return self._fetch_pois_in_grid(grid_str, types, keyword)

    def set_progress_callback(self, callback: Callable[[CrawlerProgress], None]):
        """
        设置进度回调函数

        Args:
            callback: 进度更新回调函数
        """
        self._progress_callback = callback

    def _update_progress(self, **kwargs):
        """更新进度信息"""
        for key, value in kwargs.items():
            if hasattr(self.progress, key):
                setattr(self.progress, key, value)

        if self._progress_callback:
            self._progress_callback(self.progress)

    def _make_request(self, url: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        发送API请求（带重试机制）

        Args:
            url: 请求URL
            params: 请求参数

        Returns:
            响应数据，失败返回None
        """
        for attempt in range(self.config.max_retries):
            try:
                response = requests.get(
                    url,
                    params=params,
                    timeout=self.config.timeout
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "1":
                        return data
                    else:
                        print(f"API返回错误: {data.get('info', '未知错误')}")
                        return None
                else:
                    print(f"请求失败，状态码: {response.status_code}")

            except requests.exceptions.Timeout:
                print(f"请求超时 (尝试 {attempt + 1}/{self.config.max_retries})")
            except requests.exceptions.RequestException as e:
                print(f"请求异常: {e}")

            if attempt < self.config.max_retries - 1:
                print(f"等待 {self.config.retry_interval} 秒后重试...")
                time.sleep(self.config.retry_interval)

        return None

    def _fetch_pois_in_grid(self, grid: str, poi_type: Optional[str] = None,
                           keyword: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        在单个网格内爬取POI

        Args:
            grid: 网格坐标字符串
            poi_type: POI类型编码
            keyword: 搜索关键词

        Returns:
            POI列表
        """
        all_pois = []
        page = 1

        while True:
            params = {
                "key": self.config.api_key,
                "keywords": keyword or "",
                "types": poi_type or "",
                "polygon": grid,
                "offset": min(self.config.page_size, 25),
                "page": page,
                "extensions": self.config.extensions,
                "output": "json"
            }

            response = self._make_request(AMAP_POLYGON_API_URL, params)
            if not response:
                break

            pois = response.get("pois", [])
            current_count = len(pois)

            if current_count == 0:
                break

            all_pois.extend(pois)

            if current_count < self.config.page_size:
                break

            page += 1
            time.sleep(self.config.request_interval)

        return all_pois

    def _add_pois(self, pois: List[Dict[str, Any]]):
        """
        添加POI到缓冲区（自动去重）

        Args:
            pois: POI列表
        """
        for poi in pois:
            poi_id = poi.get("id", "")
            if poi_id and poi_id not in self._seen_ids:
                self._seen_ids.add(poi_id)
                self._poi_buffer.append(poi)
                self._update_progress(total_pois=len(self._poi_buffer))

    def search_by_boundary(self,
                          boundary: str,
                          poi_types: Optional[List[str]] = None,
                          keyword: Optional[str] = None,
                          grid_size: Optional[float] = None,
                          auto_convert_coords: bool = True) -> List[Dict[str, Any]]:
        """
        基于边界爬取POI

        Args:
            boundary: 边界坐标字符串，格式为 "lon1,lat1|lon2,lat2"
            poi_types: POI类型编码列表，None表示所有类型
            keyword: 搜索关键词
            grid_size: 网格大小，None表示使用配置中的默认值
            auto_convert_coords: 是否自动将WGS84坐标转换为GCJ-02

        Returns:
            爬取到的POI列表（已去重）
        """
        self._reset_state()

        coords = boundary.split("|")
        if len(coords) < 2:
            raise ValueError("边界坐标至少需要两个点")

        min_lon, min_lat = map(float, coords[0].split(","))
        max_lon, max_lat = map(float, coords[1].split(","))

        if auto_convert_coords:
            min_lon, min_lat = wgs84_to_gcj02(min_lon, min_lat)
            max_lon, max_lat = wgs84_to_gcj02(max_lon, max_lat)

        generator = GridGenerator(
            min_lon, min_lat, max_lon, max_lat,
            grid_size=grid_size or self.config.grid_size
        )

        grids = generator.generate_grids()
        grid_info = generator.get_progress_info()

        print(f"区域信息: {grid_info['area_km2']:.2f} 平方公里")
        print(f"网格大小: {grid_info['grid_size_desc']}")
        print(f"网格总数: {len(grids)}")

        self._update_progress(
            total_grids=len(grids),
            status=CrawlerStatus.RUNNING
        )

        types_to_fetch = poi_types if poi_types else [None]

        for poi_type in types_to_fetch:
            if self._is_stopped:
                break

            while self._is_paused:
                if self._is_stopped:
                    break
                time.sleep(0.5)

            if poi_type:
                from utils.poi_types import get_type_name
                type_name = get_type_name(poi_type)
                print(f"\n正在爬取类型: {type_name} ({poi_type})")
                self._update_progress(current_type=type_name)

            for idx, grid in enumerate(grids):
                if self._is_stopped:
                    break

                while self._is_paused:
                    if self._is_stopped:
                        break
                    time.sleep(0.5)

                self._update_progress(
                    processed_grids=idx + 1,
                    current_grid=grid
                )

                pois = self._fetch_pois_in_grid(grid, poi_type, keyword)
                self._add_pois(pois)

                if len(pois) > 0:
                    print(f"  网格 {idx + 1}/{len(grids)}: 获取 {len(pois)} 条")

                time.sleep(self.config.request_interval)

        self._update_progress(
            status=CrawlerStatus.COMPLETED if not self._is_stopped else CrawlerStatus.STOPPED
        )

        print(f"\n爬取完成！共获取 {len(self._poi_buffer)} 条不重复的POI数据")
        return self._poi_buffer

    def search_by_shapefile(self,
                           shapefile_path: str,
                           poi_types: Optional[List[str]] = None,
                           keyword: Optional[str] = None,
                           grid_size: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        基于Shapefile边界文件爬取POI

        Args:
            shapefile_path: Shapefile文件路径
            poi_types: POI类型编码列表
            keyword: 搜索关键词
            grid_size: 网格大小

        Returns:
            爬取到的POI列表
        """
        from utils.shapefile_loader import ShapefileLoader

        loader = ShapefileLoader(shapefile_path)
        boundary = loader.get_boundary_polygon()

        print(f"从Shapefile加载边界: {shapefile_path}")
        print(f"原始坐标系: {loader.crs}")

        return self.search_by_boundary(
            boundary=boundary,
            poi_types=poi_types,
            keyword=keyword,
            grid_size=grid_size,
            auto_convert_coords=False
        )

    def pause(self):
        """暂停爬取"""
        self._is_paused = True
        self._update_progress(status=CrawlerStatus.PAUSED)
        print("爬取已暂停")

    def resume(self):
        """继续爬取"""
        self._is_paused = False
        self._update_progress(status=CrawlerStatus.RUNNING)
        print("爬取已继续")

    def stop(self):
        """停止爬取"""
        self._is_stopped = True
        self._is_paused = False
        self._update_progress(status=CrawlerStatus.STOPPED)
        print("爬取已停止")

    def _reset_state(self):
        """重置爬虫状态"""
        self._is_paused = False
        self._is_stopped = False
        self._poi_buffer = []
        self._seen_ids = set()
        self.progress = CrawlerProgress()

    def get_results(self) -> List[Dict[str, Any]]:
        """获取当前已爬取的POI列表"""
        return self._poi_buffer.copy()

    def save_results(self, file_path: str, format: str = "json"):
        """
        保存爬取结果

        Args:
            file_path: 保存路径
            format: 保存格式，"json" 或 "csv"
        """
        if format == "json":
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self._poi_buffer, f, ensure_ascii=False, indent=2)
        elif format == "csv":
            import csv
            if not self._poi_buffer:
                return

            with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                fieldnames = list(self._poi_buffer[0].keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self._poi_buffer)

        print(f"结果已保存到: {file_path}")
