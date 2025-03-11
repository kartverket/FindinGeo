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

TABLE_NAME = "public.fotrute_aas"


# --- FINDING DATA IN FELLESBASE ---
def download_data():

    query = """WITH kommuner AS (
                SELECT
                    k.objid AS kommune_objid, 
                    a.navn AS kommunenavn,
                    k.omrade AS geom
                FROM 
                    administrative_enheter_kommuner.kommune k
                JOIN 
                    administrative_enheter_kommuner.administrativenhetnavn a
                ON 
                    k.lokalid = a.kommune_fk
                WHERE 
                    a.sprak = 'nor'
            ),
            -- Samler alle fotruter-segmenter og beregner lengden på senterlinjen
            fotrute AS (
                SELECT 
					f.objid AS fotrute_id,
                    ST_Union(f.senterlinje) AS geom,
					f.objtype AS rutetype,
                    ST_Length(ST_Union(f.senterlinje)) AS senterlinje,
                    f.lokalid AS lokal,
                    f.navnerom AS navn,
                    f.versjonid AS versjon,
                    f.datafangstdato AS datafangstdato_,
                    f.oppdateringsdato AS oppdateringsdato_,
                    f.noyaktighet AS noyaktighet_,
                    f.opphav AS opphav_,
                    f.omradeid AS omradeid_,
                    f.informasjon AS informasjon_,
                    f.rutefolger AS rutefolger_,
                    f.malemetode AS malemetode_
                FROM 
                    tur_og_friluftsruter.fotrute f
                GROUP BY 
					f.objid,
					f.objtype,
                    f.lokalid,
                    f.navnerom,
                    f.versjonid,
                    f.datafangstdato,
                    f.oppdateringsdato,
                    f.noyaktighet,
                    f.opphav,
                    f.omradeid,
                    f.informasjon,
                    f.rutefolger,
                    f.malemetode
					
            )
            SELECT 
					f.fotrute_id,
					f.geom,
					f.rutetype,
					f.senterlinje,
					f.lokal,
					f.navn,
					f.versjon,
					f.datafangstdato_,
					f.oppdateringsdato_,
					f.noyaktighet_,
					f.opphav_,
					f.omradeid_,
					f.informasjon_,
					f.rutefolger_,
					f.malemetode_


            FROM 
                fotrute f
            JOIN 
                kommuner k 
            ON 
                ST_Intersects(f.geom, k.geom)
            WHERE 
                k.kommunenavn ILIKE 'Ås'"""     # choose file query to download
    
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


def import_to_db(file_name):
    df = file_name.to_postgis(TABLE_NAME, conn, schema="public")
    print(df.head())
    print(f"✅ Data er importert til tabell '{TABLE_NAME}'.")



# --- KJØR SKRIPTET ---
def run_script():
    file_name = download_data()  # Steg 1: Last ned data
    if not file_name.empty:
       create_table()  # Steg 2: Opprett tabell i database
       import_to_db(file_name)  # Steg 3: Importer data til database

# Kjør skriptet
run_script()
