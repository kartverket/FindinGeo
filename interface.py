import json
import streamlit as st
import folium
from streamlit_folium import st_folium
import geopandas as gpd
import pandas as pd
import re
import sys
import os
import traceback
import io # for StringIO
import pandas.api.types

st.set_page_config(
    page_title="FindinGeo",
    layout="wide"
)

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stMapContainer [title] {pointer-events: none;}
    </style>
    """, unsafe_allow_html=True)

def strip_ansi_codes(text):
    """Strip ANSI codes from text"""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


class StreamlitLogger(io.StringIO):
    def __init__(self, terminal_placeholder, original_stdout):
        super().__init__()
        self.log_buffer = []
        self._original_stdout = original_stdout
        self.terminal_placeholder = terminal_placeholder

    def write(self, text):
        self._original_stdout.write(text)
        if text.strip():
            clean_text = strip_ansi_codes(text)
            self.log_buffer.append(clean_text)
            if len(self.log_buffer) > 1000:
                 self.log_buffer = self.log_buffer[-1000:]
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
    """Handles the interaction with the Langchain agent and catches OutputParsingError."""
    terminal_placeholder = st.empty()
    results_placeholder = st.container()

    try:
        if 'original_stdout' not in st.session_state:
            st.session_state.original_stdout = sys.stdout

        streamlit_logger = StreamlitLogger(terminal_placeholder, st.session_state.original_stdout)
        sys.stdout = streamlit_logger
        st.session_state.needs_reset = True # Flag to ensure stdout is restored

        streamlit_logger.write(f"Agent thinking about: '{user_query}'...\n")

        try:
            raw_result = agent.invoke({"input": user_query}, callbacks=[tracer])
            
            with results_placeholder:
                display_results(raw_result)

        except Exception as agent_run_err:
            error_message_str = str(agent_run_err)
            extracted_llm_output = None
            
            parse_error_match = re.search(r"Could not parse LLM output: `(.*?)`", error_message_str, re.DOTALL)

            if parse_error_match:
                extracted_llm_output = parse_error_match.group(1)
                streamlit_logger.write(f"\nCaught OutputParsingError. Attempting to display extracted LLM output:\n---\n{extracted_llm_output}\n---\n")
                with results_placeholder:
                    st.error("Agent encountered an Output Parsing Error, but the raw output is given below:")
                    display_results(extracted_llm_output)
            else:
                with results_placeholder:
                    st.error(f"An error occurred during agent execution: {error_message_str}")
                    st.write("Please review the terminal output above for details.")
                    print(f"\nFull traceback for agent execution error:\n{traceback.format_exc()}")

    except Exception as outer_err:
        with results_placeholder:
            st.error(f"An unexpected application error occurred: {outer_err}")
            st.write("Please try again or check the console for details.")
            print(f"\nFull traceback for unexpected application error:\n{traceback.format_exc()}")


    finally:
        if 'original_stdout' in st.session_state and sys.stdout != st.session_state.original_stdout:
            sys.stdout = st.session_state.original_stdout
        st.session_state.needs_reset = False


def clean_sql_query(query_string):
    """Clean a SQL query string by removing markdown formatting (like ```sql) and trailing whitespace/semicolon."""
    if not query_string:
        return query_string

    query_string = str(query_string)
    query_string = re.sub(r'^```sql\s*', '', query_string, flags=re.DOTALL)
    query_string = re.sub(r'\s*```$', '', query_string, flags=re.DOTALL)
    query_string = re.sub(r'`([^`]*)`', r'\1', query_string)
    # Also strip trailing whitespace and semicolons for cleaner SQL
    query_string = query_string.strip()
    if query_string.endswith(';'):
        query_string = query_string[:-1].strip()

    return query_string


def display_results(raw_result):
    result_text = raw_result.get("output", str(raw_result)) if isinstance(raw_result, dict) else str(raw_result)

    # Variables to hold the parsed results
    narrative_answer = None
    query_for_display_and_map = None # This will hold the determined SQL query

    # --- Attempt 1: Directly parse the [SQL Query: ...] Narrative format anywhere in the text ---
    direct_bracket_match = re.search(r'\[SQL Query:\s*(.*?)]\s*(.*)', result_text, re.DOTALL)

    if direct_bracket_match:
        # Found the [SQL Query: ...] Narrative format directly
        query_for_display_and_map = clean_sql_query(direct_bracket_match.group(1).strip())
        narrative_answer = direct_bracket_match.group(2).strip()

        st.write("**Final Answer:**")
        st.write(narrative_answer)

    else:
        # --- Attempt 2: If the direct format wasn't found, look for 'Final Answer:' section ---
        final_answer_content = None
        final_answer_match = re.search(r'Final Answer:\s*(.*?)(?=\nFinished chain|\Z)', result_text, re.DOTALL)
        if final_answer_match:
            final_answer_content = final_answer_match.group(1).strip()

        st.write("**Final Answer:**")

        if final_answer_content:
             # Check if the content *within* Final Answer is also [SQL Query: ...] Narrative
             parts_within_final_answer = re.search(r'^\s*\[SQL Query:\s*(.*?)]\s*(.*)$', final_answer_content, re.DOTALL)

             if parts_within_final_answer:
                 # Found [SQL Query: ...] Narrative *within* the Final Answer content
                 query_for_display_and_map = clean_sql_query(parts_within_final_answer.group(1).strip())
                 narrative_answer = parts_within_final_answer.group(2).strip()
                 st.write(narrative_answer)
                 # Optional: st.caption(f"Query used for answer: `{query_for_display_and_map}`")

             else:
                 # Final Answer found, but not in the [SQL Query: ...] format. Try JSON or plain text.
                 try:
                    parsed_final_answer = json.loads(final_answer_content)
                    if isinstance(parsed_final_answer, (list, dict)):
                         try:
                            if isinstance(parsed_final_answer, list):
                                df = pd.DataFrame(parsed_final_answer)
                            else: # dict
                                df = pd.json_normalize(parsed_final_answer, max_level=1)

                            st.dataframe(df, use_container_width=True)
                            narrative_answer = "Data Table/Object:" # Label for non-text answers
                         except Exception as df_err:
                            st.warning(f"Could not display JSON as DataFrame: {df_err}")
                            st.json(parsed_final_answer)
                            narrative_answer = "JSON Data:"
                    else:
                         st.write(parsed_final_answer)
                         narrative_answer = "Result:" # Label for simple parsed objects

                 except json.JSONDecodeError:
                     # Not JSON, display as plain text
                     st.write(final_answer_content)
                     narrative_answer = final_answer_content # The answer is the text
                     st.warning("Final answer format was unexpected. Displaying raw output.")
                 except Exception as e:
                     st.error(f"Error processing final answer data: {e}")
                     st.write(final_answer_content) # Fallback


        else:
            # --- Attempt 3: If 'Final Answer:' section not found, display raw and look for trace SQL ---
            st.text_area("Raw Output", result_text, height=150)
            narrative_answer = "Could not extract final answer from agent output."



    if not query_for_display_and_map:
         # If no query was found in any 'Final Answer' related parsing, try extracting from verbose trace
         sql_executed_trace_match = re.search(r'SQL [Qq]uery:?\s*(.*?)(?=\nResult:|\nFinal Answer:|\n\n|\Z)', result_text, re.DOTALL)
         if sql_executed_trace_match:
             query_for_display_and_map = clean_sql_query(sql_executed_trace_match.group(1).strip())

    st.write("**Executed SQL Query:**")
    if query_for_display_and_map:
        st.code(query_for_display_and_map, language="sql")
        st.session_state.last_sql_query = query_for_display_and_map # Store for map logic below
    else:
        st.info("Could not reliably extract the executed SQL query.")
        st.session_state.last_sql_query = None # Ensure session state is None


    query_for_map = st.session_state.last_sql_query

    if query_for_map:
         if is_aggregation_query(query_for_map):
             transformed_query = transform_aggregate_query(query_for_map)
             if transformed_query:
                 st.write("**Using the followowing query for mapping:**")
                 st.code(transformed_query, language="sql")
                 st.write("**Map View:**")
                 display_map(transformed_query) # Use transformed query for map
             else:
                 pass
         else:
             pass
    else:
         st.info("No executable SQL query found for map display.")
         
         
def is_aggregation_query(sql_query):
    """Determine if a query is an aggregation query that might not return feature geometry by default."""
    if not sql_query:
        return False

    sql_query = clean_sql_query(sql_query)

    if re.search(r'SELECT\s+COUNT\(\*?\s*[^)]*\)\s+FROM', sql_query, re.IGNORECASE) and not re.search(r'GROUP BY', sql_query, re.IGNORECASE):
         return True

    if re.search(r'SELECT\s+(SUM|AVG|MIN|MAX)\([^,]*\)\s+FROM', sql_query, re.IGNORECASE) and not re.search(r'GROUP BY', sql_query, re.IGNORECASE):
         return True

    if re.search(r'GROUP BY', sql_query, re.IGNORECASE) and re.search(r'(COUNT|SUM|AVG|MIN|MAX)\(', sql_query, re.IGNORECASE):
         return True

    return False


def transform_aggregate_query(sql_query):
    """Transform specific types of aggregation queries (like COUNT, MIN/MAX without GROUP BY) to also retrieve mappable geographic data from the underlying table."""
    if not sql_query:
        return None

    sql_query = clean_sql_query(sql_query)

    clean_query = re.sub(r'--.*$', '', sql_query, flags=re.MULTILINE)
    clean_query = re.sub(r'/\*.*?\*/', '', clean_query, flags=re.DOTALL)
    clean_query = ' '.join(clean_query.split())

    # Case 1: Handle simple COUNT(*) or COUNT(column) queries without GROUP BY
    count_match = re.search(r'SELECT\s+COUNT\(\*?\s*[^)]*\)\s+FROM\s+([^\s;]+)', clean_query, re.IGNORECASE)
    if count_match and not re.search(r'GROUP BY', clean_query, re.IGNORECASE):
         table_name = count_match.group(1)

         where_part = ''
         where_match = re.search(r'(WHERE\s+.+?)(?:ORDER BY|GROUP BY|LIMIT|;|$)', clean_query, re.IGNORECASE | re.DOTALL)
         if where_match:
             where_part = ' ' + where_match.group(1)

         # Construct the new query. Ensure table_name is clean of any trailing garbage.
         clean_table_name = re.sub(r'[^a-zA-Z0-9_"]+$', '', table_name) # Rudimentary cleaning of table name
         new_query = f"SELECT *, COUNT(*) OVER() as total_count FROM {clean_table_name}{where_part}"
         return new_query

    # Case 2: Handle MIN() or MAX() queries without GROUP BY
    min_max_match = re.search(r'SELECT\s+(MIN|MAX)\(([^)]+)\)\s+FROM\s+([^\s;]+)', clean_query, re.IGNORECASE)
    if min_max_match and not re.search(r'GROUP BY', clean_query, re.IGNORECASE):
        agg_func = min_max_match.group(1).upper()
        agg_col = min_max_match.group(2).strip()
        table_name = min_max_match.group(3)

        if agg_func in ('MIN', 'MAX'):
            where_part = ''
            where_match = re.search(r'(WHERE\s+.+?)(?:ORDER BY|GROUP BY|LIMIT|;|$)', clean_query, re.IGNORECASE | re.DOTALL)
            if where_match:
                 where_part = ' ' + where_match.group(1)

            clean_table_name = re.sub(r'[^a-zA-Z0-9_"]+$', '', table_name)

            cte_query = f"""
             WITH agg_value AS (
                 SELECT {agg_func}({agg_col}) as target_value FROM {clean_table_name}
                 {where_part}
             )
             SELECT t.*, '{agg_func}({agg_col})' as aggregation_type, av.target_value as aggregation_value
             FROM {clean_table_name} t, agg_value av
             WHERE t.{agg_col} = av.target_value
             """
            if not re.search(r'LIMIT', cte_query, re.IGNORECASE):
                 cte_query += " LIMIT 10"

            return cte_query

    # Case 3: Complex aggregation queries (GROUP BY or AVG/SUM)
    if re.search(r'GROUP BY', clean_query, re.IGNORECASE) or re.search(r'(AVG|SUM)\(', clean_query, re.IGNORECASE):
         return None

    return None


def convert_dataframe_for_json(gdf):
    """
    Converts a GeoDataFrame to a JSON-serializable format for Folium popups.
    """
    gdf_copy = gdf.copy()
    geometry_col_name = gdf_copy.geometry.name if hasattr(gdf_copy, 'geometry') else None

    for col in gdf_copy.columns:
        if col != geometry_col_name:
            if not pandas.api.types.is_numeric_dtype(gdf_copy[col]) and \
               not pandas.api.types.is_bool_dtype(gdf_copy[col]) and \
               not pandas.api.types.is_string_dtype(gdf_copy[col]):
                try:
                    gdf_copy[col] = gdf_copy[col].astype(str).replace('nan', '', regex=False).replace('NaT', '', regex=False)
                except Exception as e:
                     print(f"Warning: Could not convert column '{col}' to string for JSON: {e}")
                     gdf_copy[col] = gdf_copy[col].apply(lambda x: str(x) if pd.notna(x) else '').astype(str)
            elif pandas.api.types.is_object_dtype(gdf_copy[col]) or pandas.api.types.is_string_dtype(gdf_copy[col]):
                 gdf_copy[col] = gdf_copy[col].replace({pd.NA: '', None: ''}).fillna('').astype(str)

    return gdf_copy


def display_map(query_string):
    """
    Fetches spatial data using the provided SQL query via GeoPandas
    and displays it on a Folium map embedded in Streamlit.
    """
    if not query_string or not query_string.strip():
         st.warning("No valid SQL query provided for map display.")
         return

    query_string = clean_sql_query(query_string)

    try:
        from dotenv import load_dotenv
        load_dotenv()

        conn_string = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"


        gdf = gpd.read_postgis(query_string, conn_string)

        if gdf.empty:
            st.warning("No geographic data found in the results for mapping.")
            return

        if not hasattr(gdf, 'geometry') or gdf.geometry.isna().all():
            st.warning("The result contains no valid geometry data column ('geometry') to display on the map.")
            return

        valid_geoms = gdf.geometry[~gdf.geometry.isna()]
        if valid_geoms.empty:
            st.warning("No valid geometries found to display on the map.")
            return

        try:
             centroid = valid_geoms.unary_union.centroid
             map_location = [centroid.y, centroid.x]
             initial_zoom = 12
        except Exception as e:
             st.warning(f"Could not calculate centroid for map centering. Using a default location. Error: {e}")
             map_location = [59.66, 10.76]
             initial_zoom = 10

        map = folium.Map(location=map_location, zoom_start=initial_zoom, control_scale=True)
        df_json = convert_dataframe_for_json(gdf)
        has_agg_info = 'aggregation_type' in df_json.columns and 'aggregation_value' in df_json.columns

        if has_agg_info:
             def style_function(feature):
                 return {
                     'fillColor': '#ff7800',
                     'color': '#000000',
                     'weight': 2,
                     'fillOpacity': 0.7
                 }
             all_fields = df_json.columns.tolist()
             popup_fields = [f for f in all_fields if f not in ['geometry', 'aggregation_type', 'aggregation_value']]
             popup_fields_with_agg = popup_fields + ['aggregation_type', 'aggregation_value']
             popup_aliases = popup_fields + ['Aggregation Type', 'Value']

             popup = folium.GeoJsonPopup(
                 fields=popup_fields_with_agg,
                 aliases=popup_aliases,
                 localize=True,
                 labels=True,
                 style="background-color: yellow;",
             )
             folium.GeoJson(
                 df_json,
                 style_function=style_function,
                 popup=popup,
                 name="Query Results (Aggregated)"
             ).add_to(map)
        else:
             folium.GeoJson(df_json, name="Query Results").add_to(map)

        try:
             folium.WmsTileLayer(
                 url='[https://wms.geonorge.no/skwms1/wms.topo4](https://wms.geonorge.no/skwms1/wms.topo4)',
                 layers='topo4',
                 transparent=False,
                 control=True,
                 fmt="image/png",
                 name='Topo4 (Kartverket)',
                 attr='Kartverket',
                 version='1.3.0'
             ).add_to(map)
             folium.WmsTileLayer(
                 url='[https://wms.geonorge.no/skwms1/wms.ortofoto](https://wms.geonorge.no/skwms1/wms.ortofoto)',
                 layers='ortofoto',
                 transparent=False,
                 control=True,
                 fmt="image/png",
                 name='Ortofoto (Kartverket)',
                 attr='Kartverket',
                 version='1.3.0'
             ).add_to(map)
        except Exception as wms_err:
            st.warning(f"Could not add WMS base layers: {wms_err}")
            st.info("Check if WMS URLs are correct and accessible.")

        folium.LayerControl().add_to(map)
        st_folium(map, width=1000, height=500, key=f"map_{hash(query_string)}", zoom=initial_zoom, returned_objects=[])

    except Exception as e:
        st.error(f"An error occurred while displaying the map: {e}")
        st.code(traceback.format_exc())