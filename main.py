# Entry point of the application
import os 
import pandas as pd
import geopandas as gpd
import json 
import streamlit as st
import folium 
from streamlit_folium import st_folium
from langchain.callbacks.tracers import LangChainTracer
from langchain.agents import create_sql_agent, AgentType
from config import connect_to_db
from langchain_groq import ChatGroq
from dotenv import load_dotenv



custom_prompt = 




load_dotenv()
st.set_page_config(
    page_title="FindinGeo",
    layout="wide"
)

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

def main():

    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """, unsafe_allow_html=True)

    st.title("FindinGeo👀")

    db = connect_to_db()
    llm = ChatGroq(
        api_key=os.getenv("API_KEY_GROQ"),
        model="qwen-2.5-coder-32b",
        temperature=0.0,
        max_tokens=512,
        prompt=custom_prompt
    )
    
    # LangSmith tracer for debugging/monitoring
    tracer = LangChainTracer(project_name="FindinGeo")

    agent = create_sql_agent(
        llm=llm,
        db=db,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True
    )

    user_query = st.text_input("Ask me a question:")

    if st.button("Submit"):
        if user_query.strip():
            try:
                raw_result = agent.run(user_query, callbacks=[tracer])
                display_results(raw_result)
            except Exception as e:
                st.error("An error occurred while processing your query: " + str(e))
        else:
            st.warning("Please enter a question.")

if __name__ == "__main__":
    main()