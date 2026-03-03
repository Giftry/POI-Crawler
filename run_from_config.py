#!/usr/bin/env python3
# 从配置文件运行爬取任务

from crawlers.keyword_crawler import KeywordCrawler
from crawlers.polygon_crawler import PolygonCrawler
from processors.data_processor import DataProcessor
from outputs.data_exporter import DataExporter
from config import CRAWLER_MODE

def main():
    """从配置文件运行爬取任务"""
    print("从配置文件运行爬取任务...")
    
    # 获取爬取模式
    mode = CRAWLER_MODE["mode"]
    print(f"爬取模式: {mode}")
    
    # 初始化数据处理器和导出器
    processor = DataProcessor()
    exporter = DataExporter()
    
    try:
        # 根据爬取模式执行相应的爬取
        if mode == "keyword":
            # 关键词搜索
            keyword_config = CRAWLER_MODE["keyword_config"]
            keyword = keyword_config["keyword"]
            city = keyword_config["city"]
            types = keyword_config["types"]
            
            print(f"关键词: {keyword}")
            print(f"城市: {city}")
            print(f"类型: {types or '无'}")
            
            # 初始化关键词爬取器
            crawler = KeywordCrawler()
            
            # 爬取数据
            print("\n正在从高德地图 API 获取数据...")
            raw_pois = crawler.search(
                keyword=keyword,
                city=city,
                types=types,
                extensions="all"
            )
        elif mode == "polygon":
            # 多边形搜索
            polygon_config = CRAWLER_MODE["polygon_config"]
            polygon = polygon_config["polygon"]
            boundary_file = polygon_config["boundary_file"]
            types = polygon_config["types"]
            
            # 初始化多边形爬取器
            crawler = PolygonCrawler()
            
            if boundary_file:
                print(f"边界文件: {boundary_file}")
                # 使用文件边界爬取
                raw_pois = crawler.search_by_file(
                    file_path=boundary_file,
                    keyword="餐厅",  # 添加关键词
                    types=types,
                    extensions="all"
                )
            else:
                print(f"多边形边界: {polygon}")
                # 使用多边形边界爬取
                raw_pois = crawler.search_by_polygon(
                    polygon=polygon,
                    keyword="餐厅",  # 添加关键词
                    types=types,
                    extensions="all"
                )
        else:
            print(f"不支持的爬取模式: {mode}")
            return
        
        if not raw_pois:
            print("未获取到 POI 数据")
            return
        
        print(f"成功获取 {len(raw_pois)} 条原始 POI 数据")
        
        # 处理数据
        print("\n正在处理数据...")
        processed_pois = processor.process_poi_data(raw_pois)
        print(f"成功处理 {len(processed_pois)} 条 POI 数据")
        
        # 导出数据
        print("\n正在导出数据...")
        export_path = exporter.export(processed_pois)
        
        print("\n爬取任务完成！")
        print(f"导出文件: {export_path}")
        
    except Exception as e:
        print(f"爬取过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
