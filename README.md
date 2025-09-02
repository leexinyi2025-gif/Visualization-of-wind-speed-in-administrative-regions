# Beijing Wind Speed Visualization System  
  
一个基于Python的北京市行政区域风速数据可视化系统，支持时间序列动画和交互式地图展示。修改geojson行政区边界文件和地区风速csv即可二次开发。
  
## 项目概述  
  
本项目将北京市16个行政区域的风速数据与地理边界信息结合，生成交互式HTML可视化地图。系统支持时间滑块控制、动画播放和悬停交互功能。运行当前文件以及主程序即可视化北京市2025-4-10至2025-4-14五天的16个行政区的逐时风速可视化html地图。  
  
## 功能特性  
  
- 🗺️ 交互式地理可视化（基于Plotly和Mapbox）  
- ⏱️ 时间序列动画播放  
- 📊 实时风速数据展示  
- 🎨 可自定义颜色映射和样式  
- 📱 响应式设计，支持多种设备  
  
## 项目结构
├── main.py # 主程序入口
├── config/
│ └── settings.py # 配置文件
├── src/  ├── 来源/
│ ├── data_loader.py # 数据加载模块
│ ├── geojson_processor.py # GeoJSON处理模块
│ ├── geojson_processor.py # GeoJSON 处理模块
│ ├── visualization.py # 可视化模块
│ └── utils.py # 工具函数
├── data/  ├── 数据/
│ ├── csv/ # 风速数据文件
│ │ ├── 东城区.csv
│ │ ├── 西城区.csv
│ │ └── ...
│ └── geojson/
│ └── beijing_districts.geojson
├── requirements.txt # 依赖包列表
└── README.md

  
## 安装和使用  
  
### 环境要求  
  
- Python 3.7+  
- 依赖包：pandas, plotly, numpy, shapely  
  
### 安装步骤  
  
1. 克隆项目：  
```bash  
git clone <repository-url>  

安装依赖：
pip install -r requirements.txt

运行程序：
python main.py
打开生成的 beijing_wind_speed_map.html 文件查看可视化结果

数据格式要求
CSV数据文件格式  CSV 数据文件格式
每个区域的CSV文件应包含以下列：  每个区域的 CSV 文件应包含以下列：

日期: 日期信息（格式：YYYY-MM-DD）
时间: 时间信息（格式：HH:MM）
时间 ：时间信息（格式：HH：MM）
地面风速m/s: 风速数值（单位：米/秒）
地面风速 m/s：风速值（单位：m/s）
GeoJSON文件格式  GeoJSON 文件格式
地理边界文件应包含以下属性：

adcode: 行政区域代码
name: 区域名称
geometry: 地理边界坐标
配置说明
基础配置
在 config/settings.py 中可以修改以下设置：

文件路径配置
DISTRICT_FILES = {  
    "东城": "data/csv/东城区.csv",  
    "西城": "data/csv/西城区.csv",  
    # ... 其他区域  
}  
GEOJSON_PATH = "data/geojson/beijing_districts.geojson"

可视化样式配置
VISUALIZATION_SETTINGS = {  
    "colorscale": [...],        # 颜色映射  
    "map_style": "open-street-map",  # 地图样式  
    "map_center": {"lon": 116.4, "lat": 40.0},  # 地图中心  
    "map_zoom": 8.5,           # 缩放级别  
    "opacity": 0.85,           # 透明度  
}

数据处理配置
DATA_PROCESSING_SETTINGS = {  
    "csv_encoding": "gbk",     # CSV文件编码  
    "csv_header_row": 9,       # 数据开始行  
    "possible_wind_columns": ['地面风速m/s', '风速'],  # 风速列名  
}

二次开发指南
添加新的行政区域
在 data/csv/ 目录添加新的CSV文件
在 data/csv/ 目录添加新的 CSV 文件
在 config/settings.py 的 DISTRICT_FILES 中添加映射
确保GeoJSON文件包含对应的地理边界
修改可视化样式
更改颜色方案  更改配色方案
# 在 config/settings.py 中修改  [header-2](#header-2)
"colorscale": [  
    [0.0, '#your_color_1'],  
    [0.5, '#your_color_2'],  
    [1.0, '#your_color_3']  
]

更改地图样式
支持的地图样式：

"open-street-map" - 开放街道地图（推荐，无需API密钥）
"carto-positron" - Carto浅色主题
"carto-darkmatter" - Carto深色主题
"white-bg" - 白色背景

扩展到其他城市
准备目标城市的GeoJSON边界文件  准备目标城市的 Ge
准备各区域的风速CSV数据  准备各区域的风速 CSV 数据
修改 config/settings.py 中的文件路径和地图中心坐标
根据需要调整 src/geojson_processor.py 中的区域名称标准化逻辑
添加新的数据源
在 src/data_loader.py 中扩展 detect_csv_format() 函数
在 DATA_PROCESSING_SETTINGS 中添加新的列名映射
修改数据加载逻辑以支持新的数据格式

常见问题解决
地图不显示问题
问题: 生成HTML文件但地图空白  问题 : 生成 HTML 文件但地图
解决: 修改 config/settings.py 中的地图样式：
"map_style": "open-street-map"  # 替换 "carto-voyager"

数据加载失败
问题: CSV文件读取错误  问题 : CSV 文件读取错误
解决: 检查文件编码和格式：  解决 : 检查文件编码和格式：

# 在 config/settings.py 中调整  [header-3](#header-3)
"csv_encoding": "utf-8",  # 或 "gbk"  
"csv_header_row": 0,      # 调整数据开始行

区域匹配失败
问题: 数据与地理边界不匹配  问题 : 数据与地理边界不匹配
解决: 检查区域名称标准化，确保CSV文件名与GeoJSON中的区域名称一致

技术架构
核心模块
main.py: 系统协调器，管理整个数据处理流程  main.py： 系统协调
data_loader.py: CSV数据加载和标准化
geojson_processor.py: 地理数据处理和区域映射
visualization.py: 交互式可视化生成
utils.py: 通用工具函数

数据流程
CSV文件 + GeoJSON → 数据加载 → 地理映射 → 可视化生成 → HTML输出

依赖说明
pandas>=1.3.0    # 数据处理  
plotly>=5.0.0    # 可视化  
numpy>=1.21.0    # 数值计算  
shapely>=1.8.0   # 地理计算  


