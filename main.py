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
from visualize_functions import display_logo_title

load_dotenv()


def main():

    display_logo_title()

    db = connect_to_db()
    llm = ChatGroq(
        api_key=os.getenv("API_KEY_GROQ"),
        model="gemma2-9b-it", # gemma2-9b-it
        temperature=0.0,
        max_tokens=1024       
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
    
    # Reset the session state at the start of each run (in case of pressing the stop button)
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