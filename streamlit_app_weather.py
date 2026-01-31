import streamlit as st
import requests
import pandas as pd
import pydeck as pdk

# --- ページ設定 ---
st.set_page_config(page_title="日本全国気温 3D Map", layout="wide")
st.title("🇯🇵 日本主要都市の現在の気温 3Dマップ")

# 全国の主要都市データ
cities = {
    '札幌': {'lat': 43.0642, 'lon': 141.3469},
    '仙台': {'lat': 38.2682, 'lon': 140.8694},
    '東京': {'lat': 35.6895, 'lon': 139.6917},
    '金沢': {'lat': 36.5613, 'lon': 136.6562},
    '名古屋': {'lat': 35.1815, 'lon': 136.9066},
    '大阪': {'lat': 34.6937, 'lon': 135.5023},
    '広島': {'lat': 34.3853, 'lon': 132.4553},
    '高知': {'lat': 33.5597, 'lon': 133.5311},
    '福岡': {'lat': 33.5904, 'lon': 130.4017},
    '鹿児島': {'lat': 31.5600, 'lon': 130.5580},
    '那覇': {'lat': 26.2124, 'lon': 127.6809}
}

@st.cache_data(ttl=600)
def fetch_weather_data():
    weather_info = []
    BASE_URL = 'https://api.open-meteo.com/v1/forecast'
    
    for city, coords in cities.items():
        params = {'latitude': coords['lat'], 'longitude': coords['lon'], 'current': 'temperature_2m'}
        try:
            res = requests.get(BASE_URL, params=params).json()
            temp = res['current']['temperature_2m']
            
            # 色の計算：簡易的に 気温が高い=赤(R)を増やす、低い=青(B)を増やす
            # [R, G, B, 透明度]
            r = int(min(max((temp + 10) * 5, 0), 255)) 
            b = 255 - r
            
            weather_info.append({
                'City': city, 'lat': coords['lat'], 'lon': coords['lon'], 
                'Temperature': temp, 'elevation': abs(temp) * 5000,
                'color': [r, 150, b, 200] # 明るめの色合い
            })
        except:
            pass
    return pd.DataFrame(weather_info)

df = fetch_weather_data()

# --- レイアウト ---
col1, col2 = st.columns([1, 3])

with col1:
    st.dataframe(df[['City', 'Temperature']], hide_index=True)
    if st.button('更新'):
        st.cache_data.clear()
        st.rerun()

with col2:
    view_state = pdk.ViewState(latitude=35.0, longitude=137.0, zoom=4.5, pitch=50)

    layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        get_position='[lon, lat]',
        get_elevation='elevation',
        radius=25000,
        get_fill_color='color',
        pickable=True,
        auto_highlight=True,
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "{City}: {Temperature}°C"}
    ))
