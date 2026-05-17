"""
后台爬取任务处理
"""
import streamlit as st
import time
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawlers.grid_polygon_crawler import GridPolygonCrawler
from utils.poi_types import POI_TYPES, get_type_name
from utils.coordinate_converter import gcj02_to_wgs84


def run_crawl(config):
    """执行爬取任务
    
    Args:
        config: 配置字典
    """
    if not config.get("api_key"):
        st.error("请先输入 API Key！")
        return
    
    if not config.get("boundary_coords"):
        st.error("请先设置边界！")
        return
    
    if not config.get("selected_types"):
        st.error("请至少选择一种 POI 类型！")
        return
    
    # 初始化状态
    if "pois" not in st.session_state:
        st.session_state.pois = []
    if "crawling" not in st.session_state:
        st.session_state.crawling = False
    if "should_stop" not in st.session_state:
        st.session_state.should_stop = False
    
    # 按钮
    col1, col2 = st.columns([1, 1])
    
    with col1:
        start_button = st.button("🚀 开始爬取", type="primary", use_container_width=True)
    
    with col2:
        stop_button = st.button("⏹️ 停止", use_container_width=True)
    
    if stop_button:
        st.session_state.should_stop = True
        st.session_state.crawling = False
    
    if start_button and not st.session_state.crawling:
        st.session_state.crawling = True
        st.session_state.should_stop = False
        st.session_state.pois = []
        
        # 进度显示区域
        progress_bar = st.progress(0)
        status_text = st.empty()
        stats_text = st.empty()
        
        try:
            # 创建爬虫
            crawler = GridPolygonCrawler(
                api_key=config["api_key"])
            
            # 计算网格
            from utils.grid_generator import GridGenerator
            bounds = config["bounds"]
            grid_gen = GridGenerator(
                bounds[0], bounds[1], bounds[2], bounds[3],
                grid_size=config["grid_size"]
            )
            grids = grid_gen.generate_grid_coords()  # 返回 (min_lon, min_lat, max_lon, max_lat) 元组列表
            total_grids = len(grids)
            
            all_pois = []
            
            status_text.text(f"开始爬取，共 {total_grids} 个网格，{len(config['selected_types'])} 种类型...")
            
            # 逐个类型爬取
            for type_idx, poi_type in enumerate(config["selected_types"]):
                type_name = get_type_name(poi_type)
                
                if st.session_state.should_stop:
                    break
                
                for grid_idx, grid in enumerate(grids):
                    if st.session_state.should_stop:
                        break
                    
                    # 进度
                    overall_progress = type_idx * len(grids) + grid_idx
                    overall_total = len(config["selected_types"]) * len(grids)
                    
                    progress_bar.progress(min(overall_progress / overall_total, 1.0))
                    status_text.text(f"正在爬取: {type_name} - 网格 {grid_idx + 1}/{len(grids)}")
                    
                    # 爬取当前网格
                    try:
                        results = crawler.search_by_rectangle(
                            min_lon=grid[0],
                            min_lat=grid[1],
                            max_lon=grid[2],
                            max_lat=grid[3],
                            types=poi_type,
                            keyword=config.get("keyword")
                        )
                        
                        # 处理结果
                        for poi in results:
                            location = poi.get("location", "")
                            if location and "," in location:
                                gcj_lon, gcj_lat = map(float, location.split(","))
                                # 保存原始高德坐标(GCJ02)作为主坐标，用于导出)
                                poi["lon"] = gcj_lon
                                poi["lat"] = gcj_lat
                                # 同时保存用于WGS84用于可视化
                                wgs_lon, wgs_lat = gcj02_to_wgs84(gcj_lon, gcj_lat)
                                poi["lon_wgs"] = wgs_lon
                                poi["lat_wgs"] = wgs_lat
                                poi["major_type"] = poi_type
                                poi["type_name"] = type_name
                                all_pois.append(poi)
                        
                        # 更新 session 状态
                        st.session_state.pois = all_pois.copy()
                        
                        # 更新统计
                        type_counts = {}
                        for p in all_pois:
                            t = p.get("major_type", "190000")
                            type_counts[t] = type_counts.get(t, 0) + 1
                        
                        stats_str = f"已爬取: {len(all_pois)} 条 | "
                        stats_str += " | ".join([f"{get_type_name(k)}: {v}" 
                                               for k, v in list(type_counts.items())[:3]])
                        if len(type_counts) > 3:
                            stats_str += " | ..."
                        
                        stats_text.text(stats_str)
                        
                        # 间隔
                        time.sleep(config["request_interval"])
                        
                    except Exception as e:
                            continue
            
            # 去重
            unique_pois = []
            seen_ids = set()
            for poi in all_pois:
                poi_id = poi.get("id", "")
                if poi_id and poi_id not in seen_ids:
                    seen_ids.add(poi_id)
                    unique_pois.append(poi)
            
            st.session_state.pois = unique_pois
            
            # 完成
            progress_bar.progress(1.0)
            status_text.text(f"✅ 爬取完成！共 {len(unique_pois)} 条 POI")
            st.balloons()
            
        except Exception as e:
            st.error(f"爬取失败: {str(e)}")
        finally:
            st.session_state.crawling = False
