# POI 爬取工具

一个自动化的 POI（兴趣点）爬取工具，从高德地图 API 获取数据，支持数据处理和导出为 CSV 或 JSON 格式。

## 功能特性

- 从高德地图 API 爬取 POI 数据
- 支持关键词搜索和城市筛选
- 自动处理分页和错误重试
- 标准化和处理 POI 数据
- 支持导出为 CSV 或 JSON 格式

## 项目结构

```
POI-Crawler/
├── config.py          # 配置文件
├── crawlers/          # 爬取组件
│   └── amap_crawler.py  # 高德地图 API 爬取器
├── processors/        # 数据处理组件
│   └── data_processor.py  # 数据处理器
├── outputs/           # 数据输出组件
│   └── data_exporter.py   # 数据导出器
├── run.py             # 主运行脚本
├── output/            # 输出目录
└── README.md          # 项目说明
```

## 环境要求

- Python 3.6+
- requests 库

## 安装依赖

```bash
pip install requests
```

## 配置说明

1. 打开 `config.py` 文件
2. 将 `AMAP_API_KEY` 替换为你自己的高德地图 API 密钥
3. 根据需要调整其他配置参数

## 使用方法

### 基本用法

```bash
python run.py --keyword "餐厅" --city "北京"
```

### 高级用法

```bash
# 指定 POI 类型和输出格式
python run.py --keyword "酒店" --city "上海" --types "080201" --format "json"

# 使用多边形边界爬取
python run.py --keyword "餐厅" --polygon "116.3,39.9|116.4,39.9|116.4,40.0|116.3,40.0|116.3,39.9"

# 使用边界文件爬取
python run.py --keyword "餐厅" --boundary-file "boundary_example.json"
```

### 参数说明

- `--keyword`：搜索关键词（必填）
- `--city`：城市名称或城市编码（使用多边形边界时可选）
- `--types`：POI 类型编码（可选）
- `--extensions`：返回结果控制，`base` 或 `all`（默认 `all`）
- `--format`：输出格式，`csv` 或 `json`（默认根据配置文件）
- `--polygon`：多边形边界坐标，格式为 `lon1,lat1|lon2,lat2|...|lonN,latN`（与 --city 和 --boundary-file 互斥）
- `--boundary-file`：边界文件路径，支持 JSON 和文本格式（与 --city 和 --polygon 互斥）

## 高德地图 API 密钥获取

1. 访问 [高德开放平台](https://lbs.amap.com/)
2. 注册并登录账号
3. 创建应用并获取 API 密钥
4. 将 API 密钥填入 `config.py` 文件

## 注意事项

- 高德地图 API 有调用频率限制，请合理设置请求间隔
- 免费版 API 有每日调用次数限制，请根据实际需求选择合适的 API 套餐
- 请遵守高德地图 API 的使用条款和服务协议

## 示例输出

### CSV 格式

包含 POI 的名称、地址、电话、经纬度等信息。

### JSON 格式

包含完整的 POI 信息，包括基本信息、经纬度、照片等。
