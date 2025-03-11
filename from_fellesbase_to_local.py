import os
import geopandas as gpd
from sqlalchemy import create_engine
from config import conn
from dotenv import load_dotenv
load_dotenv()


# --- CONFIGURATION SETTINGS ---
SQL_FILE_NAME = "dataset_querys/fotrute.sql" # SQL file with a query to execute
TABLE_NAME = "fotrute_aas"
SCHEMA = "public" # if None, default is public


with open(SQL_FILE_NAME, 'r', encoding="UTF-8") as file:
    download_query = file.read()


# --- FINDING DATA IN FELLESBASE ---
def download_data(query):
    print("Retrieving data from Fellesbase...")
    conn_felles = f"postgresql://{os.getenv('DB_USER_FELLESBASE')}:{os.getenv('DB_PASSWORD_FELLESBASE')}@{os.getenv('DB_HOST_FELLESBASE')}:{os.getenv('DB_PORT_FELLESBASE')}/{os.getenv('DB_NAME_FELLESBASE')}"
    gdf = gpd.read_postgis(query, conn_felles)
    print(f"✅ Data successfully loaded from Fellesbase.")
    return gdf


def import_to_db(data):
    print("Importing data to the local database...")
    conn_local = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    engine = create_engine(conn_local)
    data.to_postgis(TABLE_NAME, engine, schema=SCHEMA, if_exists="replace") # default if_exists="fail"
    print(f"✅ Data has been successfully imported into the table '{SCHEMA}.{TABLE_NAME}'.")


# --- MAIN SCRIPT ---
def run_script():
    gdf_data = download_data(download_query)
    if not gdf_data.empty:
       import_to_db(gdf_data)

run_script()
