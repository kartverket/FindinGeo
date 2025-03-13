# LLM integration and SQL agent logic

from langchain.sql_database import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
import os
from config import conn
from llm import llm



class GeoSQLAgent:
    def __init__(self):
        #self.llm = llm_hf()
        self.llm = llm()
        
        self.db = SQLDatabase(conn)
        
        self.chain = SQLDatabaseChain(
            llm=self.llm,
            database=self.db, 
            verbose=True)
        
    def run_query(self, natural_language_query):
        """
        Accepts a natural language query, translates it to SQL, executes it, and returns the results.
        """
        try:
            result = self.chain.run(natural_language_query)
            return result
        except Exception as e:
            return f"An error occurred: {e}"
        

# For quick testing via the command line:
if __name__ == "__main__":
    agent = GeoSQLAgent()
    sample_query = (
        "Find all regions that intersect with the bounding box defined by "
        "coordinates (min_longitude, min_latitude, max_longitude, max_latitude)."
    )
    print("Query Results:", agent.run_query(sample_query))