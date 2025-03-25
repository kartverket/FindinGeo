import json 
import streamlit as st
import folium
from streamlit_folium import st_folium
import geopandas as gpd
import pandas as pd


st.set_page_config(
    page_title="FindinGeo",
    layout="wide"
)

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)


def display_results(raw_result):
    """
    Attempts to parse raw_result as JSON.
    If successful, displays it as a DataFrame and, if geometry is found, also shows a map.
    Otherwise, shows the raw result in a code block.
    """
    parsed = None
    try:
        parsed = json.loads(raw_result)
    except Exception as e:
        st.error("Could not parse result as JSON. Showing raw output instead.")
    
    if parsed:

        if isinstance(parsed, list):
            df = pd.DataFrame(parsed)
            st.write("**Parsed as DataFrame (list):**")
            st.dataframe(df, use_container_width=True)

        elif isinstance(parsed, dict):
            df = pd.json_normalize(parsed, max_level=1)
            st.write("**Parsed as DataFrame (dict):**")
            st.dataframe(df, use_container_width=True)
            
            if "geometry" in parsed:
                try:
                    gdf = gpd.GeoDataFrame.from_features(parsed["geometry"])
                    if not gdf.empty:
                        center_lat = gdf.geometry.centroid.y.mean()
                        center_lon = gdf.geometry.centroid.x.mean()
                        m = folium.Map(location=[center_lat, center_lon], zoom_start=8)
                        folium.GeoJson(gdf).add_to(m)
                        st_folium(m, width=900, height=600)
                except Exception as map_err:
                    st.error("Error displaying geometry on map: " + str(map_err))
        else:
            st.write("**Parsed object:**", parsed)
    else:
        st.write("**Raw Result:**")
        st.code(raw_result, language="plaintext")
