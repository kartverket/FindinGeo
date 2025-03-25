import json 
import streamlit as st
import folium
from streamlit_folium import st_folium
import geopandas as gpd
import pandas as pd
import re
import sys


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

def strip_ansi_codes(text):
    """Strip ANSI codes from text"""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


class StreamlitLogger:
    def __init__(self, terminal_placeholder, original_stdout):
        self.log_buffer = []
        self._original_stdout = original_stdout
        self.terminal_placeholder = terminal_placeholder
        
    def write(self, text):
        self._original_stdout.write(text)  # write to terminal
        if text.strip():  # Only add non-empty text
            clean_text = strip_ansi_codes(text)
            self.log_buffer.append(clean_text)
            
            # Create a terminal-like display
            terminal_html = f"""
            <div style="background-color: #f0f0f0; color: #333; 
                      padding: 10px; font-family: monospace; 
                      font-size: 0.85em;
                      height: 150px; overflow-y: auto; 
                      border: 1px solid #ddd;
                      border-radius: 5px; white-space: pre-wrap;">
                {''.join(self.log_buffer)}
            </div>
            """
            self.terminal_placeholder.markdown(terminal_html, unsafe_allow_html=True)
    
    def flush(self):
        self._original_stdout.flush()


def handle_agent_interaction(agent, user_query, tracer):
    agent_output_container = st.container()
    
    try:
        # Create a placeholder for the terminal-like output
        with agent_output_container:
            terminal_placeholder = st.empty()
            
            if 'original_stdout' not in st.session_state:
                st.session_state.original_stdout = sys.stdout
                
            # Reset log buffer on each new query
            streamlit_logger = StreamlitLogger(terminal_placeholder, st.session_state.original_stdout)
            
            sys.stdout = streamlit_logger
            
            # Mark that we need to reset on next run
            st.session_state.needs_reset = True
            
            try:
                raw_result = agent.invoke({"input": user_query}, callbacks=[tracer])
                
                # handle different response formats
                if isinstance(raw_result, dict) and "output" in raw_result:
                    result_text = raw_result["output"]
                else:
                    # Fallback if the output is not in the expected format
                    result_text = str(raw_result)
                
                # Check for timeout/iteration limit messages
                if "Agent stopped due to iteration limit or time limit" in result_text:
                    st.warning("The query was too complex to process in the allotted time. Try simplifying your question.")
                # Handle simple "I don't know" responses
                elif result_text.strip() == "I don't know":
                    st.info("The agent couldn't find an answer to your question. Try rephrasing or asking about something else.")
                # Check for common error patterns in the result
                elif "insufficient information" in result_text.lower() or "error" in result_text.lower():
                    # Extract the error message if possible
                    if "{\"error\":" in result_text:
                        error_match = re.search(r'{"error":\s*"([^"]+)"}', result_text)
                        if error_match:
                            error_message = error_match.group(1)
                            st.error(f"Database Error: {error_message}")
                    # If we couldn't extract a specific error but error keywords are present
                    elif "Final Answer is not a valid tool" in result_text:
                        # This indicates the agent is trying to return an error message
                        error_content = re.search(r'Action Input: (.+?)Final Answer is not a valid tool', result_text, re.DOTALL)
                        if error_content:
                            try:
                                error_json = json.loads(error_content.group(1).strip())
                                if "error" in error_json:
                                    st.error(f"Query Error: {error_json['error']}")
                            except:
                                st.warning("The agent couldn't find the necessary information to answer your question.")
                        else:
                            st.warning("The agent couldn't complete the query properly.")
                    else:
                        # Still try to display results for other error cases
                        display_results(result_text)
                else:
                    # Only call display_results for proper results
                    display_results(result_text)
                
            except Exception as agent_err:
                # Display a more user-friendly error
                error_message = str(agent_err)
                
                # If it's a parsing error, provide a simplified message
                if "output parsing error" in error_message.lower():
                    st.error("The agent encountered difficulty formulating a proper response. Try rephrasing your question to be more specific.")
                    # Log the full error for debugging
                    print(f"Original error: {error_message}")
                else:
                    st.error(f"An error occurred: {error_message}")
            finally:
                sys.stdout = st.session_state.original_stdout
                
    except Exception as e:

        sys.stdout = st.session_state.original_stdout
        st.error("An unexpected error occurred: " + str(e))


def display_results(raw_result):
    parsed = None
    try:
        parsed = json.loads(raw_result)
    except Exception as e:
        pass
    
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
        st.write("**Result:**")
        st.code(raw_result, language="plaintext")
