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
from langchain import hub
from config import connect_to_db
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from interface import display_results
from langchain_core.prompts.prompt import PromptTemplate #, FewShotPromptTemplate

db = connect_to_db()

custom_prompt = PromptTemplate.from_template("""

You are an agent that translates questions into PostgreSQL queries. 

Use the following format:
Thought: Think about how to solve the problem
Action: Choose one of these tools: {tool_names}
Action Input: The input to the tool (like a SQL query)
Observation: The result of the action
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I know the answer now
Action: Final Answer
Action Input: The final answer to the original question, formatted as valid JSON when possible

Important rules:
- Do not use terms such as 'DELETE', 'UPDATE', 'CREATE', 'INSERT', 'DROP', 'ALTER' and so on.
- You will receive a question in either English or Norwegian.
- You will need to translate the question into a SQL query and output the result.
- Always format your final answer as valid JSON when the data allows for it.

Question: {input}

Tools: {tools}

{agent_scratchpad}
"""
)

#https://python.langchain.com/docs/how_to/sql_prompting/
# example_prompt = PromptTemplate.from_template("User input: {input}\nSQL query: {query}")
# prompt = FewShotPromptTemplate(
#     examples=few_shots[:5],
#     example_prompt=example_prompt,
#     prefix="You are a SQLite expert. Given an input question, create a syntactically correct SQLite query to run. Unless otherwise specificed, do not return more than {top_k} rows.\n\nHere is the relevant table info: {table_info}\n\nBelow are a number of examples of questions and their corresponding SQL queries.",
#     suffix="User input: {input}\nSQL query: ",
#     input_variables=["input", "top_k", "table_info"],
# )



load_dotenv()

def main():

    st.title("FindinGeo👀")

    db = connect_to_db()
    llm = ChatGroq(
        api_key=os.getenv("API_KEY_GROQ"),
        model="qwen-2.5-coder-32b",
        temperature=0.0,
        max_tokens=512        
    )
    
    # LangSmith tracer for debugging/monitoring
    tracer = LangChainTracer(project_name="FindinGeo")

    agent = create_sql_agent(
        llm=llm,
        db=db,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        prompt=custom_prompt
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