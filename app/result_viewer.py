"""
结果查看器组件
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from utils.poi_types import get_type_name, get_type_color


def setup_chinese_font():
    """设置中文字体"""
    chinese_fonts = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi', 'FangSong', 
                     'Arial Unicode MS', 'DejaVu Sans']
    
    try:
        system_fonts = [f.name for f in fm.fontManager.ttflist]
        
        for font in chinese_fonts:
            if font in system_fonts:
                plt.rcParams['font.sans-serif'] = [font]
                plt.rcParams['axes.unicode_minus'] = False
                return True
    except:
        pass
    
    plt.rcParams['axes.unicode_minus'] = False
    return False


setup_chinese_font()


def render_results():
    """渲染结果展示区域"""
    pois = st.session_state.get("pois", [])
    
    if not pois:
        st.info("暂无数据，请先爬取 POI。")
        return
    
    st.subheader("📊 统计概览")
    st.metric("总 POI 数量", len(pois))
    
    type_counts = {}
    for poi in pois:
        poi_type = poi.get("major_type", "190000")
        type_counts[poi_type] = type_counts.get(poi_type, 0) + 1
    
    view_mode = st.radio("查看模式", ["数据表格", "类型分布", "混合模式"], horizontal=True)
    
    if view_mode in ["数据表格", "混合模式"]:
        st.subheader("📋 数据表格")
        df = pd.DataFrame(pois)
        
        columns_available = [col for col in df.columns if col in [
            "name", "address", "type_name", "lon", "lat", "typecode", "adname", "pname"
        ]]
        
        default_cols = ["name", "address", "type_name", "lon", "lat"]
        selected_cols = st.multiselect(
            "选择要显示的列",
            columns_available,
            default=[c for c in default_cols if c in columns_available]
        )
        
        if selected_cols:
            st.dataframe(df[selected_cols], use_container_width=True)
    
    if view_mode in ["类型分布", "混合模式"]:
        st.subheader("📈 类型分布")
        if len(type_counts):
            fig, ax = plt.subplots(figsize=(10, 6))
            
            type_names = [get_type_name(t) for t in type_counts.keys()]
            colors = [get_type_color(t) for t in type_counts.keys()]
            values = list(type_counts.values())
            
            bars = ax.barh(type_names, values, color=colors)
            ax.invert_yaxis()
            ax.set_xlabel("数量", fontsize=11)
            ax.set_title("POI 类型分布", fontsize=13, fontweight='bold')
            
            for bar, v in zip(bars, values):
                ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, 
                       f"{v}", va='center', fontsize=10)
            
            plt.tight_layout()
            st.pyplot(fig)
    
    st.subheader("💾 导出数据")
    
    col1, col2 = st.columns(2)
    
    with col1:
        df = pd.DataFrame(pois)
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            "📥 导出 CSV",
            csv,
            "poi_data.csv",
            "text/csv",
            use_container_width=True
        )
    
    with col2:
        json_str = pd.DataFrame(pois).to_json(orient='records', force_ascii=False)
        st.download_button(
            "📥 导出 JSON",
            json_str,
            "poi_data.json",
            "application/json",
            use_container_width=True
        )
