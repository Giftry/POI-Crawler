#!/usr/bin/env python3
# 测试文件

from crawlers.amap_crawler import AMapCrawler
from processors.data_processor import DataProcessor
from outputs.data_exporter import DataExporter

def test_crawler():
    """测试爬取组件"""
    print("测试爬取组件...")
    crawler = AMapCrawler()
    
    # 测试搜索功能
    print("测试搜索功能...")
    pois = crawler.search_poi(keyword="餐厅", city="北京", extensions="base")
    print(f"搜索结果数量: {len(pois)}")
    
    if pois:
        print("第一条结果:")
        print(pois[0])
    
    return pois

def test_processor(raw_pois):
    """测试数据处理组件"""
    print("\n测试数据处理组件...")
    processor = DataProcessor()
    
    # 测试数据处理功能
    processed_pois = processor.process_poi_data(raw_pois)
    print(f"处理后结果数量: {len(processed_pois)}")
    
    if processed_pois:
        print("第一条处理结果:")
        print(processed_pois[0])
    
    return processed_pois

def test_exporter(processed_pois):
    """测试数据输出组件"""
    print("\n测试数据输出组件...")
    exporter = DataExporter()
    
    # 测试导出功能
    export_path = exporter.export(processed_pois)
    print(f"导出文件路径: {export_path}")
    
    return export_path

def main():
    """主测试函数"""
    print("开始测试 POI 爬取工具...\n")
    
    # 测试爬取组件
    raw_pois = test_crawler()
    
    if raw_pois:
        # 测试数据处理组件
        processed_pois = test_processor(raw_pois)
        
        if processed_pois:
            # 测试数据输出组件
            test_exporter(processed_pois)
    
    print("\n测试完成！")

if __name__ == "__main__":
    main()
