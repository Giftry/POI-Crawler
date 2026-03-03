import argparse
import os
from crawlers.amap_crawler import AMapCrawler
from processors.data_processor import DataProcessor
from outputs.data_exporter import DataExporter

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="POI 爬取工具 - 从高德地图获取 POI 数据")
    parser.add_argument("--keyword", help="搜索关键词（使用城市搜索时必填）")
    parser.add_argument("--city", help="城市名称或城市编码（使用多边形边界时可选）")
    parser.add_argument("--types", help="POI 类型")
    parser.add_argument("--extensions", default="all", choices=["base", "all"], help="返回结果控制")
    parser.add_argument("--format", choices=["csv", "json"], help="输出格式")
    
    # 多边形爬取参数
    polygon_group = parser.add_mutually_exclusive_group()
    polygon_group.add_argument("--polygon", help="多边形边界坐标，格式为 'lon1,lat1|lon2,lat2|...|lonN,latN'")
    polygon_group.add_argument("--boundary-file", help="边界文件路径，支持 JSON 和文本格式")
    
    args = parser.parse_args()
    
    # 检查参数合法性
    if not args.city and not args.polygon and not args.boundary_file:
        parser.error("必须指定城市或多边形边界或边界文件")
    
    # 检查城市搜索时是否提供了关键词
    if args.city and not args.keyword:
        parser.error("使用城市搜索时必须提供关键词")
    
    print(f"开始爬取 POI 数据...")
    if args.city:
        print(f"关键词: {args.keyword}")
        print(f"城市: {args.city}")
    if args.polygon:
        print(f"多边形边界: {args.polygon}")
    if args.boundary_file:
        print(f"边界文件: {args.boundary_file}")
    print(f"类型: {args.types or '无'}")
    print(f"返回结果控制: {args.extensions}")
    
    # 初始化组件
    crawler = AMapCrawler()
    processor = DataProcessor()
    exporter = DataExporter()
    
    try:
        # 爬取数据
        print("\n正在从高德地图 API 获取数据...")
        
        if args.polygon:
            # 使用多边形边界爬取（不使用关键词）
            raw_pois = crawler.search_poi_by_polygon(
                polygon=args.polygon,
                types=args.types,
                extensions=args.extensions
            )
        elif args.boundary_file:
            # 检查文件是否存在
            if not os.path.exists(args.boundary_file):
                print(f"边界文件不存在: {args.boundary_file}")
                return
            # 使用文件边界爬取（不使用关键词）
            raw_pois = crawler.search_poi_by_file(
                file_path=args.boundary_file,
                types=args.types,
                extensions=args.extensions
            )
        else:
            # 使用城市爬取（使用关键词）
            raw_pois = crawler.search_poi(
                keyword=args.keyword,
                city=args.city,
                types=args.types,
                extensions=args.extensions
            )
        
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
