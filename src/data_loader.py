"""数据加载和处理模块"""
import os
import pandas as pd
import logging
from .utils import standardize_district_name

logger = logging.getLogger(__name__)

def detect_csv_format(file_path, encoding="gbk"):
    """检测CSV文件格式"""
    try:
        # 尝试读取前20行来检测格式
        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            lines = [f.readline() for _ in range(20)]
        
        # 查找数据开始的行
        data_start_row = 0
        for i, line in enumerate(lines):
            if "日期" in line and "时间" in line:
                data_start_row = i
                break
        
        # 查找可能的列名
        possible_columns = lines[data_start_row].strip().split(',')
        logger.debug(f"Detected columns at row {data_start_row}: {possible_columns}")
        
        return data_start_row, possible_columns
    except Exception as e:
        logger.error(f"Error detecting CSV format for {file_path}: {str(e)}")
        return 0, []

def load_wind_data(district_files, geojson, config):
    """加载所有区域的风速数据"""
    from .geojson_processor import create_district_adcode_map
    
    # 创建区名到adcode的映射
    district_adcode_map = create_district_adcode_map(geojson)
    
    all_data = []
    missing_districts = []
    processed_files = 0
    
    logger.info("Loading wind speed data...")
    
    for district, file_path in district_files.items():
        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.error(f"File does not exist - {file_path}")
            continue
        
        try:
            logger.info(f"Processing district: {district}, File: {file_path}")
            
            # 检测CSV格式
            data_start_row, detected_columns = detect_csv_format(file_path, config.DATA_PROCESSING_SETTINGS["csv_encoding"])
            
            # 如果自动检测失败，使用配置中的默认值
            if data_start_row == 0 and not detected_columns:
                data_start_row = config.DATA_PROCESSING_SETTINGS["csv_header_row"]
                logger.warning(f"Using default header row: {data_start_row}")
            
            # 读取CSV文件
            df = pd.read_csv(
                file_path, 
                encoding=config.DATA_PROCESSING_SETTINGS["csv_encoding"], 
                header=data_start_row
            )
            
            # 清理列名：去除前后空格和不可见字符
            df.columns = df.columns.str.strip()
            logger.info(f"Columns found: {list(df.columns)}")
            
            # 检查必要的列是否存在
            required_columns = ['日期', '时间']
            if not all(col in df.columns for col in required_columns):
                logger.warning(f"File {file_path} missing required columns, skipping")
                continue
                
            # 合并日期和时间列
            try:
                df['datetime'] = pd.to_datetime(
                    df['日期'].astype(str) + ' ' + df['时间'].astype(str), 
                    errors='coerce'
                )
            except Exception as e:
                logger.error(f"Error parsing datetime: {str(e)}")
                continue
            
            # 添加区域列
            df['district'] = district
            
            # 添加adcode
            adcode = district_adcode_map.get(district)
            if adcode is None:
                missing_districts.append(district)
                logger.warning(f"District '{district}' not found in GeoJSON")
                continue
            
            df['adcode'] = adcode
            
            # 查找风速列
            wind_col = None
            for col in config.DATA_PROCESSING_SETTINGS["possible_wind_columns"]:
                if col in df.columns:
                    wind_col = col
                    break
            
            if wind_col is None:
                # 如果没有找到标准列名，尝试查找包含"风速"的列
                wind_cols = [col for col in df.columns if '风速' in col]
                if wind_cols:
                    wind_col = wind_cols[0]
                    logger.info(f"Using alternative wind column: {wind_col}")
                else:
                    logger.warning(f"File {file_path} does not contain wind speed column, skipping")
                    continue
            
            # 重命名风速列
            df = df.rename(columns={wind_col: 'wind_speed'})
            
            # 转换风速列为数值类型
            df['wind_speed'] = pd.to_numeric(df['wind_speed'], errors='coerce')
            
            # 只保留需要的列
            df = df[['datetime', 'district', 'adcode', 'wind_speed']].dropna()
            
            # 打印加载统计
            logger.info(f"Records loaded: {len(df)}, Time range: {df['datetime'].min()} to {df['datetime'].max()}")
            if len(df) > 0:
                logger.info(f"Wind speed range: {df['wind_speed'].min():.2f} - {df['wind_speed'].max():.2f} m/s")
            
            all_data.append(df)
            processed_files += 1
            
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # 合并所有数据
    if all_data:
        full_df = pd.concat(all_data, ignore_index=True)
    else:
        full_df = pd.DataFrame(columns=['datetime', 'district', 'adcode', 'wind_speed'])
    
    # 打印最终统计
    if not full_df.empty:
        logger.info("Data loading completed:")
        logger.info(f"Total records: {len(full_df)}")
        logger.info(f"Files successfully loaded: {processed_files}/{len(district_files)}")
        logger.info(f"Districts included: {full_df['district'].nunique()}")
        logger.info(f"Time range: {full_df['datetime'].min()} to {full_df['datetime'].max()}")
        logger.info(f"Wind speed range: {full_df['wind_speed'].min():.2f} - {full_df['wind_speed'].max():.2f} m/s")
        
        # 打印缺失区域
        if missing_districts:
            logger.warning(f"Districts not matched in GeoJSON: {', '.join(missing_districts)}")
    else:
        logger.error("No valid data loaded")
    
    return full_df