"""
ESRI Shapefile边界文件加载器

支持从Shapefile文件中加载地理边界数据
"""

import os
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class BoundaryInfo:
    """边界信息数据类"""
    name: str
    bounds: Tuple[float, float, float, float]
    centroid: Tuple[float, float]
    coordinates: List[Tuple[float, float]]
    crs: str
    area: Optional[float] = None


class ShapefileLoader:
    """
    Shapefile边界文件加载器

    从ESRI Shapefile格式的文件中加载地理边界数据
    """

    def __init__(self, file_path: str):
        """
        初始化加载器

        Args:
            file_path: Shapefile文件路径
        """
        self.file_path = file_path
        self._gdf = None
        self._crs = None

    def load(self) -> bool:
        """
        加载Shapefile文件

        Returns:
            加载是否成功
        """
        try:
            import geopandas as gpd
            self._gdf = gpd.read_file(self.file_path)
            self._crs = self._gdf.crs
            return True
        except ImportError:
            raise ImportError("请安装geopandas库: pip install geopandas")
        except Exception as e:
            raise RuntimeError(f"加载Shapefile文件失败: {e}")

    def get_bounds(self) -> Tuple[float, float, float, float]:
        """
        获取整体的边界框

        Returns:
            (minx, miny, maxx, maxy) 边界框坐标
        """
        if self._gdf is None:
            self.load()

        return self._gdf.total_bounds

    def get_wgs84_bounds(self) -> Tuple[float, float, float, float]:
        """
        获取WGS84坐标系下的边界框

        Returns:
            (minx, miny, maxx, maxy) 边界框坐标
        """
        if self._gdf is None:
            self.load()

        gdf_wgs84 = self._gdf.to_crs(epsg=4326)
        return gdf_wgs84.total_bounds

    def get_gcj02_bounds(self) -> Tuple[float, float, float, float]:
        """
        获取GCJ-02坐标系下的边界框

        高德地图使用GCJ-02坐标系

        Returns:
            (minx, miny, maxx, maxy) 边界框坐标
        """
        from .coordinate_converter import wgs84_to_gcj02

        minx, miny, maxx, maxy = self.get_wgs84_bounds()

        min_gcj_lon, min_gcj_lat = wgs84_to_gcj02(minx, miny)
        max_gcj_lon, max_gcj_lat = wgs84_to_gcj02(maxx, maxy)

        return (min_gcj_lon, min_gcj_lat, max_gcj_lon, max_gcj_lat)

    def get_boundary_polygon(self) -> str:
        """
        获取边界多边形字符串（适用于高德API）

        Returns:
            格式: "lon1,lat1|lon2,lat2|...|lonN,latN"
        """
        minx, miny, maxx, maxy = self.get_gcj02_bounds()
        return f"{minx},{miny}|{maxx},{maxy}"

    def get_all_boundaries(self) -> List[BoundaryInfo]:
        """
        获取所有边界的详细信息

        Returns:
            边界信息列表
        """
        if self._gdf is None:
            self.load()

        boundaries = []
        gdf_wgs84 = self._gdf.to_crs(epsg=4326)

        for idx, row in gdf_wgs84.iterrows():
            geom = row.geometry

            if hasattr(row, 'name') and row['name']:
                name = str(row['name'])
            else:
                name = f"Boundary_{idx}"

            bounds = geom.bounds
            centroid = geom.centroid

            coords = []
            if hasattr(geom, 'exterior'):
                coords = [(float(pt[0]), float(pt[1])) 
                         for pt in geom.exterior.coords]
            elif hasattr(geom, 'coords'):
                coords = [(float(pt[0]), float(pt[1])) 
                         for pt in geom.coords]

            boundaries.append(BoundaryInfo(
                name=name,
                bounds=bounds,
                centroid=(float(centroid.x), float(centroid.y)),
                coordinates=coords,
                crs="EPSG:4326",
                area=geom.area if hasattr(geom, 'area') else None
            ))

        return boundaries

    def get_feature_count(self) -> int:
        """
        获取要素数量

        Returns:
            边界要素的数量
        """
        if self._gdf is None:
            self.load()
        return len(self._gdf)

    @property
    def crs(self) -> Optional[str]:
        """获取坐标系信息"""
        return str(self._crs) if self._crs else None

    @staticmethod
    def is_valid_shapefile(file_path: str) -> bool:
        """
        检查文件是否为有效的Shapefile

        Args:
            file_path: 文件路径

        Returns:
            是否为有效的Shapefile
        """
        if not os.path.exists(file_path):
            return False

        ext = os.path.splitext(file_path)[1].lower()
        return ext in ['.shp', '.json', '.geojson']


def load_boundary_from_file(file_path: str, 
                            target_crs: str = "gcj02") -> Tuple[float, float, float, float]:
    """
    便捷函数：从文件加载边界

    Args:
        file_path: 边界文件路径
        target_crs: 目标坐标系，"gcj02" 或 "wgs84"

    Returns:
        (minx, miny, maxx, maxy) 边界框坐标
    """
    loader = ShapefileLoader(file_path)

    if target_crs.lower() == "gcj02":
        return loader.get_gcj02_bounds()
    else:
        return loader.get_wgs84_bounds()


def load_polygon_string(file_path: str, target_crs: str = "gcj02") -> str:
    """
    便捷函数：加载边界并返回高德API格式字符串

    Args:
        file_path: 边界文件路径
        target_crs: 目标坐标系，"gcj02" 或 "wgs84"

    Returns:
        高德API格式的边界字符串
    """
    loader = ShapefileLoader(file_path)

    if target_crs.lower() == "gcj02":
        return loader.get_boundary_polygon()
    else:
        minx, miny, maxx, maxy = loader.get_wgs84_bounds()
        return f"{minx},{miny}|{maxx},{maxy}"
