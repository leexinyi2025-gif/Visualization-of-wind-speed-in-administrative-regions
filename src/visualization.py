"""可视化模块"""
import plotly.graph_objects as go
import numpy as np
import logging

logger = logging.getLogger(__name__)

def create_wind_visualization(df, geojson, config):
    """创建风速可视化（使用等值线图）"""
    if df.empty:
        logger.error("No data available for visualization")
        return go.Figure()
    
    # 获取所有唯一时间点
    unique_times = sorted(df['datetime'].unique())
    
    logger.info(f"Creating visualization - Number of time points: {len(unique_times)}")
    
    # 创建颜色映射
    max_wind = max(df['wind_speed'].max(), 1)  # 确保最大值至少为1
    min_wind = min(df['wind_speed'].min(), 0)  # 确保最小值至少为0
    
    logger.info(f"Wind speed range: {min_wind:.2f} - {max_wind:.2f} m/s")
    
    # 获取区域中心点
    from .geojson_processor import get_adcode_centroids
    adcode_centroids = get_adcode_centroids(geojson)
    
    # 添加初始数据（第一小时）
    initial_data = df[df['datetime'] == unique_times[0]]
    
    if initial_data.empty:
        logger.error(f"No data for first time point {unique_times[0]}")
        return go.Figure()
    
    logger.debug(f"Initial data districts: {initial_data['district'].unique()}")
    
    fig = go.Figure()
    
    # 添加区域填充层 - 使用adcode作为唯一标识符
    fig.add_trace(go.Choroplethmapbox(
        geojson=geojson,
        locations=initial_data['adcode'],
        z=initial_data['wind_speed'],
        featureidkey="properties.adcode",  # 关键修改：使用adcode作为标识符
        colorscale=config.VISUALIZATION_SETTINGS["colorscale"],
        zmin=min_wind,
        zmax=max_wind,
        marker_opacity=config.VISUALIZATION_SETTINGS["opacity"],
        marker_line_width=config.VISUALIZATION_SETTINGS["line_width"],
        marker_line_color=config.VISUALIZATION_SETTINGS["line_color"],
        text=initial_data['district'] + '<br>Wind Speed: ' + initial_data['wind_speed'].round(2).astype(str) + ' m/s',
        hoverinfo='text',
        name='Wind Speed',
        colorbar=dict(
            title='Wind Speed (m/s)',
            thickness=20,
            tickvals=np.linspace(min_wind, max_wind, 6),
            tickformat=".1f"
        )
    ))
    
    # 添加风速文本层
    initial_lons = []
    initial_lats = []
    initial_texts = []
    
    for _, row in initial_data.iterrows():
        adcode = row['adcode']
        centroid = adcode_centroids.get(adcode)
        if centroid:
            lon, lat = centroid
            initial_lons.append(lon)
            initial_lats.append(lat)
            initial_texts.append(f"{row['wind_speed']:.1f} m/s")
    
    fig.add_trace(go.Scattermapbox(
        lon=initial_lons,
        lat=initial_lats,
        mode='text',
        text=initial_texts,
        textfont=dict(
            size=config.VISUALIZATION_SETTINGS["text_font_size"],
            color=config.VISUALIZATION_SETTINGS["text_font_color"],
            family=config.VISUALIZATION_SETTINGS["text_font_family"]
        ),
        hoverinfo='none',
        showlegend=False
    ))
    
    # 创建时间滑块
    steps = create_slider_steps(df, unique_times, adcode_centroids)
    sliders = [dict(
        active=0,
        currentvalue={
            "prefix": "Time: ",
            "font": {"size": 14, "color": "#333"},
            "xanchor": "right"
        },
        pad={"t": 50, "b": 10},
        len=0.9,
        x=0.05,
        steps=steps,
        transition=dict(duration=300))
    ]
    
    # 添加播放按钮
    updatemenus = create_playback_buttons()
    
    # 创建动画帧
    frames = create_animation_frames(df, unique_times, adcode_centroids, config, min_wind, max_wind, steps)
    fig.frames = frames
    
    # 设置地图布局
    setup_map_layout(fig, geojson, config, sliders, updatemenus, df, unique_times)
    
    return fig

def create_slider_steps(df, unique_times, adcode_centroids):
    """创建时间滑块步骤"""
    steps = []
    
    for i, time_point in enumerate(unique_times):
        # 获取当前时间点的数据
        current_data = df[df['datetime'] == time_point]
        
        # 准备文本数据
        text_lons = []
        text_lats = []
        text_values = []
        
        for _, row in current_data.iterrows():
            adcode = row['adcode']
            centroid = adcode_centroids.get(adcode)
            if centroid:
                lon, lat = centroid
                text_lons.append(lon)
                text_lats.append(lat)
                text_values.append(f"{row['wind_speed']:.1f} m/s")
        
        # 创建滑块步长
        step = dict(
            method='update',
            args=[{
                'z': [current_data['wind_speed']],
                'locations': [current_data['adcode']],
                'text': [current_data['district'] + '<br>Wind Speed: ' + current_data['wind_speed'].round(2).astype(str) + ' m/s']
            }, {
                'lon': [text_lons],
                'lat': [text_lats],
                'text': [text_values]
            }],
            label=time_point.strftime('%m-%d %H:%M')
        )
        steps.append(step)
    
    return steps

def create_playback_buttons():
    """创建播放控制按钮"""
    return [
        dict(
            type="buttons",
            showactive=False,
            buttons=[
                dict(
                    label="Play",
                    method="animate",
                    args=[
                        None, 
                        {
                            "frame": {"duration": 300, "redraw": True},
                            "fromcurrent": True,
                            "transition": {"duration": 300, "easing": "quadratic-in-out"}
                        }
                    ]
                ),
                dict(
                    label="Pause",
                    method="animate",
                    args=[
                        [None],
                        {
                            "frame": {"duration": 0, "redraw": False},
                            "mode": "immediate",
                            "transition": {"duration": 0}
                        }
                    ]
                )
            ],
            direction="left",
            pad={"r": 10, "t": 10},
            x=0.1,
            xanchor="right",
            y=0,
            yanchor="top"
        )
    ]

def create_animation_frames(df, unique_times, adcode_centroids, config, min_wind, max_wind, steps):
    """创建动画帧"""
    frames = []
    
    for i, time_point in enumerate(unique_times):
        current_data = df[df['datetime'] == time_point]
        if not current_data.empty:
            # 创建包含时间信息的帧名称
            frame_name = time_point.strftime('%Y-%m-%d %H:%M')
            
            # 准备文本数据
            text_lons = []
            text_lats = []
            text_values = []
            
            for _, row in current_data.iterrows():
                adcode = row['adcode']
                centroid = adcode_centroids.get(adcode)
                if centroid:
                    lon, lat = centroid
                    text_lons.append(lon)
                    text_lats.append(lat)
                    text_values.append(f"{row['wind_speed']:.1f} m/s")
            
            # 创建填充层
            choropleth_trace = go.Choroplethmapbox(
                z=current_data['wind_speed'],
                locations=current_data['adcode'],
                text=current_data['district'] + '<br>Wind Speed: ' + current_data['wind_speed'].round(2).astype(str) + ' m/s',
                featureidkey="properties.adcode",
                colorscale=config.VISUALIZATION_SETTINGS["colorscale"],
                zmin=min_wind,
                zmax=max_wind,
                marker_opacity=config.VISUALIZATION_SETTINGS["opacity"],
                marker_line_width=config.VISUALIZATION_SETTINGS["line_width"],
                marker_line_color=config.VISUALIZATION_SETTINGS["line_color"],
                showscale=False
            )
            
            # 创建文本层
            text_trace = go.Scattermapbox(
                lon=text_lons,
                lat=text_lats,
                mode='text',
                text=text_values,
                textfont=dict(
                    size=config.VISUALIZATION_SETTINGS["text_font_size"],
                    color=config.VISUALIZATION_SETTINGS["text_font_color"],
                    family=config.VISUALIZATION_SETTINGS["text_font_family"]
                ),
                hoverinfo='none',
                showlegend=False
            )
            
            frames.append(
                go.Frame(
                    data=[choropleth_trace, text_trace],
                    name=frame_name,
                    layout=dict(
                        # 添加时间滑块到帧
                        sliders=[dict(
                            active=i,
                            steps=steps,
                            currentvalue={
                                "prefix": "Time: ",
                                "font": {"size": 14, "color": "#333"},
                                "xanchor": "right"
                            }
                        )]
                    )
                )
            )
            
        # 每处理50个时间点打印一次进度
        if i % 50 == 0:
            logger.info(f"Creating frame {i+1}/{len(unique_times)} - {time_point}")
    
    return frames

def setup_map_layout(fig, geojson, config, sliders, updatemenus, df, unique_times):
    """设置地图布局"""
    fig.update_layout(
        title={
            'text': 'Beijing District Wind Speed Monitoring',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24, 'color': '#1f77b4'}
        },
        autosize=True,
        height=800,
        sliders=sliders,
        updatemenus=updatemenus,
        mapbox=dict(
            style=config.VISUALIZATION_SETTINGS["map_style"],
            zoom=config.VISUALIZATION_SETTINGS["map_zoom"],
            center=config.VISUALIZATION_SETTINGS["map_center"],
            layers=[{
                "source": geojson,
                "type": "line",
                "color": "rgba(100, 100, 100, 0.5)",
                "line": {"width": 1}
            }],
            # 启用地图缩放功能
            bearing=0,
            pitch=0,
            accesstoken=None,
            uirevision=True
        ),
        margin={"r":20,"t":100,"l":20,"b":20},
        plot_bgcolor='rgba(240, 240, 240, 0.9)',
        paper_bgcolor='rgba(240, 240, 240, 0.9)',
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Arial"
        )
    )
    
    # 添加副标题和数据源信息
    fig.add_annotation(
        text="Data Source: Beijing Meteorological Monitoring Stations",
        xref="paper", yref="paper",
        x=0.5, y=-0.05,
        showarrow=False,
        font=dict(size=12, color="#666")
    )
    
    if not df.empty:
        fig.add_annotation(
            text=f"Data Time Range: {df['datetime'].min().strftime('%Y-%m-%d')} to {df['datetime'].max().strftime('%Y-%m-%d')}",
            xref="paper", yref="paper",
            x=0.5, y=-0.08,
            showarrow=False,
            font=dict(size=12, color="#666")
        )
    
    # 添加时间显示框
    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.5, y=1.05,
        showarrow=False,
        text=unique_times[0].strftime('%Y-%m-%d %H:%M'),
        font=dict(size=16, color="#333"),
        bgcolor="rgba(255, 255, 255, 0.7)",
        bordercolor="#AAA",
        borderwidth=1,
        borderpad=4
    )