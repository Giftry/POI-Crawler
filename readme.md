# POI 爬取工具

一个基于高德地图 API 的多边形网格化 POI（兴趣点）爬取工具，支持边界文件加载、坐标自动转换、数据可视化验证。

## 功能特性

- **网格化爬取策略**：自动将大区域切分为小网格逐格爬取，突破 API 单次返回 900 条数据的限制
- **Shapefile/GeoJSON 边界加载**：直接加载 ESRI Shapefile 或 GeoJSON 格式的边界文件
- **坐标系自动转换**：支持 WGS84 ↔ GCJ02 坐标转换
- **19 大类 POI 覆盖**：餐饮、住宿、购物、交通、景点、金融等完整类型体系
- **可视化验证**：爬取完成后自动生成 POI 空间分布图和类型统计图
- **数据导出**：支持 CSV 和 JSON 格式导出

## 项目结构

```
POI-Crawler/
├── config.py                     # 配置文件（API Key、默认参数）
├── run.py                        # 主运行脚本（命令行入口）
├── requirements.txt              # 依赖库
│
├── crawlers/                     # 爬取模块
│   ├── __init__.py
│   ├── api_endpoints.py         # API 端点
│   └── grid_polygon_crawler.py  # 网格化多边形爬虫（核心）
│
├── utils/                        # 工具模块
│   ├── __init__.py
│   ├── coordinate_converter.py  # WGS84 ↔ GCJ02 坐标系转换
│   ├── grid_generator.py        # 网格生成器
│   ├── shapefile_loader.py      # Shapefile/GeoJSON 边界加载
│   ├── poi_types.py             # POI 类型定义（19 大类）
│   └── visualizer.py            # 爬取结果可视化
│
├── processors/                   # 数据处理
│   └── data_processor.py        # 数据清洗和提取
│
├── outputs/                      # 输出模块
│   ├── __init__.py
│   ├── data_exporter.py         # CSV/JSON 导出
│   ├── poi_distribution.png     # POI 分布图（自动生成）
│   └── poi_type_distribution.png # 类型分布图（自动生成）
│
├── inputs/                       # 输入数据
│   ├── boundary/                # 边界文件（Shapefile/GeoJSON）
│   └── POI/                     # 参考 POI 数据
│
├── test_crawler.py              # 爬虫测试脚本
├── test_visualizer.py           # 可视化测试脚本
└── readme.md                    # 本文件
```

## 环境要求

- Python 3.7+

## 安装依赖

```bash
pip install -r requirements.txt
```

如需最小依赖（不含可视化）：
```bash
pip install requests geopandas coord_convert
```

## 配置说明

打开 [config.py](file:///d:\爬虫\POI-Crawler\config.py)，配置你的高德地图 API 密钥：

```python
AMAP_API_KEY = "你的API密钥"
```

**获取 API Key**：
1. 访问 [高德开放平台](https://lbs.amap.com/)
2. 注册并登录账号
3. 创建应用并获取 Web 服务 API Key

## 使用方法

### 基本用法

```bash
# 使用边界文件爬取所有类型 POI
python run.py --boundary-file inputs/boundary/调研边界.shp --all-types

# 爬取餐饮类 POI
python run.py --boundary-file inputs/boundary/调研边界.shp --types 010000

# 使用多边形坐标
python run.py --polygon "112.98,27.99|113.01,28.02" --types 010000,060000
```

### 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `--boundary-file` | 二选一 | Shapefile 或 GeoJSON 边界文件路径 |
| `--polygon` | 二选一 | 多边形坐标，格式: "lon1,lat1\|lon2,lat2\|..." |
| `--types` | 否 | POI 类型编码，多个类型用逗号分隔（如: 010000,060000） |
| `--all-types` | 否 | 爬取全部 19 大类 POI |
| `--api-key` | 否 | 指定 API Key（覆盖 config.py） |
| `--keyword` | 否 | 关键词过滤（如: "餐厅"） |
| `--grid-size` | 否 | 网格精度，0.001-0.01，默认 0.005 |
| `--request-interval` | 否 | API 请求间隔（秒），默认 0.2 |
| `--format` | 否 | 输出格式，csv 或 json |
| `--no-visualize` | 否 | 禁用可视化图片生成 |
| `--list-types` | - | 列出所有 POI 类型并退出 |

### 常见使用示例

```bash
# 1. 查看所有 POI 类型
python run.py --list-types

# 2. 爬取餐饮和购物
python run.py --boundary-file inputs/boundary/调研边界.shp --types 010000,060000

# 3. 爬取所有类型（19 大类）
python run.py --boundary-file inputs/boundary/调研边界.shp --all-types

# 4. 精细网格（适合密集区域）
python run.py --boundary-file inputs/boundary/调研边界.shp --grid-size 0.002

# 5. 关键词过滤
python run.py --boundary-file inputs/boundary/调研边界.shp --types 010000 --keyword "肯德基"
```

### POI 类型编码

| 编码 | 名称 |
|------|------|
| 010000 | 餐饮服务 |
| 020000 | 住宿服务 |
| 030000 | 交通设施服务 |
| 040000 | 金融保险服务 |
| 050000 | 风景名胜 |
| 060000 | 购物服务 |
| 070000 | 生活服务 |
| 080000 | 体育休闲服务 |
| 090000 | 医疗保健服务 |
| 100000 | 科教文化服务 |
| 110000 | 公司企业 |
| 120000 | 政府机构及社会团体 |
| 130000 | 道路附属设施 |
| 140000 | 地名地址信息 |
| 150000 | 商务住宅 |
| 160000 | 通行设施 |
| 170000 | 公共设施 |
| 180000 | 事件活动 |
| 190000 | 其他 |

## 网格大小建议

| 网格大小 | 实际覆盖 | 适用场景 |
|----------|----------|----------|
| 0.01 | ~1.1km × 1.1km | 快速大范围扫描 |
| 0.005 | ~550m × 500m | 平衡精度与速度（默认） |
| 0.002 | ~220m × 200m | 高精度需求 |
| 0.001 | ~110m × 100m | 极精细覆盖 |

## 输出说明

### 数据文件
- CSV/JSON 文件保存在 `outputs/` 目录
- 文件命名: `poi_data_YYYYMMDD_HHMMSS.{csv|json}`

### 可视化图片
爬取完成后自动生成两张验证图：

1. **poi_distribution.png** - POI 空间分布图
   - 红色矩形：爬取边界
   - 彩色散点：各类型 POI

2. **poi_type_distribution.png** - POI 类型分布柱状图
   - 各类 POI 数量统计

## 运行测试

```bash
# 测试核心功能（不调用真实 API）
python test_crawler.py --api-key YOUR_KEY --skip-real

# 测试可视化功能
python test_visualizer.py
```

## 注意事项

- 高德地图 API 免费版有调用频率（QPS）和日调用量限制，请合理设置 `--request-interval`
- 大区域或精细网格爬取时间较长，建议先用小区域测试
- 爬取边界文件建议使用 GCJ02（国测局）坐标系

## 许可证

MIT License
