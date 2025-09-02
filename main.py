"""主程序入口"""
import os
import sys
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_loader import load_wind_data
from src.geojson_processor import load_geojson, create_district_adcode_map
from src.visualization import create_wind_visualization
from src.utils import setup_logging
import config.settings as config

def main():
    """主函数"""
    # 设置日志
    setup_logging(verbose=True)
    logger = logging.getLogger(__name__)
    
    # 加载GeoJSON数据
    if not os.path.exists(config.GEOJSON_PATH):
        logger.error(f"GeoJSON file does not exist - {config.GEOJSON_PATH}")
        return
    
    logger.info(f"Loading GeoJSON file: {config.GEOJSON_PATH}")
    beijing_geojson = load_geojson(config.GEOJSON_PATH)
    
    # 检查GeoJSON结构
    logger.info(f"GeoJSON type: {beijing_geojson.get('type')}")
    logger.info(f"Number of features: {len(beijing_geojson.get('features', []))}")
    
    # 打印前几个特征的属性
    for i, feature in enumerate(beijing_geojson.get('features', [])[:3]):
        logger.info(f"Feature {i} properties: {feature.get('properties')}")
    
    # 创建区名到adcode的映射
    district_adcode_map = create_district_adcode_map(beijing_geojson)
    logger.info(f"District adcode mapping: {district_adcode_map}")
    
    # 加载数据
    wind_df = load_wind_data(config.DISTRICT_FILES, beijing_geojson, config)
    
    if wind_df.empty:
        logger.error("No valid data loaded")
        return
    
    # 检查数据与GeoJSON的匹配
    data_adcodes = wind_df['adcode'].unique()
    logger.info(f"Data adcodes: {data_adcodes}")
    
    # 检查哪些adcode在GeoJSON中不存在
    missing_in_geojson = [adcode for adcode in data_adcodes if adcode not in district_adcode_map.values()]
    if missing_in_geojson:
        logger.warning(f"Adcodes in data but not in GeoJSON: {missing_in_geojson}")
    
    # 创建可视化
    logger.info("Creating visualization...")
    fig = create_wind_visualization(wind_df, beijing_geojson, config)
    
    # 显示图形
    logger.info("Displaying visualization...")
    fig.show()
    
    # 保存为HTML文件
    output_file = "beijing_wind_speed_map.html"
    fig.write_html(output_file)
    logger.info(f"Visualization saved as {output_file}")

if __name__ == "__main__":
    main()