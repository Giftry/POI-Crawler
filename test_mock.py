#!/usr/bin/env python3
# 模拟数据测试文件

from processors.data_processor import DataProcessor
from outputs.data_exporter import DataExporter

# 模拟 POI 数据
mock_pois = [
    {
        "id": "B000A83C6X",
        "name": "全聚德烤鸭店",
        "type": "餐饮服务;中餐厅;北京菜",
        "typecode": "050101",
        "location": "116.407413,39.914789",
        "address": "北京市东城区前门大街30号",
        "tel": "010-67011379",
        "pname": "北京市",
        "cityname": "北京市",
        "adname": "东城区",
        "business_area": "前门",
        "shopinfo": "1",
        "distance": "1000",
        "photos": [
            {"url": "https://example.com/photo1.jpg"},
            {"url": "https://example.com/photo2.jpg"}
        ],
        "biz_ext": {
            "rating": "4.5",
            "cost": "150"
        }
    },
    {
        "id": "B000A83C6Y",
        "name": "海底捞火锅",
        "type": "餐饮服务;中餐厅;火锅",
        "typecode": "050102",
        "location": "116.417413,39.924789",
        "address": "北京市朝阳区建国路88号",
        "tel": "010-67011380",
        "pname": "北京市",
        "cityname": "北京市",
        "adname": "朝阳区",
        "business_area": "国贸",
        "shopinfo": "1",
        "distance": "2000",
        "photos": [
            {"url": "https://example.com/photo3.jpg"}
        ],
        "biz_ext": {
            "rating": "4.8",
            "cost": "120"
        }
    }
]

def test_processor():
    """测试数据处理组件"""
    print("测试数据处理组件...")
    processor = DataProcessor()
    
    # 测试数据处理功能
    processed_pois = processor.process_poi_data(mock_pois)
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
    print("开始测试 POI 爬取工具（模拟数据）...\n")
    
    # 测试数据处理组件
    processed_pois = test_processor()
    
    if processed_pois:
        # 测试数据输出组件
        test_exporter(processed_pois)
    
    print("\n测试完成！")

if __name__ == "__main__":
    main()
