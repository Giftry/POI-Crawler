"""
地图查看器组件（简化版，不需要 streamlit-folium）
"""
import streamlit as st
import folium
from streamlit.components.v1 import html
from utils.poi_types import get_type_color, get_type_name


def render_map(config):
    """渲染地图组件
    
    Args:
        config: 配置字典，包含 bounds 和边界信息
    """
    # 计算中心点
    if config.get("bounds"):
        min_lon, min_lat, max_lon, max_lat = config["bounds"]
        center_lat = (min_lat + max_lat) / 2
        center_lon = (min_lon + max_lon) / 2
        zoom_start = 12
    else:
        # 默认位置（长沙）
        center_lat = 28.2
        center_lon = 112.9
        zoom_start = 11
    
    # 创建地图
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_start,
        tiles="OpenStreetMap"
    )
    
    # 绘制边界
    if config.get("bounds"):
        min_lon, min_lat, max_lon, max_lat = config["bounds"]
        boundary_coords = [
            [min_lat, min_lon],
            [max_lat, min_lon],
            [max_lat, max_lon],
            [min_lat, max_lon],
            [min_lat, min_lon]
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
    
    # 绘制 POI 点
    pois = st.session_state.get("pois", [])
    if pois:
        for poi in pois:
            try:
                lat = poi.get("lat")
                lon = poi.get("lon")
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
