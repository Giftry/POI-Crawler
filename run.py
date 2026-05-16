"""
POI爬取主入口

提供统一的命令行接口，支持多种爬取模式
"""

import argparse
import sys
import os
from typing import Optional, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import AMAP_API_KEY, OUTPUT_CONFIG, get_output_path, GridPolygonConfig
from crawlers.grid_polygon_crawler import GridPolygonCrawler, CrawlerConfig, CrawlerStatus
from utils.poi_types import POI_TYPES, get_type_name, get_all_type_codes
from utils.shapefile_loader import ShapefileLoader
from utils.coordinate_converter import wgs84_to_gcj02


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="POI爬取工具 - 基于高德地图API的网格化多边形POI爬取",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 使用Shapefile边界爬取所有POI
  python run.py --boundary-file inputs/boundary/调研边界.shp

  # 使用多边形坐标爬取，指定网格大小
  python run.py --polygon "116.3,39.9|116.5,40.0" --grid-size 0.005

  # 只爬取餐饮和购物类型的POI
  python run.py --boundary-file inputs/boundary/调研边界.shp --types 010000 --types 060000

  # 指定API密钥和输出格式
  python run.py --boundary-file inputs/boundary/调研边界.shp --api-key YOUR_KEY --format json

  # 使用关键词过滤
  python run.py --boundary-file inputs/boundary/调研边界.shp --keyword "餐厅"

网格大小说明:
  0.01°  ≈ 1公里    (粗略)
  0.005° ≈ 500米    (标准)
  0.002° ≈ 200米    (精细)
  0.001° ≈ 100米    (超精细)

POI类型编码:
  010000 - 餐饮     020000 - 住宿     030000 - 交通设施
  040000 - 金融     050000 - 旅游景点  060000 - 购物
  070000 - 生活服务 080000 - 体育休闲  090000 - 医疗保健
  100000 - 科教文化 110000 - 公司企业  120000 - 政府机构
        """
    )

    parser.add_argument("--api-key", "-k",
                       default=AMAP_API_KEY,
                       help="高德地图API密钥 (默认: 使用配置文件中的密钥)")

    boundary_group = parser.add_mutually_exclusive_group(required=True)
    boundary_group.add_argument("--polygon", "-p",
                               help="多边形边界坐标，格式: 'lon1,lat1|lon2,lat2'")
    boundary_group.add_argument("--boundary-file", "-b", "-f",
                               help="边界文件路径 (支持Shapefile、GeoJSON、JSON格式)")

    parser.add_argument("--types", "-t", action="append",
                       dest="poi_types",
                       help="POI类型编码，可指定多个 (使用 --types 010000 --types 060000)")

    parser.add_argument("--all-types", action="store_true",
                       help="爬取所有类型的POI")

    parser.add_argument("--grid-size", "-g", type=float,
                       default=0.005,
                       help="网格大小，单位为经纬度度数 (默认: 0.005，约500米)")

    parser.add_argument("--keyword", "-w",
                       help="搜索关键词，用于过滤POI")

    parser.add_argument("--format", "-o", choices=["csv", "json"],
                       default=OUTPUT_CONFIG["format"],
                       help="输出文件格式 (默认: csv)")

    parser.add_argument("--output", dest="output_file",
                       help="输出文件路径 (默认: 自动生成)")

    parser.add_argument("--list-types", action="store_true",
                       help="列出所有可用的POI类型编码")

    parser.add_argument("--no-convert", action="store_true",
                       help="不自动转换坐标系 (坐标已是GCJ-02时使用)")

    parser.add_argument("--page-size", type=int, default=25,
                       help="每页结果数，最大25 (默认: 25)")

    parser.add_argument("--request-interval", type=float, default=0.2,
                       help="请求间隔（秒），避免QPS限制 (默认: 0.2)")

    parser.add_argument("--no-visualize", action="store_true",
                       help="禁用可视化图片生成")

    return parser.parse_args()


def list_poi_types():
    """列出所有POI类型"""
    print("\n可用的POI类型编码:")
    print("-" * 40)
    print(f"{'编码':<10} {'类型名称':<15}")
    print("-" * 40)
    for code, name in POI_TYPES.items():
        print(f"{code:<10} {name:<15}")
    print("-" * 40)
    print(f"\n可使用 --types 参数指定一个或多个类型，")
    print(f"例如: --types 010000 --types 060000")


def get_boundary_info(boundary_file: str = None, polygon: str = None) -> dict:
    """
    获取边界信息

    Args:
        boundary_file: 边界文件路径
        polygon: 多边形坐标字符串

    Returns:
        边界信息字典
    """
    info = {}

    if boundary_file:
        if not os.path.exists(boundary_file):
            raise FileNotFoundError(f"边界文件不存在: {boundary_file}")

        ext = os.path.splitext(boundary_file)[1].lower()
        if ext in ['.shp', '.json', '.geojson']:
            loader = ShapefileLoader(boundary_file)
            gcj_bounds = loader.get_gcj02_bounds()
            wgs_bounds = loader.get_wgs84_bounds()

            info = {
                "type": "file",
                "file_path": boundary_file,
                "file_type": ext,
                "crs": loader.crs,
                "bounds_gcj02": gcj_bounds,
                "bounds_wgs84": wgs_bounds,
                "polygon_string": loader.get_boundary_polygon(),
                "feature_count": loader.get_feature_count()
            }
        else:
            with open(boundary_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content.startswith('[') or content.startswith('{'):
                    import json
                    data = json.loads(content)
                    if 'coordinates' in data:
                        coords = data['coordinates']
                        polygon = "|".join([f"{c[0]},{c[1]}" for c in coords])
                        info = {
                            "type": "geojson",
                            "polygon_string": polygon
                        }
                else:
                    info = {
                        "type": "text",
                        "polygon_string": content
                    }

    elif polygon:
        info = {
            "type": "polygon",
            "polygon_string": polygon
        }

    return info


def run_crawler(args):
    """执行爬取任务"""
    print("=" * 60)
    print("POI爬取工具 - 网格化多边形爬取")
    print("=" * 60)

    api_key = args.api_key
    if not api_key:
        print("错误: 未提供API密钥")
        print("请通过 --api-key 参数提供，或在config.py中设置 AMAP_API_KEY")
        return 1

    polygon = args.polygon
    boundary_file = args.boundary_file

    boundary_info = get_boundary_info(boundary_file, polygon)
    print(f"\n边界信息来源: {boundary_info['type']}")

    if 'file_path' in boundary_info:
        print(f"文件路径: {boundary_info['file_path']}")
        print(f"原始坐标系: {boundary_info.get('crs', '未知')}")
        print(f"特征数量: {boundary_info.get('feature_count', 1)}")

    polygon = boundary_info.get('polygon_string', polygon)
    print(f"多边形坐标: {polygon[:50]}..." if len(polygon) > 50 else f"多边形坐标: {polygon}")

    poi_types = None
    if args.all_types:
        poi_types = None
        print("\n爬取类型: 全部类型")
    elif args.poi_types:
        poi_types = args.poi_types
        type_names = [get_type_name(t) for t in poi_types]
        print(f"\n爬取类型: {', '.join(type_names)}")
    else:
        print("\n爬取类型: 全部类型 (未指定)")

    print(f"\n网格大小: {args.grid_size}°")
    print(f"  约 {args.grid_size * 111.32 * 1000:.0f}米 x {args.grid_size * 111.32 * 1000:.0f}米")

    if args.keyword:
        print(f"关键词过滤: {args.keyword}")

    print(f"请求间隔: {args.request_interval}秒")
    print(f"输出格式: {args.format}")

    config = GridPolygonConfig(
        api_key=api_key,
        polygon=polygon,
        boundary_file=boundary_file,
        types=poi_types,
        grid_size=args.grid_size,
        keyword=args.keyword,
        page_size=args.page_size,
        request_interval=args.request_interval
    )

    errors = config.validate()
    if errors:
        print("\n配置错误:")
        for error in errors:
            print(f"  - {error}")
        return 1

    crawler_config = CrawlerConfig(
        api_key=config.api_key,
        grid_size=config.grid_size,
        page_size=config.page_size,
        request_interval=config.request_interval
    )

    crawler = GridPolygonCrawler(crawler_config)

    print("\n" + "-" * 60)
    print("开始爬取...")
    print("-" * 60 + "\n")

    try:
        results = crawler.search_by_boundary(
            boundary=config.polygon or polygon,
            poi_types=config.types,
            keyword=config.keyword,
            grid_size=config.grid_size,
            auto_convert_coords=not args.no_convert
        )

        if not results:
            print("\n未获取到任何POI数据")
            return 1

        print(f"\n成功获取 {len(results)} 条POI数据")

        output_format = args.format or OUTPUT_CONFIG["format"]
        output_file = args.output_file or get_output_path(
            file_prefix="poi_data",
            format=output_format
        )

        from processors.data_processor import DataProcessor
        from outputs.data_exporter import DataExporter

        processor = DataProcessor()
        processed_results = processor.process_poi_data(results)

        exporter = DataExporter()
        if output_format == "json":
            exporter._export_json(processed_results)
        else:
            exporter._export_csv(processed_results)

        print(f"\n数据已保存到: {output_file}")

        if not args.no_visualize:
            try:
                from utils.visualizer import visualize_crawl_results

                boundary_coords = config.polygon or polygon
                bounds = None
                if boundary_coords:
                    coords = boundary_coords.split("|")
                    if len(coords) >= 2:
                        min_lon, min_lat = map(float, coords[0].split(","))
                        max_lon, max_lat = map(float, coords[1].split(","))
                        bounds = (min_lon, min_lat, max_lon, max_lat)

                vis_results = visualize_crawl_results(
                    pois=processed_results,
                    boundary=bounds,
                    title=f"POI爬取结果 - {args.boundary_file or '多边形边界'}",
                    output_dir=OUTPUT_CONFIG["output_dir"],
                    show_plot=False
                )

                print(f"\n可视化图片已保存:")
                if vis_results.get("scatter"):
                    print(f"  - 分布图: {vis_results['scatter']}")
                if vis_results.get("type_distribution"):
                    print(f"  - 类型分布图: {vis_results['type_distribution']}")

            except ImportError:
                print("\n提示: 安装 matplotlib 可以生成可视化图片")
                print("  pip install matplotlib")
            except Exception as e:
                print(f"\n可视化生成失败: {e}")

        print("\n" + "=" * 60)
        print("爬取完成!")
        print("=" * 60)

        return 0

    except KeyboardInterrupt:
        print("\n\n用户中断爬取")
        results = crawler.get_results()
        if results:
            save_choice = input(f"是否保存已获取的 {len(results)} 条数据? (y/n): ")
            if save_choice.lower() == 'y':
                output_file = args.output_file or get_output_path(
                    file_prefix="poi_data_interrupted",
                    format=args.format
                )
                crawler.save_results(output_file, format=args.format)
                print(f"数据已保存到: {output_file}")
        return 130

    except Exception as e:
        print(f"\n爬取出错: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """主函数"""
    args = parse_args()

    if args.list_types:
        list_poi_types()
        return 0

    return run_crawler(args)


if __name__ == "__main__":
    sys.exit(main())
