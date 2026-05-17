"""
地图查看器组件（简化版，不需要 streamlit-folium）
"""
import streamlit as st
import folium
from streamlit.components.v1 import html
from utils.poi_types import get_type_color, get_type_name
from utils.coordinate_converter import gcj02_to_wgs84


def render_map(config):
    """渲染地图组件
    
    Args:
        config: 配置字典，包含 bounds 和边界信息
    """
    # 计算中心点
    if config.get("bounds"):
        # 边界是 GCJ02，需要转换为 WGS84 用于显示
        gcj_min_lon, gcj_min_lat, gcj_max_lon, gcj_max_lat = config["bounds"]
        # 转换边界
        wgs_min_lon, wgs_min_lat = gcj02_to_wgs84(gcj_min_lon, gcj_min_lat)
        wgs_max_lon, wgs_max_lat = gcj02_to_wgs84(gcj_max_lon, gcj_max_lat)
        
        center_lat = (wgs_min_lat + wgs_max_lat) / 2
        center_lon = (wgs_min_lon + wgs_max_lon) / 2
        zoom_start = 12
    else:
        # 默认位置（长沙）
        center_lat = 28.2
        center_lon = 112.9
        wgs_min_lon, wgs_min_lat, wgs_max_lon, wgs_max_lat = None, None, None, None
        zoom_start = 11
    
    # 创建地图
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_start,
        tiles="OpenStreetMap"
    )
    
    # 绘制边界（使用转换后的 WGS84 坐标）
    if config.get("bounds") and wgs_min_lon is not None:
        boundary_coords = [
            [wgs_min_lat, wgs_min_lon],
            [wgs_max_lat, wgs_min_lon],
            [wgs_max_lat, wgs_max_lon],
            [wgs_min_lat, wgs_max_lon],
            [wgs_min_lat, wgs_min_lon]
        ]
        
        folium.Polygon(
            locations=boundary_coords,
            color="red",
            weight=3,
            fill=True,
            fill_color="red",
            fill_opacity=0.1,
            popup="爬取边界"
        ).add_to(m)
    
    # 绘制 POI 点（使用 WGS84 坐标）
    pois = st.session_state.get("pois", [])
    if pois:
        for poi in pois:
            try:
                # 优先使用 WGS84 坐标
                lat = poi.get("lat_wgs")
                lon = poi.get("lon_wgs")
                # 如果没有 WGS84，尝试转换
                if lat is None or lon is None:
                    gcj_lat = poi.get("lat")
                    gcj_lon = poi.get("lon")
                    if gcj_lon and gcj_lat:
                        lon, lat = gcj02_to_wgs84(gcj_lon, gcj_lat)
                
                name = poi.get("name", "未知")
                poi_type = poi.get("major_type", "190000")
                type_name = poi.get("type_name", "未知")
                address = poi.get("address", "")
                
                color = get_type_color(poi_type)
                
                # 弹出信息
                popup_text = f"<b>{name}</b><br>"
                if type_name:
                    popup_text += f"类型: {type_name}<br>"
                if address:
                    popup_text += f"地址: {address}"
                
                if lon and lat:
                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=5,
                        color=color,
                        fill=True,
                        fill_color=color,
                        fill_opacity=0.7,
                        popup=folium.Popup(popup_text, max_width=300)
                    ).add_to(m)
                
            except Exception:
                continue
    
    # 显示地图 - 直接用 HTML 显示
    map_html = m._repr_html_()
    html(map_html, height=600, scrolling=True)
