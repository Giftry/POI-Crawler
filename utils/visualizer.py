"""
爬取结果可视化模块

用于验证POI爬取结果的正确性，显示边界和POI点分布
"""

import os
from typing import List, Dict, Any, Optional, Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.font_manager import FontProperties
import numpy as np

try:
    from utils.poi_types import POI_TYPES, get_type_name, get_type_color
    HAS_POI_TYPES = True
except ImportError:
    HAS_POI_TYPES = False

try:
    from utils.coordinate_converter import gcj02_to_wgs84
    HAS_COORD_CONVERTER = True
except ImportError:
    HAS_COORD_CONVERTER = False


def setup_chinese_font():
    """设置中文字体支持"""
    import matplotlib
    matplotlib.use('Agg')
    
    available_fonts = [f.name for f in FontProperties().get_size_adjustable() if hasattr(f, 'name')]
    
    chinese_fonts = ['SimHei', 'Microsoft YaHei', 'SimSun', 'KaiTi', 'FangSong', 
                     'Arial Unicode MS', 'DejaVu Sans']
    
    for font in chinese_fonts:
        if font in available_fonts:
            plt.rcParams['font.sans-serif'] = [font]
            plt.rcParams['axes.unicode_minus'] = False
            return True
    
    try:
        import matplotlib.font_manager as fm
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


class CrawlResultVisualizer:
    """
    爬取结果可视化器

    用于显示爬取边界和POI点分布，验证爬取位置是否正确
    自动处理坐标系转换（GCJ02 -> WGS84）
    """

    def __init__(self, boundary: Tuple[float, float, float, float] = None,
                 poi_types_colors: Optional[Dict[str, str]] = None,
                 source_coords: str = "gcj02"):
        """
        初始化可视化器

        Args:
            boundary: 边界框 (min_lon, min_lat, max_lon, max_lat)
            poi_types_colors: POI类型到颜色的映射
            source_coords: 源坐标系，"gcj02" 或 "wgs84"，默认 "gcj02"
        """
        self.boundary = boundary
        self.poi_types_colors = poi_types_colors or {}
        self.pois = []
        self.figure = None
        self.ax = None
        self.source_coords = source_coords
        
        setup_chinese_font()

        if not HAS_POI_TYPES:
            self.default_colors = plt.cm.tab20.colors
        else:
            self.default_colors = None

    def _convert_coords(self, lon: float, lat: float) -> Tuple[float, float]:
        """转换坐标到 WGS84"""
        if self.source_coords.lower() == "wgs84":
            return lon, lat
        
        if HAS_COORD_CONVERTER:
            return gcj02_to_wgs84(lon, lat)
        
        return lon, lat

    def add_pois(self, pois: List[Dict[str, Any]]):
        """
        添加POI数据

        Args:
            pois: POI列表，每个POI需要包含location字段 (格式: "lon,lat")
        """
        self.pois = []
        for poi in pois:
            location = poi.get('location', '')
            if location and ',' in location:
                try:
                    lon, lat = map(float, location.split(','))
                    
                    lon_wgs, lat_wgs = self._convert_coords(lon, lat)
                    
                    poi_copy = poi.copy()
                    poi_copy['lon'] = lon_wgs
                    poi_copy['lat'] = lat_wgs
                    poi_copy['lon_gcj'] = lon
                    poi_copy['lat_gcj'] = lat

                    typecode = poi.get('typecode', '')
                    if typecode and HAS_POI_TYPES:
                        major_type = typecode[:2] + '0000'
                        poi_copy['major_type'] = major_type
                        poi_copy['type_name'] = get_type_name(major_type)
                    else:
                        poi_copy['major_type'] = 'other'
                        poi_copy['type_name'] = poi.get('type', '未知')

                    self.pois.append(poi_copy)
                except (ValueError, TypeError):
                    continue

    def _get_color(self, poi_type: str) -> str:
        """获取POI类型的颜色"""
        if HAS_POI_TYPES and poi_type in POI_TYPES:
            return get_type_color(poi_type)
        if poi_type in self.poi_types_colors:
            return self.poi_types_colors[poi_type]

        if self.default_colors:
            type_hash = sum(ord(c) for c in poi_type)
            return self.default_colors[type_hash % len(self.default_colors)]

        return '#1f77b4'

    def plot(self, title: str = "POI爬取结果验证",
             show_grid: bool = True,
             show_boundary: bool = True,
             show_labels: bool = False,
             max_labels: int = 20,
             save_path: Optional[str] = None,
             figsize: Tuple[int, int] = (14, 10),
             dpi: int = 150) -> plt.Figure:
        """
        绑定爬取结果

        Args:
            title: 图表标题
            show_grid: 是否显示网格
            show_boundary: 是否显示边界框
            show_labels: 是否显示POI名称标签
            max_labels: 最大标签数量（避免拥挤）
            save_path: 保存路径，None则不保存
            figsize: 图形大小
            dpi: 分辨率

        Returns:
            matplotlib Figure对象
        """
        if not self.pois:
            raise ValueError("没有POI数据可绑定")

        self.figure, self.ax = plt.subplots(figsize=figsize, dpi=dpi)

        lons = [poi['lon'] for poi in self.pois]
        lats = [poi['lat'] for poi in self.pois]
        types = [poi.get('major_type', 'other') for poi in self.pois]
        names = [poi.get('name', '') for poi in self.pois]

        unique_types = sorted(set(types))
        type_to_color = {t: self._get_color(t) for t in unique_types}
        colors = [type_to_color[t] for t in types]

        if HAS_POI_TYPES:
            type_names = [get_type_name(t) if t in POI_TYPES else t for t in unique_types]
        else:
            type_names = unique_types

        for poi_type, type_name in zip(unique_types, type_names):
            mask = [t == poi_type for t in types]
            type_lons = [l for l, m in zip(lons, mask) if m]
            type_lats = [l for l, m in zip(lats, mask) if m]

            self.ax.scatter(type_lons, type_lats,
                         c=type_to_color[poi_type],
                         s=50, alpha=0.7, label=f'{type_name} ({sum(mask)})',
                         edgecolors='white', linewidths=0.5)

        if show_labels and names:
            label_count = 0
            for i, (lon, lat, name) in enumerate(zip(lons, lats, names)):
                if label_count >= max_labels:
                    break
                self.ax.annotate(name[:8], (lon, lat),
                               fontsize=6, alpha=0.8,
                               xytext=(3, 3), textcoords='offset points')
                label_count += 1

        if show_boundary and self.boundary:
            min_lon, min_lat, max_lon, max_lat = self.boundary
            
            min_lon, min_lat = self._convert_coords(min_lon, min_lat)
            max_lon, max_lat = self._convert_coords(max_lon, max_lat)
            
            boundary_rect = mpatches.Rectangle(
                (min_lon, min_lat),
                max_lon - min_lon,
                max_lat - min_lat,
                linewidth=2, edgecolor='red',
                facecolor='red', alpha=0.1,
                label='爬取边界'
            )
            self.ax.add_patch(boundary_rect)

        margin = 0.002
        if self.boundary:
            min_lon, min_lat, max_lon, max_lat = self.boundary
            min_lon, min_lat = self._convert_coords(min_lon, min_lat)
            max_lon, max_lat = self._convert_coords(max_lon, max_lat)
            
            self.ax.set_xlim(min_lon - margin, max_lon + margin)
            self.ax.set_ylim(min_lat - margin, max_lat + margin)

        if show_grid:
            self.ax.grid(True, linestyle='--', alpha=0.3)

        self.ax.set_xlabel('经度 (Longitude)', fontsize=10)
        self.ax.set_ylabel('纬度 (Latitude)', fontsize=10)
        self.ax.set_title(title, fontsize=14, fontweight='bold')

        self.ax.legend(loc='upper left', fontsize=8, framealpha=0.9,
                      ncol=2 if len(unique_types) > 8 else 1)

        plt.tight_layout()

        if save_path:
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
            self.figure.savefig(save_path, dpi=dpi, bbox_inches='tight',
                              facecolor='white', edgecolor='none')
            print(f"可视化图片已保存到: {save_path}")

        return self.figure

    def plot_by_types(self, title: str = "POI类型分布",
                     save_path: Optional[str] = None,
                     figsize: Tuple[int, int] = (12, 8)) -> plt.Figure:
        """
        绑定POI类型分布柱状图

        Args:
            title: 图表标题
            save_path: 保存路径
            figsize: 图形大小

        Returns:
            matplotlib Figure对象
        """
        if not self.pois:
            raise ValueError("没有POI数据可绑定")

        type_counts = {}
        for poi in self.pois:
            major_type = poi.get('major_type', 'other')
            if HAS_POI_TYPES and major_type in POI_TYPES:
                type_name = get_type_name(major_type)
            else:
                type_name = major_type

            type_counts[type_name] = type_counts.get(type_name, 0) + 1

        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)

        fig, ax = plt.subplots(figsize=figsize)

        names = [t[0] for t in sorted_types]
        counts = [t[1] for t in sorted_types]
        colors = [self._get_color(t) for t in [k for k, v in sorted_types]]

        bars = ax.barh(names, counts, color=colors, edgecolor='white', linewidth=0.5)

        for bar, count in zip(bars, counts):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                   f'{count}', va='center', fontsize=9)

        ax.set_xlabel('POI数量', fontsize=10)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.invert_yaxis()

        plt.tight_layout()

        if save_path:
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
            fig.savefig(save_path, dpi=150, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            print(f"类型分布图已保存到: {save_path}")

        return fig

    def get_summary(self) -> Dict[str, Any]:
        """获取爬取结果摘要"""
        if not self.pois:
            return {"total": 0}

        type_counts = {}
        for poi in self.pois:
            major_type = poi.get('major_type', 'other')
            type_counts[major_type] = type_counts.get(major_type, 0) + 1

        lons = [poi['lon'] for poi in self.pois]
        lats = [poi['lat'] for poi in self.pois]

        return {
            "total": len(self.pois),
            "type_distribution": type_counts,
            "bounds": {
                "min_lon": min(lons),
                "max_lon": max(lons),
                "min_lat": min(lats),
                "max_lat": max(lats)
            },
            "center": {
                "lon": sum(lons) / len(lons),
                "lat": sum(lats) / len(lats)
            }
        }

    def show(self):
        """显示图形"""
        if self.figure:
            plt.show()
        else:
            raise ValueError("请先调用plot()方法")


def visualize_crawl_results(pois: List[Dict[str, Any]],
                          boundary: Tuple[float, float, float, float] = None,
                          title: str = "POI爬取结果验证",
                          output_dir: str = "outputs",
                          show_plot: bool = True,
                          source_coords: str = "gcj02") -> Dict[str, str]:
    """
    便捷函数：可视化爬取结果

    Args:
        pois: POI列表
        boundary: 边界框 (min_lon, min_lat, max_lon, max_lat)
        title: 图表标题
        output_dir: 输出目录
        show_plot: 是否显示图形
        source_coords: 源坐标系，"gcj02" 或 "wgs84"，默认 "gcj02"

    Returns:
        输出文件路径字典
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    visualizer = CrawlResultVisualizer(boundary=boundary, source_coords=source_coords)
    visualizer.add_pois(pois)

    scatter_path = os.path.join(output_dir, "poi_distribution.png")
    try:
        visualizer.plot(title=title, save_path=scatter_path, show_boundary=boundary is not None)
    except Exception as e:
        print(f"绑定散点图失败: {e}")

    type_dist_path = os.path.join(output_dir, "poi_type_distribution.png")
    try:
        visualizer.plot_by_types(title=f"{title} - 类型分布", save_path=type_dist_path)
    except Exception as e:
        print(f"绑定类型分布图失败: {e}")

    summary = visualizer.get_summary()
    print(f"\n爬取结果摘要:")
    print(f"  总POI数量: {summary['total']}")
    if 'bounds' in summary:
        print(f"  位置范围: 经度 [{summary['bounds']['min_lon']:.4f}, {summary['bounds']['max_lon']:.4f}]")
        print(f"            纬度 [{summary['bounds']['min_lat']:.4f}, {summary['bounds']['max_lat']:.4f}]")
        print(f"  中心点: ({summary['center']['lon']:.4f}, {summary['center']['lat']:.4f})")

    if not show_plot:
        plt.close('all')

    return {
        "scatter": scatter_path if os.path.exists(scatter_path) else None,
        "type_distribution": type_dist_path if os.path.exists(type_dist_path) else None,
        "summary": summary
    }
