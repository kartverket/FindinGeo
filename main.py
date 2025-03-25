# Entry point of the application
import os 
import sys
import streamlit as st
from langchain.callbacks.tracers import LangChainTracer
from langchain.agents import create_sql_agent, AgentType
from config import connect_to_db
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from interface import handle_agent_interaction
from fewshotprompt import few_shot_prompt
from tools import ALL_TOOLS
from langchain_core.prompts.prompt import PromptTemplate


load_dotenv()

# custom_prompt = PromptTemplate.from_template("""

# You are an agent that translates questions into PostgreSQL queries. 

# Use the following format:
# Thought: Think about how to solve the problem
# Action: Choose one of these tools: {tool_names}
# Action Input: The input to the tool (like a SQL query)
# Observation: The result of the action
# ... (repeat Thought/Action/Action Input/Observation as needed)
# Thought: I know the answer now
# Action: Final Answer
# Action Input: The final answer to the original question, formatted as valid JSON when possible

# Important rules:
# - Do not use terms such as 'DELETE', 'UPDATE', 'CREATE', 'INSERT', 'DROP', 'ALTER' and so on.
# - You will receive a question in either English or Norwegian.
# - You will need to translate the question into a SQL query and output the result.
# - Always format your final answer as valid JSON when the data allows for it.

# Question: {input}

# Tools: {tools}

# {agent_scratchpad}
# """

# )




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
        tools=ALL_TOOLS,
        db=db,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        prompt=few_shot_prompt
    )
    
    # Make sure that the session state is reset at the start of each run (in case of pressing the stop button without refreshing the window)
    if 'needs_reset' not in st.session_state:
        st.session_state.needs_reset = False
        
    if st.session_state.needs_reset:
        sys.stdout = st.session_state.original_stdout
        st.session_state.needs_reset = False

    # UI Streamlit
    user_query = st.text_input("Ask me a question:")
    submit_button = st.button("Submit", key="unique_submit")
    
    if submit_button and user_query.strip():
        handle_agent_interaction(agent, user_query, tracer)
    else:
        if submit_button:
            st.warning("Please enter a question.")

if __name__ == "__main__":
    main()