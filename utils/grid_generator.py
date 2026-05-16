"""
网格生成器

将大区域切分为小网格，用于网格化POI爬取
"""

from typing import List, Tuple, Optional, Dict
import math


class GridGenerator:
    """
    网格生成器

    将矩形或多边形区域切分为等大小的网格
    """

    DEFAULT_GRID_SIZE = 0.005

    def __init__(self,
                 min_lon: float,
                 min_lat: float,
                 max_lon: float,
                 max_lat: float,
                 grid_size: Optional[float] = None):
        """
        初始化网格生成器

        Args:
            min_lon: 最小经度
            min_lat: 最小纬度
            max_lon: 最大经度
            max_lat: 最大纬度
            grid_size: 网格大小（经纬度单位），默认为0.005
        """
        self.min_lon = min_lon
        self.min_lat = min_lat
        self.max_lon = max_lon
        self.max_lat = max_lat
        self.grid_size = grid_size or self.DEFAULT_GRID_SIZE

        self._validate_bounds()

    def _validate_bounds(self):
        """验证边界坐标的有效性"""
        if self.min_lon >= self.max_lon:
            raise ValueError(f"最小经度({self.min_lon})必须小于最大经度({self.max_lon})")
        if self.min_lat >= self.max_lat:
            raise ValueError(f"最小纬度({self.min_lat})必须小于最大纬度({self.max_lat})")

        if not (-180 <= self.min_lon <= 180 and -180 <= self.max_lon <= 180):
            raise ValueError("经度超出有效范围(-180到180)")
        if not (-90 <= self.min_lat <= 90 and -90 <= self.max_lat <= 90):
            raise ValueError("纬度超出有效范围(-90到90)")

    def generate_grids(self) -> List[str]:
        """
        生成网格列表

        Returns:
            网格字符串列表，格式为 "lon1,lat1|lon2,lat2"
        """
        grids = []

        lon = self.min_lon
        while lon < self.max_lon:
            lat = self.min_lat
            while lat < self.max_lat:
                grid_min_lon = round(lon, 6)
                grid_min_lat = round(lat, 6)
                grid_max_lon = round(min(lon + self.grid_size, self.max_lon), 6)
                grid_max_lat = round(min(lat + self.grid_size, self.max_lat), 6)

                grid_str = f"{grid_min_lon},{grid_min_lat}|{grid_max_lon},{grid_max_lat}"
                grids.append(grid_str)

                lat += self.grid_size
            lon += self.grid_size

        return grids

    def generate_grid_coords(self) -> List[Tuple[float, float, float, float]]:
        """
        生成网格坐标列表

        Returns:
            网格坐标元组列表，每个元素为 (min_lon, min_lat, max_lon, max_lat)
        """
        coords = []

        lon = self.min_lon
        while lon < self.max_lon:
            lat = self.min_lat
            while lat < self.max_lat:
                grid_min_lon = round(lon, 6)
                grid_min_lat = round(lat, 6)
                grid_max_lon = round(min(lon + self.grid_size, self.max_lon), 6)
                grid_max_lat = round(min(lat + self.grid_size, self.max_lat), 6)

                coords.append((grid_min_lon, grid_min_lat, grid_max_lon, grid_max_lat))

                lat += self.grid_size
            lon += self.grid_size

        return coords

    def get_grid_count(self) -> int:
        """
        获取网格总数

        Returns:
            网格数量
        """
        lon_count = math.ceil((self.max_lon - self.min_lon) / self.grid_size)
        lat_count = math.ceil((self.max_lat - self.min_lat) / self.grid_size)
        return lon_count * lat_count

    def get_grid_area(self) -> float:
        """
        获取网格覆盖的面积（近似值，单位：平方公里）

        Returns:
            面积
        """
        width = self.max_lon - self.min_lon
        height = self.max_lat - self.min_lat

        lat_mid = (self.min_lat + self.max_lat) / 2

        lon_km = width * 111.32 * math.cos(math.radians(lat_mid))
        lat_km = height * 110.574

        return lon_km * lat_km

    def get_grid_size_description(self) -> str:
        """
        获取网格大小的描述信息

        Returns:
            网格大小描述，如 "约500米 x 500米"
        """
        lat_km = self.grid_size * 110.574
        lon_km = self.grid_size * 111.32 * math.cos(math.radians(
            (self.min_lat + self.max_lat) / 2))

        return f"约{int(lat_km * 1000)}米 x {int(lon_km * 1000)}米"

    def get_progress_info(self) -> dict:
        """
        获取网格信息摘要

        Returns:
            包含网格统计信息的字典
        """
        return {
            "total_grids": self.get_grid_count(),
            "area_km2": round(self.get_grid_area(), 2),
            "grid_size": self.grid_size,
            "grid_size_desc": self.get_grid_size_description(),
            "bounds": {
                "min_lon": self.min_lon,
                "min_lat": self.min_lat,
                "max_lon": self.max_lon,
                "max_lat": self.max_lat
            }
        }

    @staticmethod
    def from_polygon_string(polygon_str: str, grid_size: Optional[float] = None) -> 'GridGenerator':
        """
        从多边形字符串创建网格生成器

        Args:
            polygon_str: 多边形字符串，格式为 "lon1,lat1|lon2,lat2"
            grid_size: 网格大小

        Returns:
            GridGenerator实例
        """
        coords = polygon_str.split("|")
        if len(coords) < 2:
            raise ValueError("多边形字符串至少需要两个坐标点")

        min_lons = []
        min_lats = []
        max_lons = []
        max_lats = []

        for coord in coords:
            lon, lat = map(float, coord.split(","))
            min_lons.append(lon)
            max_lons.append(lon)
            min_lats.append(lat)
            max_lats.append(lat)

        return GridGenerator(
            min_lon=min(min_lons),
            min_lat=min(min_lats),
            max_lon=max(max_lons),
            max_lat=max(max_lats),
            grid_size=grid_size
        )

    @staticmethod
    def from_bounds(min_lon: float, min_lat: float, max_lon: float, max_lat: float,
                   grid_size: Optional[float] = None) -> 'GridGenerator':
        """
        从边界坐标创建网格生成器

        Args:
            min_lon: 最小经度
            min_lat: 最小纬度
            max_lon: 最大经度
            max_lat: 最大纬度
            grid_size: 网格大小

        Returns:
            GridGenerator实例
        """
        return GridGenerator(min_lon, min_lat, max_lon, max_lat, grid_size)
