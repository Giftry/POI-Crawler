"""
坐标系转换工具

实现WGS84与GCJ-02（火星坐标系）之间的转换
WGS84: GPS设备使用的标准坐标系
GCJ-02: 国测局制定的加密坐标系，国内地图服务使用
"""

from typing import Tuple, List, Optional
import math


def wgs84_to_gcj02(lon: float, lat: float) -> Tuple[float, float]:
    """
    将WGS84坐标转换为GCJ-02坐标

    Args:
        lon: WGS84经度
        lat: WGS84纬度

    Returns:
        Tuple[float, float]: GCJ-02经度和纬度
    """
    if out_of_china(lon, lat):
        return lon, lat

    dlat = transform_lat(lon - 105.0, lat - 35.0)
    dlon = transform_lon(lon - 105.0, lat - 35.0)
    radlat = lat / 180.0 * math.pi
    magic = math.sin(radlat)
    magic = 1 - 0.00669342162296594323 * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((6378245.0 * (1 - 0.00669342162296594323)) / (magic * sqrtmagic) * math.pi)
    dlon = (dlon * 180.0) / (6378245.0 / sqrtmagic * math.cos(radlat) * math.pi)
    mglat = lat + dlat
    mglon = lon + dlon
    return round(mglon, 8), round(mglat, 8)


def gcj02_to_wgs84(lon: float, lat: float) -> Tuple[float, float]:
    """
    将GCJ-02坐标转换为WGS84坐标（近似转换）

    注意：由于WGS84到GCJ-02的转换是不可逆的，
    此方法只能得到近似值，存在一定偏差

    Args:
        lon: GCJ-02经度
        lat: GCJ-02纬度

    Returns:
        Tuple[float, float]: WGS84经度和纬度（近似值）
    """
    if out_of_china(lon, lat):
        return lon, lat

    dlat = transform_lat(lon - 105.0, lat - 35.0)
    dlon = transform_lon(lon - 105.0, lat - 35.0)
    radlat = lat / 180.0 * math.pi
    magic = math.sin(radlat)
    magic = 1 - 0.00669342162296594323 * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((6378245.0 * (1 - 0.00669342162296594323)) / (magic * sqrtmagic) * math.pi)
    dlon = (dlon * 180.0) / (6378245.0 / sqrtmagic * math.cos(radlat) * math.pi)
    mglat = lat + dlat
    mglon = lon + dlon
    return round(lon * 2 - mglon, 8), round(lat * 2 - mglat, 8)


def transform_lat(lon: float, lat: float) -> float:
    ret = -100.0 + 2.0 * lon + 3.0 * lat + 0.2 * lat * lat + 0.1 * lon * lat + 0.2 * math.sqrt(abs(lon))
    ret += (20.0 * math.sin(6.0 * lon * math.pi) + 20.0 * math.sin(2.0 * lon * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * math.pi) + 40.0 * math.sin(lat / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * math.pi) + 320.0 * math.sin(lat * math.pi / 30.0)) * 2.0 / 3.0
    return ret


def transform_lon(lon: float, lat: float) -> float:
    ret = 300.0 + lon + 2.0 * lat + 0.1 * lon * lon + 0.1 * lon * lat + 0.1 * math.sqrt(abs(lon))
    ret += (20.0 * math.sin(6.0 * lon * math.pi) + 20.0 * math.sin(2.0 * lon * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lon * math.pi) + 40.0 * math.sin(lon / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lon / 12.0 * math.pi) + 300.0 * math.sin(lon / 30.0 * math.pi)) * 2.0 / 3.0
    return ret


def out_of_china(lon: float, lat: float) -> bool:
    """判断坐标是否在中国境外"""
    return not (72.004 < lon < 137.8347 and 0.8293 < lat < 55.8271)


def batch_convert(coords: List[Tuple[float, float]], 
                  to_gcj: bool = True) -> List[Tuple[float, float]]:
    """
    批量转换坐标

    Args:
        coords: 坐标列表，每个元素为 (经度, 纬度)
        to_gcj: True表示转换为GCJ-02，False表示转换为WGS84

    Returns:
        转换后的坐标列表
    """
    converter = wgs84_to_gcj02 if to_gcj else gcj02_to_wgs84
    return [converter(lon, lat) for lon, lat in coords]


def convert_boundary(coords: List[Tuple[float, float]], 
                   to_gcj: bool = True) -> str:
    """
    将边界坐标列表转换为高德API所需的字符串格式

    Args:
        coords: 边界坐标列表，每个元素为 (经度, 纬度)
        to_gcj: True表示转换为GCJ-02，False表示保持WGS84

    Returns:
        符合高德API格式的边界字符串
    """
    if to_gcj:
        converted = batch_convert(coords, to_gcj=True)
    else:
        converted = coords

    return "|".join([f"{lon},{lat}" for lon, lat in converted])

