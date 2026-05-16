"""
POI 爬取工具 - Streamlit Web 应用
"""
import streamlit as st
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.sidebar import render_sidebar
from app.map_viewer import render_map
from app.result_viewer import render_results
from app.crawl_worker import run_crawl


def main():
    st.set_page_config(
        page_title="POI 爬取工具",
        page_icon="📍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 标题
    st.title("📍 POI 爬取工具")
    st.markdown("基于高德地图 API 的多边形网格化 POI 爬取工具")
    
    # 侧边栏配置
    with st.sidebar:
        config = render_sidebar()
    
    # 主区域布局
    map_col, result_col = st.columns([3, 2])
    
    with map_col:
        st.subheader("🗺️ 地图显示")
        render_map(config)
        
        # 爬取控制（放在地图下方）
        st.subheader("🎮 爬取控制")
        run_crawl(config)
    
    with result_col:
        st.subheader("📋 爬取结果")
        render_results()


if __name__ == "__main__":
    main()
