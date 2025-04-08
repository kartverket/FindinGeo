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


class StreamlitLogger:
    def __init__(self, terminal_placeholder, original_stdout):
        self.log_buffer = []
        self._original_stdout = original_stdout
        self.terminal_placeholder = terminal_placeholder
        
    def write(self, text):
        self._original_stdout.write(text)
        if text.strip():
            clean_text = strip_ansi_codes(text)
            self.log_buffer.append(clean_text)
            
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


def clean_sql_query(query_string):
    """
    Clean a SQL query string by removing markdown formatting
    
    Args:
        query_string (str): SQL query that may contain markdown formatting
        
    Returns:
        str: Clean SQL query with all markdown formatting removed
    """
    if not query_string:
        return query_string
        
    # Remove ```sql at the beginning
    query_string = re.sub(r'^```sql\s*', '', query_string)
    # Remove ``` at the end
    query_string = re.sub(r'\s*```$', '', query_string)
    # Remove any remaining inline code formatting
    query_string = re.sub(r'`([^`]*)`', r'\1', query_string)
    
    return query_string


def handle_agent_interaction(agent, user_query, tracer):
    # Create a placeholder for the terminal-like output
    terminal_placeholder = st.empty()
    
    # Create a placeholder for results after the terminal
    results_placeholder = st.container()
    
    # Initialize the SQL query variable
    sql_query_string = ""
    
    st.session_state.map_displayed = False
    
    try:
        if 'original_stdout' not in st.session_state:
            st.session_state.original_stdout = sys.stdout
            
        streamlit_logger = StreamlitLogger(terminal_placeholder, st.session_state.original_stdout)
        sys.stdout = streamlit_logger
        st.session_state.needs_reset = True
        
        try:
            raw_result = agent.invoke({"input": user_query}, callbacks=[tracer])
            
            # Extract result text from various possible formats
            result_text = raw_result["output"] if isinstance(raw_result, dict) and "output" in raw_result else str(raw_result)
            
            # Handle various response scenarios
            with results_placeholder:
                if "Agent stopped due to iteration limit or time limit" in result_text:
                    st.warning("The query was too complex to process in the allotted time. Try simplifying your question.")
                elif result_text.strip() == "I don't know":
                    st.info("The agent couldn't find an answer to your question. Try rephrasing or asking about something else.")
                elif "insufficient information" in result_text.lower() or "error" in result_text.lower():
                    if "{\"error\":" in result_text and (error_match := re.search(r'{"error":\s*"([^"]+)"}', result_text)):
                        st.error(f"Database Error: {error_match.group(1)}")
                    elif "Final Answer is not a valid tool" in result_text and (error_content := re.search(r'Action Input: (.+?)Final Answer is not a valid tool', result_text, re.DOTALL)):
                        try:
                            error_json = json.loads(error_content.group(1).strip())
                            if "error" in error_json:
                                st.error(f"Query Error: {error_json['error']}")
                            else:
                                st.warning("The agent couldn't find the necessary information to answer your question.")
                        except:
                            st.warning("The agent couldn't complete the query properly.")
                    else:
                        display_results(result_text)
                else:
                    display_results(result_text)
            
        except Exception as agent_err:
            error_message = str(agent_err)
            
            with results_placeholder:
                if "output parsing error" in error_message.lower():
                    # Try to extract structured content from error message
                    parsing_error_match = re.search(r'Could not parse LLM output: `(.*?)`', error_message, re.DOTALL)
                    if parsing_error_match:
                        error_content = parsing_error_match.group(1)
                        
                        # Extract SQL query using various patterns
                        # Case 1: SQL Query/query format
                        sql_pattern1 = re.search(r'SQL [Qq]uery:?\s*(.*?)(?=Result:|$)', error_content, re.DOTALL)
                        # Case 2: Direct SQL statement
                        sql_pattern2 = re.search(r'(SELECT\s+.*?;)', error_content, re.DOTALL | re.IGNORECASE)
                        
                        if sql_pattern1:
                            sql_query_string = sql_pattern1.group(1).strip()
                        elif sql_pattern2:
                            sql_query_string = sql_pattern2.group(1).strip()
                            
                        # Clean the SQL query from markdown formatting
                        sql_query_string = clean_sql_query(sql_query_string)
                        
                        result_match = re.search(r'Result:\s*(.*?)$', error_content, re.DOTALL)
                        
                        if sql_query_string:
                            st.subheader("Extracted Information:")
                            st.write("**SQL Query:**")
                            st.code(sql_query_string, language="sql")
                            if result_match:
                                st.write("**Answer:**")
                                st.write(result_match.group(1).strip())
                            
                            st.session_state.last_sql_query = sql_query_string
                            return sql_query_string
                    
                    st.error("Output parsing error has occurred!")
                    print(f"{error_message}")
                else:
                    st.error(f"An error has occurred: {error_message}")
        finally:
            sys.stdout = st.session_state.original_stdout
    
    except Exception as e:
        sys.stdout = st.session_state.original_stdout
        with results_placeholder:
            st.error("An unexpected error occurred: " + str(e))
    
    return sql_query_string


def transform_aggregate_query(sql_query):
    """
    Transform aggregation queries to retrieve mappable geographic data.
    
    This function takes aggregate queries (COUNT, MAX, MIN, etc.) and 
    transforms them to also return the geographic data needed for mapping.
    
    Args:
        sql_query (str): The original SQL query
        
    Returns:
        str: A transformed SQL query that will return mappable data
    """
    # Skip if query is empty
    if not sql_query:
        return None
        
    # Make sure the query is clean of any markdown formatting
    sql_query = clean_sql_query(sql_query)
        
    # Clean the query further (remove comments, extra spaces, etc.)
    clean_query = re.sub(r'--.*$', '', sql_query, flags=re.MULTILINE)
    clean_query = re.sub(r'/\*.*?\*/', '', clean_query, flags=re.DOTALL)
    clean_query = ' '.join(clean_query.split())
    
    # Case 1: Handle COUNT(*) queries without GROUP BY
    if re.search(r'SELECT\s+COUNT\(\*\)\s+FROM', clean_query, re.IGNORECASE) and not re.search(r'GROUP BY', clean_query, re.IGNORECASE):
        # Parse the table name
        table_match = re.search(r'FROM\s+([^\s;]+)', clean_query, re.IGNORECASE)
        if table_match:
            table_name = table_match.group(1)
            # Create a new query that selects everything from the table with geometry
            new_query = f"SELECT *, COUNT(*) OVER() as total_count FROM {table_name}"
            
            # Add any WHERE clause from the original query
            where_match = re.search(r'(WHERE\s+.+?)(?:ORDER BY|GROUP BY|LIMIT|;|$)', clean_query, re.IGNORECASE | re.DOTALL)
            if where_match:
                new_query += f" {where_match.group(1)}"
                
            # Add LIMIT to avoid returning too much data
            if not re.search(r'LIMIT', new_query, re.IGNORECASE):
                new_query += " LIMIT 100"
                
            return new_query
    
    # Case 2: Handle MIN/MAX/AVG queries without GROUP BY
    min_max_match = re.search(r'SELECT\s+(MIN|MAX|AVG)\(([^)]+)\)\s+FROM\s+([^\s;]+)', clean_query, re.IGNORECASE)
    if min_max_match and not re.search(r'GROUP BY', clean_query, re.IGNORECASE):
        agg_func = min_max_match.group(1).upper()
        agg_col = min_max_match.group(2)
        table_name = min_max_match.group(3)
        
        # For MIN/MAX, we can find the row(s) with that value
        if agg_func in ('MIN', 'MAX'):
            new_query = r"""
            WITH agg_value AS (
                SELECT {agg_func}({agg_col}) as target_value FROM {table_name}
                {' WHERE ' + re.search(r'WHERE\s+(.+?)(?:ORDER BY|GROUP BY|LIMIT|;|$)', clean_query, re.IGNORECASE | re.DOTALL).group(1) if re.search(r'WHERE', clean_query, re.IGNORECASE) else ''}
            )
            SELECT t.*, '{agg_func}({agg_col})' as aggregation_type, av.target_value as aggregation_value
            FROM {table_name} t, agg_value av
            WHERE t.{agg_col} = av.target_value
            """
            return new_query
    
    # Case 3: Handle GROUP BY queries with aggregations
    group_by_match = re.search(r'GROUP BY\s+(.+?)(?:ORDER BY|HAVING|LIMIT|;|$)', clean_query, re.IGNORECASE | re.DOTALL)
    if group_by_match and re.search(r'(COUNT|SUM|AVG|MIN|MAX)\(', clean_query, re.IGNORECASE):
        # These queries can be complex - we need to determine if we can extract geographical information
        # This would require more complex query transformation - a simpler approach might be:
        return None  # Signal that we need special handling for these cases
        
    # If no transformation was applied, return None to indicate we should skip mapping
    return None


def is_aggregation_query(sql_query):
    """
    Determine if a query is an aggregation query.
    """
    if not sql_query:
        return False
        
    sql_query = clean_sql_query(sql_query)
        
    # Pure COUNT queries without GROUP BY
    if re.search(r'SELECT\s+COUNT\(\*\)\s+FROM', sql_query, re.IGNORECASE) and not re.search(r'GROUP BY', sql_query, re.IGNORECASE):
        return True
        
    # Simple aggregation queries that return single values
    if re.search(r'SELECT\s+(SUM|AVG|MIN|MAX)\([^,]*\)\s+FROM', sql_query, re.IGNORECASE) and not re.search(r'GROUP BY', sql_query, re.IGNORECASE):
        return True
        
    # Queries that count specific columns
    if re.search(r'SELECT\s+COUNT\([^,]*\)\s+FROM', sql_query, re.IGNORECASE) and not re.search(r'GROUP BY', sql_query, re.IGNORECASE):
        return True
    
    return False


def display_results(raw_result):
    parsed = None
    try:
        parsed = json.loads(raw_result)
    except Exception as e:
        pass
    
    # Try to extract SQL query from the raw result
    sql_query_string = ""
    sql_match = re.search(r'SQL [Qq]uery:?\s*(.*?)(?=\nResult:|\n\n|$)', raw_result, re.DOTALL)
    if sql_match:
        sql_query_string = sql_match.group(1).strip()
        
        sql_query_string = clean_sql_query(sql_query_string)
        
        # Store the SQL query in session state
        st.session_state.last_sql_query = sql_query_string
        
        # Display the extracted SQL query
        st.write("**SQL Query:**")
        st.code(sql_query_string, language="sql")
    
    st.write("**Answer:**")
    # Display results based on parsing success
    if parsed:
        if isinstance(parsed, list):
            df = pd.DataFrame(parsed)
            st.dataframe(df, use_container_width=True)

        elif isinstance(parsed, dict):
            df = pd.json_normalize(parsed, max_level=1)
            st.dataframe(df, use_container_width=True)
        else:
            st.write("**Parsed object:**", parsed)
    else:
        st.code(raw_result, language="plaintext")
    
    # Instead of skipping, transform the query if needed
    if is_aggregation_query(sql_query_string):
        st.info("This query returns aggregated data. Attempting to show relevant spatial information.")
        
        # Transform the original query to get mappable data
        transformed_query = transform_aggregate_query(sql_query_string)
        
        if transformed_query:
            st.write("**Using transformed query for mapping:**")
            st.code(transformed_query, language="sql")
            display_map(transformed_query)
        else:
            st.warning("Could not create a mappable version of this query.")
    else:
        display_map(sql_query_string)


def convert_dataframe_for_json(gdf):
    """
    Converts a GeoDataFrame to a JSON-serializable format (converts all non-numeric columns to strings)
    """
    for col in gdf.columns:
        # Convert all columns except for geometry column to strings
        if pd.api.types.is_datetime64_any_dtype(gdf[col]):
            gdf[col] = gdf[col].astype(str)
        elif gdf[col].dtype == 'object' and col != gdf.geometry.name:
            gdf[col] = gdf[col].astype(str)
    return gdf


def display_map(query_string):
    """Display a map based on query results"""
    if not st.session_state.get('map_displayed', False):
        st.write("**Map View:**")
        
        # Make sure the query is clean before execution
        query_string = clean_sql_query(query_string)
        
        try:
            conn_string = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
            
            # Debug line to verify the query being executed
            st.write(f"Executing query: `{query_string}`")
            
            gdf = gpd.read_postgis(query_string, conn_string)
            
            if gdf.empty:
                st.warning("No geographic data found in the results.")
                return
                
            # Check if we have geometry data
            if not hasattr(gdf, 'geometry') or gdf.geometry.isna().all():
                st.warning("The result contains no valid geometry data to display on the map.")
                return
            
            # Calculate centroid for map positioning
            valid_geoms = gdf.geometry[~gdf.geometry.isna()]
            if len(valid_geoms) == 0:
                st.warning("No valid geometries found to display.")
                return
                
            centroid = valid_geoms.unary_union.centroid
            
            # Create the map
            map = folium.Map(location=[centroid.y, centroid.x], zoom_start=12)
            
            # Convert dataframe for JSON serialization
            df_json = convert_dataframe_for_json(gdf)
            
            # Check if we have aggregation info to customize the popup
            has_agg_info = 'aggregation_type' in gdf.columns and 'aggregation_value' in gdf.columns
            
            # Add GeoJSON with custom styling based on presence of aggregation data
            if has_agg_info:
                # Add a GeoJSON layer with custom popups highlighting the aggregation info
                def style_function(feature):
                    return {
                        'fillColor': '#ff7800',
                        'color': '#000000',
                        'weight': 2,
                        'fillOpacity': 0.7
                    }
                
                # Create popup content that highlights the aggregation value
                popup = folium.GeoJsonPopup(
                    fields=gdf.columns.drop(['geometry', 'aggregation_type', 'aggregation_value']).tolist() + 
                           ['aggregation_type', 'aggregation_value'],
                    aliases=gdf.columns.drop(['geometry', 'aggregation_type', 'aggregation_value']).tolist() + 
                           ['Aggregation Type', 'Value'],
                    localize=True,
                    labels=True,
                )
                
                # Add GeoJSON with the custom popup
                folium.GeoJson(
                    df_json,
                    style_function=style_function,
                    popup=popup
                ).add_to(map)
            else:
                # Standard GeoJSON layer
                folium.GeoJson(df_json).add_to(map)
            
            # Display the map
            st_folium(map, width=1000, height=500, key="map", feature_group_to_add=None, returned_objects=[], zoom=None)        

            # Add base map layers
            folium.WmsTileLayer(
                url='https://cache.kartverket.no/v1/wmts/1.0.0/WMTSCapabilities.xml',
                layers='topograatone',
                transparent=False,
                control=True,
                fmt="image/png",
                name='Topo (gråtone)',
                attr='Kartverket',
                overlay=True,
                show=True,
                CRS='EPSG:25832',
                version='1.0.0'
            ).add_to(map)

            folium.LayerControl().add_to(map)
            
        except Exception as e:
            st.error(f"Error displaying map: {str(e)}")
            st.code(traceback.format_exc())

        st.session_state.map_displayed = True