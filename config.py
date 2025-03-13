# Configuration settings (API keys, database URI, etc.)
import os
import psycopg2
from dotenv import load_dotenv


load_dotenv()
# Using secure file to store the connection string
# conn = psycopg2.connect(
#     dbname=os.getenv("DB_NAME"),
#     user=os.getenv("DB_USER"),
#     password=os.getenv("DB_PASSWORD"),
#     host=os.getenv("DB_HOST"),
#     port=os.getenv("DB_PORT")
# )

# Fellesbasen
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME_FELLESBASE"),
    user=os.getenv("DB_USER_FELLESBASE"),
    password=os.getenv("DB_PASSWORD_FELLESBASE"),
    host=os.getenv("DB_HOST_FELLESBASE"),
    port=os.getenv("DB_PORT_FELLESBASE")
)

# Using secure file to store the API key for LLM's 
HF_API_KEY = os.getenv("HF_API_KEY")
HF_REPO_ID = os.getenv("HF_REPO_ID")
API_KEY_GROQ = os.getenv("API_KEY_GROQ")