import psycopg2
from langchain.agents import Tool
from config import DATABASE_URI

def sql_db_query(query: str) -> str:
    """
    Execute a SQL query and return the results as a string.
    """
    try:
        with psycopg2.connect(DATABASE_URI) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                # Fetch all results
                rows = cur.fetchall()
                # Convert rows to a readable string
                result_str = "\n".join(str(row) for row in rows)
                return result_str if result_str else "No results."
    except Exception as e:
        return f"Error executing query: {e}"

def sql_db_schema(tables: str) -> str:
    """
    Given a comma-separated list of table names, return schema info and sample rows for each table.
    """
    table_list = [t.strip() for t in tables.split(",") if t.strip()]
    if not table_list:
        return "No tables specified."

    try:
        with psycopg2.connect(DATABASE_URI) as conn:
            with conn.cursor() as cur:
                results = []
                for table in table_list:
                    # Get schema info from information_schema
                    schema_query = f"""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = '{table}';
                    """
                    cur.execute(schema_query)
                    schema_rows = cur.fetchall()
                    schema_info = f"Schema for {table}:\n" + "\n".join(str(row) for row in schema_rows)

                    # Get sample rows
                    sample_query = f"SELECT * FROM {table} LIMIT 5;"
                    try:
                        cur.execute(sample_query)
                        sample_rows = cur.fetchall()
                        sample_info = f"Sample rows from {table}:\n" + "\n".join(str(row) for row in sample_rows)
                    except Exception as e:
                        sample_info = f"Could not get sample rows from {table}: {e}"

                    results.append(schema_info + "\n" + sample_info + "\n")
                return "\n".join(results)
    except Exception as e:
        return f"Error retrieving schema: {e}"

def sql_db_list_tables(_: str = "") -> str:
    """
    Return a comma-separated list of all tables in the public schema of the database.
    """
    try:
        with psycopg2.connect(DATABASE_URI) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT tablename
                    FROM pg_catalog.pg_tables
                    WHERE schemaname = 'public';
                """)
                rows = cur.fetchall()
                if not rows:
                    return "No tables found."
                table_names = [row[0] for row in rows]
                return ", ".join(table_names)
    except Exception as e:
        return f"Error listing tables: {e}"

def sql_db_query_checker(query: str) -> str:
    """
    A simple query checker that tries to parse the query using EXPLAIN.
    If it's valid, return 'Query seems valid.'
    If not, return the error message.
    """
    try:
        with psycopg2.connect(DATABASE_URI) as conn:
            with conn.cursor() as cur:
                # Use EXPLAIN to check if the query is valid
                explain_query = f"EXPLAIN {query}"
                cur.execute(explain_query)
                # If we get here, the query is likely valid
                return "Query seems valid."
    except Exception as e:
        return f"Query check failed: {e}"

# Tools for SQL queries
sql_db_query = Tool(
    name="sql_db_query",
    func=sql_db_query,
    description="Input to this tool is a detailed and correct SQL query, output is a result from the database. If the query is not correct, an error message will be returned. If an error is returned, rewrite the query, check the query, and try again. If you encounter an issue with Unknown column 'xxxx' in 'field list', use sql_db_schema to query the correct table fields."
)

sql_db_schema = Tool(
    name="sql_db_schema",
    func=sql_db_schema,
    description="Input to this tool is a comma-separated list of tables, output is the schema and sample rows for those tables. Be sure that the tables actually exist by calling sql_db_list_tables first! Example Input: table1, table2, table3"
)

sql_db_list_tables = Tool(
    name="sql_db_list_tables",
    func=sql_db_list_tables,
    description="Input is an empty string, output is a comma-separated list of tables in the database."
)

sql_db_query_checker = Tool(
    name="sql_db_query_checker",
    func=sql_db_query_checker,
    description="Use this tool to double check if your query is correct before executing it. Always use this tool before executing a query with sql_db_query!"
)

ALL_TOOLS = [
    sql_db_query, 
    sql_db_schema, 
    sql_db_list_tables, 
    sql_db_query_checker,
    ]