

def validate_sql(sql_query):
    """
    Implement basic validation to avoid dangerous commands (e.g., DROP, DELETE).
    """
    prohibited_keywords = ["DROP", "DELETE", "ALTER"]
    for word in prohibited_keywords:
        if word.lower() in sql_query.lower():
            raise ValueError("Query contains prohibited operations.")
    return True