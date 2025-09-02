# 配置文件 - 用户可以修改这些设置

import os

# 项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 数据目录和文件路径
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_DIR = os.path.join(DATA_DIR, "csv")
GEOJSON_DIR = os.path.join(DATA_DIR, "geojson")
GEOJSON_PATH = os.path.join(GEOJSON_DIR, "beijing_districts.geojson")

# 区域文件映射 - 使用相对路径
DISTRICT_FILES = {
    "东城": os.path.join(CSV_DIR, "东城区.csv"),
    "西城": os.path.join(CSV_DIR, "西城区.csv"),
    "朝阳": os.path.join(CSV_DIR, "朝阳区.csv"),
    "海淀": os.path.join(CSV_DIR, "海淀区.csv"),
    "丰台": os.path.join(CSV_DIR, "丰台区.csv"),
    "石景山": os.path.join(CSV_DIR, "石景山区.csv"),
    "通州": os.path.join(CSV_DIR, "通州区.csv"),
    "顺义": os.path.join(CSV_DIR, "顺义区.csv"),
    "大兴": os.path.join(CSV_DIR, "大兴区.csv"),
    "房山": os.path.join(CSV_DIR, "房山区.csv"),
    "门头沟": os.path.join(CSV_DIR, "门头沟区.csv"),
    "昌平": os.path.join(CSV_DIR, "昌平区.csv"),
    "平谷": os.path.join(CSV_DIR, "平谷区.csv"),
    "怀柔": os.path.join(CSV_DIR, "怀柔区.csv"),
    "密云": os.path.join(CSV_DIR, "密云区.csv"),
    "延庆": os.path.join(CSV_DIR, "延庆区.csv")
}

# 可视化设置
VISUALIZATION_SETTINGS = {
    "colorscale": [
        [0.0, '#0000FF'],   # 蓝色
        [0.2, '#00FFFF'],   # 青色
        [0.4, '#00FF00'],   # 绿色
        [0.6, '#FFFF00'],   # 黄色
        [0.8, '#FFA500'],   # 橙色
        [1.0, '#FF0000']    # 红色
    ],
    "map_style": "open-street-map",
    "map_center": {"lon": 116.4, "lat": 40.0},
    "map_zoom": 8.5,
    "opacity": 0.85,
    "line_width": 1.5,
    "line_color": "rgba(255, 255, 255, 0.8)",
    "text_font_size": 12,
    "text_font_color": "black",
    "text_font_family": "Arial"
}

# 数据处理设置
DATA_PROCESSING_SETTINGS = {
    "csv_encoding": "gbk",
    "csv_header_row": 9,
    "date_format": "%Y-%m-%d",
    "time_format": "%H:%M",
    "datetime_format": "%Y-%m-%d %H:%M",
    "possible_wind_columns": ['地面风速m/s', '地面风速(m/s)', '风速', '地面风速', '10米风速']
}