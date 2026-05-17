"""
ESRI Shapefile边界文件加载器

支持从Shapefile文件中加载地理边界数据
自动检测坐标系并转换到 WGS84 -> GCJ02
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
    自动处理坐标系转换：输入 -> WGS84 -> GCJ02
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
        self._gdf_wgs84 = None

    def load(self) -> bool:
        """
        加载Shapefile文件

        Returns:
            加载是否成功
        """
        try:
            import geopandas as gpd
            self._gdf = gpd.read_file(self.file_path)
            self._crs = str(self._gdf.crs).upper()
            self._gdf_wgs84 = self._gdf.to_crs(epsg=4326)
            return True
        except ImportError:
            raise ImportError("请安装geopandas库: pip install geopandas")
        except Exception as e:
            raise RuntimeError(f"加载Shapefile文件失败: {e}")

    def _ensure_loaded(self):
        """确保数据已加载"""
        if self._gdf is None:
            self.load()

    def detect_crs(self) -> str:
        """
        自动检测输入文件的坐标系

        Returns:
            坐标系描述字符串
        """
        self._ensure_loaded()
        
        crs_str = self._crs
        
        if "4326" in crs_str or "WGS84" in crs_str:
            return "WGS84 (EPSG:4326)"
        elif "4490" in crs_str or "CGCS2000" in crs_str or "2000" in crs_str:
            return "CGCS2000 (EPSG:4490)"
        elif "GCJ-02" in crs_str or "EPSG:4214" in crs_str:
            return "GCJ-02"
        elif "EPSG:3857" in crs_str or "WEB MERCATOR" in crs_str:
            return "Web Mercator (EPSG:3857)"
        else:
            return f"Unknown ({self._crs})"

    def get_bounds(self) -> Tuple[float, float, float, float]:
        """
        获取整体的边界框（原坐标系）

        Returns:
            (minx, miny, maxx, maxy) 边界框坐标
        """
        self._ensure_loaded()
        return self._gdf.total_bounds

    def get_wgs84_bounds(self) -> Tuple[float, float, float, float]:
        """
        获取WGS84坐标系下的边界框

        统一将输入坐标转换为 WGS84

        Returns:
            (minx, miny, maxx, maxy) 边界框坐标
        """
        self._ensure_loaded()
        return self._gdf_wgs84.total_bounds

    def get_gcj02_bounds(self) -> Tuple[float, float, float, float]:
        """
        获取GCJ-02坐标系下的边界框

        先转换为 WGS84，再转换为 GCJ-02
        高德地图使用 GCJ-02 坐标系

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

        自动检测坐标系并转换为 GCJ-02

        Returns:
            格式: "lon1,lat1|lon2,lat2|...|lonN,latN"
        """
        minx, miny, maxx, maxy = self.get_gcj02_bounds()
        return f"{minx},{miny}|{maxx},{maxy}"

    def get_wgs84_polygon(self) -> str:
        """
        获取WGS84坐标系的多边形字符串

        Returns:
            格式: "lon1,lat1|lon2,lat2|...|lonN,latN"
        """
        minx, miny, maxx, maxy = self.get_wgs84_bounds()
        return f"{minx},{miny}|{maxx},{maxy}"

    def get_all_boundaries(self) -> List[BoundaryInfo]:
        """
        获取所有边界的详细信息

        Returns:
            边界信息列表
        """
        self._ensure_loaded()

        boundaries = []

        for idx, row in self._gdf_wgs84.iterrows():
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
        """获取要素数量"""
        self._ensure_loaded()
        return len(self._gdf)

    def to_geojson(self, target_crs: str = "wgs84") -> str:
        """
        导出为GeoJSON格式

        Args:
            target_crs: 目标坐标系，"wgs84" 或 "gcj02"

        Returns:
            GeoJSON字符串
        """
        self._ensure_loaded()
        
        if target_crs.lower() == "gcj02":
            gdf_target = self._gdf_wgs84.copy()
        else:
            gdf_target = self._gdf_wgs84.copy()
        
        return gdf_target.to_json()


# ============================================================================
# 便捷函数
# ============================================================================

def load_boundary_from_file(file_path: str, target_crs: str = "gcj02") -> Tuple[float, float, float, float]:
    """
    便捷函数：从文件加载边界框

    Args:
        file_path: 文件路径
        target_crs: 目标坐标系，"gcj02" 或 "wgs84"

    Returns:
        (min_lon, min_lat, max_lon, max_lat) 边界框
    """
    loader = ShapefileLoader(file_path)
    
    if target_crs.lower() == "wgs84":
        return loader.get_wgs84_bounds()
    else:
        return loader.get_gcj02_bounds()


def load_polygon_string(file_path: str, target_crs: str = "gcj02") -> str:
    """
    便捷函数：从文件加载多边形字符串

    Args:
        file_path: 文件路径
        target_crs: 目标坐标系，"gcj02" 或 "wgs84"

    Returns:
        格式: "lon1,lat1|lon2,lat2"
    """
    loader = ShapefileLoader(file_path)
    
    if target_crs.lower() == "wgs84":
        return loader.get_wgs84_polygon()
    else:
        return loader.get_boundary_polygon()


def detect_file_crs(file_path: str) -> str:
    """
    便捷函数：检测文件坐标系

    Args:
        file_path: 文件路径

    Returns:
        坐标系描述字符串
    """
    loader = ShapefileLoader(file_path)
    return loader.detect_crs()
