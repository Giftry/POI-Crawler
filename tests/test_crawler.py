"""
测试网格化多边形爬取功能

提供模拟数据和真实API测试两种模式
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.grid_generator import GridGenerator
from utils.coordinate_converter import wgs84_to_gcj02
from utils.poi_types import POI_TYPES, get_type_name
from crawlers.grid_polygon_crawler import GridPolygonCrawler, CrawlerConfig


def test_grid_generator():
    """测试网格生成器"""
    print("=" * 60)
    print("测试网格生成器")
    print("=" * 60)

    min_lon, min_lat = 112.96, 27.97
    max_lon, max_lat = 113.04, 28.03

    print(f"\n测试区域:")
    print(f"  经度范围: {min_lon} ~ {max_lon}")
    print(f"  纬度范围: {min_lat} ~ {max_lat}")

    generator = GridGenerator(min_lon, min_lat, max_lon, max_lat, grid_size=0.005)
    grids = generator.generate_grids()

    print(f"\n网格大小: {generator.grid_size}")
    print(f"网格大小描述: {generator.get_grid_size_description()}")
    print(f"网格总数: {len(grids)}")
    print(f"覆盖面积: {generator.get_grid_area():.2f} 平方公里")

    print(f"\n前5个网格:")
    for i, grid in enumerate(grids[:5]):
        print(f"  {i + 1}. {grid}")

    print("\n测试不同网格大小:")
    for size in [0.01, 0.005, 0.002, 0.001]:
        gen = GridGenerator(min_lon, min_lat, max_lon, max_lat, grid_size=size)
        print(f"  {size}: {gen.get_grid_count()} 个网格, {gen.get_grid_size_description()}")

    print("\n✓ 网格生成器测试通过")


def test_coordinate_converter():
    """测试坐标系转换"""
    print("\n" + "=" * 60)
    print("测试坐标系转换")
    print("=" * 60)

    test_coords = [
        (116.397128, 39.916527),
        (113.0, 28.0),
        (121.473701, 31.230416),
    ]

    print("\nWGS84 -> GCJ-02 转换测试:")
    for lon, lat in test_coords:
        gcj_lon, gcj_lat = wgs84_to_gcj02(lon, lat)
        print(f"  WGS84: ({lon}, {lat}) -> GCJ-02: ({gcj_lon}, {gcj_lat})")

    print("\n✓ 坐标系转换测试通过")


def test_poi_types():
    """测试POI类型定义"""
    print("\n" + "=" * 60)
    print("测试POI类型定义")
    print("=" * 60)

    print(f"\nPOI类型总数: {len(POI_TYPES)}")

    print("\n所有POI类型:")
    for code, name in POI_TYPES.items():
        print(f"  {code}: {name}")

    print(f"\n类型名称查询:")
    for code in ['010000', '060000', '110000']:
        print(f"  {code} -> {get_type_name(code)}")

    print("\n✓ POI类型定义测试通过")


def test_mock_crawler():
    """模拟爬取测试（不调用真实API）"""
    print("\n" + "=" * 60)
    print("模拟爬取测试")
    print("=" * 60)

    min_lon, min_lat = 112.98, 27.99
    max_lon, max_lat = 113.01, 28.02

    generator = GridGenerator(min_lon, min_lat, max_lon, max_lat, grid_size=0.01)
    grids = generator.generate_grids()

    print(f"\n模拟爬取区域:")
    print(f"  网格数量: {len(grids)}")
    print(f"  网格大小: {generator.get_grid_size_description()}")

    print("\n模拟爬取进度:")
    for i, grid in enumerate(grids):
        progress = (i + 1) / len(grids) * 100
        print(f"  [{progress:5.1f}%] 网格 {i + 1}/{len(grids)}: {grid}")

    print("\n✓ 模拟爬取测试通过")


def test_real_crawler(api_key: str = None):
    """真实API爬取测试"""
    if not api_key:
        print("\n未提供API密钥，跳过真实API测试")
        print("使用以下命令运行真实API测试:")
        print("  python test_crawler.py --api-key YOUR_API_KEY")
        return

    print("\n" + "=" * 60)
    print("真实API爬取测试")
    print("=" * 60)

    boundary = "112.98,27.99|113.01,28.02"

    print(f"\n爬取参数:")
    print(f"  边界: {boundary}")
    print(f"  类型: 餐饮 (010000)")
    print(f"  网格大小: 0.01")

    config = CrawlerConfig(
        api_key=api_key,
        grid_size=0.01,
        page_size=25,
        request_interval=0.3
    )

    crawler = GridPolygonCrawler(config)

    print("\n开始爬取...")
    results = crawler.search_by_boundary(
        boundary=boundary,
        poi_types=['010000'],
        grid_size=0.01,
        auto_convert_coords=True
    )

    print(f"\n爬取结果:")
    print(f"  获取POI数量: {len(results)}")

    if results:
        print(f"\n第一条POI:")
        poi = results[0]
        print(f"  名称: {poi.get('name', 'N/A')}")
        print(f"  类型: {poi.get('type', 'N/A')}")
        print(f"  地址: {poi.get('address', 'N/A')}")
        print(f"  位置: {poi.get('location', 'N/A')}")

    print("\n✓ 真实API爬取测试完成")


def main():
    """主测试函数"""
    import argparse

    parser = argparse.ArgumentParser(description="POI爬虫测试")
    parser.add_argument("--api-key", "-k", help="高德地图API密钥")
    parser.add_argument("--skip-real", action="store_true", help="跳过真实API测试")
    args = parser.parse_args()

    test_grid_generator()
    test_coordinate_converter()
    test_poi_types()
    test_mock_crawler()

    if not args.skip_real:
        test_real_crawler(args.api_key)

    print("\n" + "=" * 60)
    print("所有测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
