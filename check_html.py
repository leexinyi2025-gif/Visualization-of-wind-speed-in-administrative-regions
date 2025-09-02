# check_html.py
import os

def check_html_file(file_path):
    """检查HTML文件的基本信息"""
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return
    
    file_size = os.path.getsize(file_path)
    print(f"文件大小: {file_size / (1024*1024):.2f} MB")
    
    # 读取文件前几行
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = []
        for i in range(10):
            line = f.readline()
            if not line:
                break
            lines.append(line)
    
    print("\n文件前10行:")
    for i, line in enumerate(lines):
        print(f"{i+1}: {line.strip()}")
    
    # 检查是否包含Plotly相关代码
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read(5000)  # 只读取前5000个字符
    
    if 'Plotly' in content:
        print("\n✓ 文件包含Plotly代码")
    else:
        print("\n✗ 文件不包含Plotly代码")
    
    if 'mapbox' in content.lower():
        print("✓ 文件包含mapbox代码")
    else:
        print("✗ 文件不包含mapbox代码")
    
    # 检查是否包含GeoJSON数据
    if 'geojson' in content.lower():
        print("✓ 文件包含GeoJSON数据")
    else:
        print("✗ 文件不包含GeoJSON数据")

if __name__ == "__main__":
    check_html_file("beijing_wind_speed_map.html")