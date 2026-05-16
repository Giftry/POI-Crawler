"""
测试可视化功能

测试POI爬取结果的可视化绑定
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.visualizer import CrawlResultVisualizer, visualize_crawl_results


def test_visualizer():
    """测试可视化功能"""
    print("=" * 60)
    print("测试可视化功能")
    print("=" * 60)

    mock_pois = [
        {"id": "1", "name": "餐厅A", "location": "112.985,28.000", "typecode": "010101", "type": "餐饮服务;中餐厅"},
        {"id": "2", "name": "餐厅B", "location": "112.990,28.002", "typecode": "010102", "type": "餐饮服务;外国餐厅"},
        {"id": "3", "name": "商场C", "location": "112.995,28.005", "typecode": "060101", "type": "购物;综合商场"},
        {"id": "4", "name": "银行D", "location": "112.988,28.008", "typecode": "040100", "type": "金融;银行"},
        {"id": "5", "name": "景点E", "location": "112.992,28.001", "typecode": "050101", "type": "旅游景点;公园"},
        {"id": "6", "name": "医院F", "location": "112.987,28.003", "typecode": "090101", "type": "医疗保健;医院"},
        {"id": "7", "name": "学校G", "location": "112.991,28.006", "typecode": "100101", "type": "科教文化;学校"},
        {"id": "8", "name": "酒店H", "location": "112.994,28.004", "typecode": "020101", "type": "住宿;酒店"},
    ]

    boundary = (112.98, 27.99, 113.01, 28.02)

    print(f"\n测试数据:")
    print(f"  POI数量: {len(mock_pois)}")
    print(f"  边界: {boundary}")

    visualizer = CrawlResultVisualizer(boundary=boundary)
    visualizer.add_pois(mock_pois)

    summary = visualizer.get_summary()
    print(f"\n数据摘要:")
    print(f"  总POI数: {summary['total']}")
    if 'bounds' in summary:
        print(f"  位置范围: 经度 [{summary['bounds']['min_lon']:.4f}, {summary['bounds']['max_lon']:.4f}]")
        print(f"            纬度 [{summary['bounds']['min_lat']:.4f}, {summary['bounds']['max_lat']:.4f}]")

    output_dir = os.path.join(os.path.dirname(__file__), "outputs")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"\n生成可视化图片...")
    vis_results = visualize_crawl_results(
        pois=mock_pois,
        boundary=boundary,
        title="测试POI爬取结果",
        output_dir=output_dir,
        show_plot=False
    )

    print(f"\n生成结果:")
    if vis_results.get("scatter"):
        print(f"  ✓ 分布图: {vis_results['scatter']}")
    if vis_results.get("type_distribution"):
        print(f"  ✓ 类型分布图: {vis_results['type_distribution']}")

    print("\n✓ 可视化功能测试完成")
    return vis_results


if __name__ == "__main__":
    test_visualizer()
