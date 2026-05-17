"""
快速测试 Streamlit 应用的基本功能
"""
import streamlit as st
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_app():
    st.set_page_config(page_title="POI 测试", layout="wide")
    st.title("🧪 测试 Streamlit 环境")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("依赖检查")
        
        dependencies = ["streamlit", "folium", "requests", "pandas", 
                      "matplotlib", "geopandas", "coord_convert"]
        
        for dep in dependencies:
            try:
                __import__(dep)
                st.success(f"✅ {dep}")
            except ImportError:
                st.error(f"❌ {dep} (未安装)")
    
    with col2:
        st.subheader("测试数据")
        # 创建一些模拟 POI
        test_pois = [
            {"name": "测试点1", "lat": 28.20, "lon": 112.90, "major_type": "010000", "type_name": "餐饮服务"},
            {"name": "测试点2", "lat": 28.21, "lon": 112.91, "major_type": "060000", "type_name": "购物服务"},
            {"name": "测试点3", "lat": 28.205, "lon": 112.915, "major_type": "050000", "type_name": "风景名胜"}
        ]
        
        if "pois" not in st.session_state:
            st.session_state.pois = test_pois
        
        # 显示测试数据
        st.dataframe(st.session_state.pois)
    
    st.subheader("地图测试")
    
    # 测试地图
    import folium
    from streamlit.components.v1 import html
    
    m = folium.Map(location=[28.20, 112.90], zoom_start=13)
    
    # 添加边界
    bounds = [112.88, 28.18, 112.94, 28.24]
    boundary_coords = [
        [bounds[1], bounds[0]],
        [bounds[3], bounds[0]],
        [bounds[3], bounds[2]],
        [bounds[1], bounds[2]],
        [bounds[1], bounds[0]]
    ]
    folium.Polygon(boundary_coords, color="red", fill=True, fill_opacity=0.1).add_to(m)
    
    # 添加测试点
    for poi in test_pois:
        folium.CircleMarker(
            location=[poi["lat"], poi["lon"]],
            radius=8,
            popup=poi["name"],
            color="blue"
        ).add_to(m)
    
    html(m._repr_html_(), height=500)
    
    st.success("🎉 测试环境运行正常！")


if __name__ == "__main__":
    test_app()
