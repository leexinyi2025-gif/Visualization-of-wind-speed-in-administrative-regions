"""GeoJSON处理模块"""
import json
import logging
import numpy as np

logger = logging.getLogger(__name__)

def load_geojson(file_path):
    """加载GeoJSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading GeoJSON file {file_path}: {str(e)}")
        raise

def calculate_polygon_area(coords):
    """使用鞋带公式计算多边形面积"""
    x = coords[:, 0]
    y = coords[:, 1]
    return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))

def calculate_polygon_centroid(coords):
    """计算多边形的质心"""
    area = calculate_polygon_area(coords)
    if area == 0:
        return np.mean(coords, axis=0)
    
    x = coords[:, 0]
    y = coords[:, 1]
    
    cx = np.sum((x + np.roll(x, 1)) * (x * np.roll(y, 1) - np.roll(x, 1) * y)) / (6 * area)
    cy = np.sum((y + np.roll(y, 1)) * (x * np.roll(y, 1) - np.roll(x, 1) * y)) / (6 * area)
    
    return np.array([cx, cy])

def calculate_centroid(geometry):
    """计算几何图形的质心"""
    try:
        if geometry['type'] == 'Point':
            return tuple(geometry['coordinates'])
            
        elif geometry['type'] == 'MultiPoint':
            coords = np.array(geometry['coordinates'])
            return tuple(np.mean(coords, axis=0))
            
        elif geometry['type'] == 'LineString':
            coords = np.array(geometry['coordinates'])
            return tuple(np.mean(coords, axis=0))
            
        elif geometry['type'] == 'MultiLineString':
            all_coords = []
            for line in geometry['coordinates']:
                all_coords.extend(line)
            coords = np.array(all_coords)
            return tuple(np.mean(coords, axis=0))
            
        elif geometry['type'] == 'Polygon':
            # 只使用外环
            coords = np.array(geometry['coordinates'][0])
            centroid = calculate_polygon_centroid(coords)
            return tuple(centroid)
            
        elif geometry['type'] == 'MultiPolygon':
            # 计算多个多边形的加权质心
            total_area = 0
            weighted_centroids = np.zeros(2)
            
            for polygon in geometry['coordinates']:
                # 只使用外环
                coords = np.array(polygon[0])
                centroid = calculate_polygon_centroid(coords)
                area = calculate_polygon_area(coords)
                
                total_area += area
                weighted_centroids += area * centroid
            
            if total_area > 0:
                centroid = weighted_centroids / total_area
                return tuple(centroid)
            else:
                return tuple(np.mean(coords, axis=0))
                
        else:
            # 对于其他几何类型，返回第一个点
            if 'coordinates' in geometry and len(geometry['coordinates']) > 0:
                return tuple(geometry['coordinates'][0])
            return (0, 0)
            
    except Exception as e:
        logger.error(f"Error calculating centroid: {str(e)}")
        # 回退到简单计算方法
        if 'coordinates' in geometry and len(geometry['coordinates']) > 0:
            return tuple(geometry['coordinates'][0])
        return (0, 0)

def standardize_district_name(name):
    """标准化区名，移除'区'字"""
    import re
    return re.sub(r'区$', '', name)

def create_district_adcode_map(geojson):
    """创建区名到adcode的映射"""
    district_adcode_map = {}
    
    logger.info("Parsing GeoJSON features:")
    
    for feature in geojson['features']:
        props = feature['properties']
        adcode = props.get('adcode')
        name = props.get('name')
        
        if not adcode or not name:
            logger.warning(f"Feature missing adcode or name property - {props}")
            continue
            
        # 标准化区名
        standardized_name = standardize_district_name(name)
        
        # 特殊处理：西城区 -> 西城
        if standardized_name == "西城":
            standardized_name = "西城"
        
        logger.debug(f"adcode: {adcode}, Original name: {name}, Standardized name: {standardized_name}")
        district_adcode_map[standardized_name] = adcode
    
    logger.info("District mapping completed")
    return district_adcode_map

def get_adcode_centroids(geojson):
    """获取所有区域的中心点坐标"""
    adcode_centroids = {}
    
    for feature in geojson['features']:
        adcode = feature['properties'].get('adcode')
        if adcode:
            centroid = calculate_centroid(feature['geometry'])
            if centroid:
                adcode_centroids[adcode] = centroid
    
    return adcode_centroids