"""
侧边栏配置组件
"""
import streamlit as st
import os
import tempfile
import zipfile
import io
from utils.poi_types import POI_TYPES, get_type_name
from utils.shapefile_loader import load_boundary_from_file, load_polygon_string


def extract_shapefile_from_zip(zip_bytes: bytes, temp_dir: str) -> str:
    """
    从 ZIP 压缩包中提取 Shapefile
    
    Args:
        zip_bytes: ZIP 文件字节数据
        temp_dir: 临时目录
        
    Returns:
        .shp 文件的完整路径
    """
    zip_path = os.path.join(temp_dir, "boundary.zip")
    with open(zip_path, "wb") as f:
        f.write(zip_bytes)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    
    shp_files = []
    for file in os.listdir(temp_dir):
        if file.lower().endswith('.shp'):
            shp_files.append(os.path.join(temp_dir, file))
    
    if not shp_files:
        raise ValueError("ZIP 压缩包中未找到 .shp 文件")
    
    return shp_files[0]


def render_sidebar():
    """渲染侧边栏配置面板"""
    st.sidebar.title("⚙️ 配置面板")
    
    # API Key
    st.sidebar.subheader("🔑 API Key")
    api_key = st.sidebar.text_input(
        "高德地图 API Key",
        type="password",
        help="获取地址: https://lbs.amap.com/"
    )
    
    # 边界来源
    st.sidebar.subheader("📐 边界来源")
    boundary_mode = st.sidebar.radio(
        "选择边界来源",
        ["加载边界文件", "手动输入坐标"],
        label_visibility="collapsed"
    )
    
    boundary_coords = None
    bounds = None
    
    if boundary_mode == "加载边界文件":
        st.sidebar.info("📁 支持格式：\n- GeoJSON (.geojson, .json)\n- Shapefile ZIP 压缩包（含 .shp/.shx/.dbf）")
        
        uploaded_file = st.sidebar.file_uploader(
            "上传边界文件",
            type=["geojson", "json", "zip"],
            help="GeoJSON 文件或 Shapefile ZIP 压缩包"
        )
        
        if uploaded_file:
            try:
                temp_dir = tempfile.mkdtemp()
                file_name = uploaded_file.name.lower()
                
                if file_name.endswith('.zip'):
                    st.sidebar.info("📦 检测到 Shapefile ZIP 压缩包，正在解压...")
                    temp_path = extract_shapefile_from_zip(
                        uploaded_file.getvalue(), 
                        temp_dir
                    )
                else:
                    temp_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                
                boundary_coords = load_polygon_string(temp_path, "gcj02")
                bounds = load_boundary_from_file(temp_path, "gcj02")
                
                st.sidebar.success(f"✅ 边界文件加载成功!")
                st.sidebar.info(f"📍 边界范围: 经度 {bounds[0]:.4f}~{bounds[2]:.4f}, 纬度 {bounds[1]:.4f}~{bounds[3]:.4f}")
                
            except Exception as e:
                st.sidebar.error(f"❌ 加载失败: {str(e)}")
    
    else:  # 手动输入坐标
        coords_text = st.sidebar.text_area(
            "输入多边形坐标",
            placeholder="lon1,lat1|lon2,lat2|lon3,lat3",
            help="格式: 经度1,纬度1|经度2,纬度2|...，至少需要2个点（矩形）"
        )
        
        if coords_text:
            try:
                boundary_coords = coords_text
                coords_list = [tuple(map(float, p.split(','))) 
                              for p in coords_text.split('|')]
                lons = [p[0] for p in coords_list]
                lats = [p[1] for p in coords_list]
                bounds = (min(lons), min(lats), max(lons), max(lats))
                
            except Exception as e:
                st.sidebar.error(f"❌ 坐标格式错误: {str(e)}")
    
    # POI 类型选择
    st.sidebar.subheader("🎯 POI 类型")
    all_types = list(POI_TYPES.keys())
    
    select_all = st.sidebar.checkbox("全选所有类型", value=False)
    
    if select_all:
        selected_types = all_types
    else:
        default_types = ["010000", "060000", "050000", "110000"]
        selected_types = st.sidebar.multiselect(
            "选择 POI 类型",
            options=all_types,
            default=default_types,
            format_func=get_type_name
        )
    
    # 爬取设置
    st.sidebar.subheader("⚙️ 爬取设置")
    
    grid_size = st.sidebar.slider(
        "网格大小",
        min_value=0.001,
        max_value=0.01,
        value=0.005,
        step=0.001,
        help="越小精度越高，但爬取时间越长"
    )
    
    request_interval = st.sidebar.slider(
        "请求间隔 (秒)",
        min_value=0.05,
        max_value=2.0,
        value=0.2,
        step=0.05,
        help="避免 QPS 超限"
    )
    
    keyword = st.sidebar.text_input(
        "关键词过滤 (可选)",
        placeholder="例如: 肯德基",
        help="只爬取名称包含关键词的 POI"
    )
    
    output_format = st.sidebar.selectbox(
        "输出格式",
        ["csv", "json"],
        index=0
    )
    
    config = {
        "api_key": api_key,
        "boundary_coords": boundary_coords,
        "bounds": bounds,
        "selected_types": selected_types,
        "grid_size": grid_size,
        "request_interval": request_interval,
        "keyword": keyword,
        "output_format": output_format
    }
    
    return config
