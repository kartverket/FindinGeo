from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.prompts.few_shot import FewShotPromptTemplate


# Few-shot prompt for SQL queries
few_shots = [
    {
        "input": "What is the total number of rows in the table?",
        "query": "SELECT COUNT(*) FROM table_name;"
    },
    {
        "input": "What is the average value of the column 'column_name'?",
        "query": "SELECT AVG(column_name) FROM table_name;"
    },
    {
        "input": "What is the maximum value of the column 'column_name'?",
        "query": "SELECT MAX(column_name) FROM table_name;"
    },
    {
        "input": "What is the minimum value of the column 'column_name'?",
        "query": "SELECT MIN(column_name) FROM table_name;"
    },
    {
        "input": "What is the sum of the column 'column_name'?",
        "query": "SELECT SUM(column_name) FROM table_name;"
    }
]

prefix="""
You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct postgresql query to run, then look at the results of the query and return the answer.
Unless the user explicitly requests more than 10 results, always limit your query to at most 10 rows.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.
You have access to tools for interacting with the database.
Only use the below tools. Only use the information returned by the below tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again. 

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

If the question does not seem related to the database, just return "I don't know" as the answer.


sql_db_query - Input to this tool is a detailed and correct SQL query, output is a result from the database. If the query is not correct, an error message will be returned. If an error is returned, rewrite the query, check the query, and try again. If you encounter an issue with Unknown column 'xxxx' in 'field list', use sql_db_schema to query the correct table fields.
sql_db_schema - Input to this tool is a comma-separated list of tables, output is the schema and sample rows for those tables. Be sure that the tables actually exist by calling sql_db_list_tables first! Example Input: table1, table2, table3
sql_db_list_tables - Input is an empty string, output is a comma-separated list of tables in the database.
sql_db_query_checker - Use this tool to double check if your query is correct before executing it. Always use this tool before executing a query with sql_db_query!

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [sql_db_query, sql_db_schema, sql_db_list_tables, sql_db_query_checker]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!
"""

# Finne chatGroq prompt template 

#https://python.langchain.com/docs/how_to/sql_prompting/
example_prompt = PromptTemplate.from_template("User input: {input}\nSQL query: {query}")
few_shot_prompt = FewShotPromptTemplate(
    examples=few_shots,
    example_prompt=example_prompt,
    prefix=prefix,
    suffix="User input: {input}\nSQL query: ",
    input_variables=["input", "top_k", "table_info"],
)

if __name__ == "__main__":
    render_prompt = few_shot_prompt.format(
        input="What is the total number of rows in the table?",
        top_k=5,
        table_info="table_name"
    )
    print(render_prompt)
