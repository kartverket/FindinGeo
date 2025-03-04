import os
import requests
import geopandas as gpd
from sqlalchemy import create_engine
import psycopg2
from config import conn
from dotenv import load_dotenv
load_dotenv()

with open('dataset_querys/skiloyper.sql', 'r') as file:
    skiloyper = file.read()

with open('dataset_querys/fotrute.sql', 'r') as file:
    fotrute = file.read()

TABLE_NAME = "public.skifotruter_aas"


# --- FINDING DATA IN FELLESBASE ---
def download_data():

    query = fotrute
    
    print("Henter data fra Fellesbase...")

    conn_string = f"postgresql://{os.getenv('DB_USER_FELLESBASE')}:{os.getenv('DB_PASSWORD_FELLESBASE')}@{os.getenv('DB_HOST_FELLESBASE')}/{os.getenv('DB_NAME_FELLESBASE')}"
    print(conn_string)
    gdf = gpd.read_postgis(query, conn_string)
    
    print(gdf.head())
    return gdf.head()



# --- KOBLE TIL DATABASE OG OPPRETT TABELL ---
def create_table():
    print("Kobler til PostgreSQL-database...")
    cursor = conn.cursor()

    # Sjekk om tabellen finnes, og opprett den hvis ikke
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id SERIAL PRIMARY KEY,
        navn TEXT,
        koordinater GEOMETRY
    );
    """)
    conn.commit()
    cursor.close()
    print(f"✅ Tabell '{TABLE_NAME}' er opprettet (hvis ikke allerede eksistens).")



# --- KJØR SKRIPTET ---
def run_script():
    file_name = download_data()  # Steg 1: Last ned data
    if file_name:
       create_table()  # Steg 2: Opprett tabell i database
       # import_to_db(file_name)  # Steg 3: Importer data til database

# Kjør skriptet
run_script()
