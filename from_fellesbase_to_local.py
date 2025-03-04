import os
import requests
import geopandas as gpd
from sqlalchemy import create_engine
import psycopg2
from config import conn
from dotenv import load_dotenv
load_dotenv()

TABLE_NAME = "public.skifotruter_aas"


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
                -- Samler alle skiløype-segmenter og beregner lengden på senterlinjen
                skiløyper AS (
                    SELECT 
                        s.objid AS skiloype_id,
                        ST_Union(s.senterlinje) AS geom
                    FROM 
                        tur_og_friluftsruter.skiloype s
                    GROUP BY 
                        s.objid
                )
                SELECT 
                    s.skiloype_id,
                    s.geom
                FROM 
                    skiløyper s
                JOIN 
                    kommuner k 
                ON 
                    ST_Intersects(s.geom, k.geom)
                WHERE 
                    k.kommunenavn ILIKE 'Ås'"""

    # query = """WITH kommuner AS (
    #             SELECT
    #                 k.objid AS kommune_objid, 
    #                 a.navn AS kommunenavn,
    #                 k.omrade AS geom
    #             FROM 
    #                 administrative_enheter_kommuner.kommune k
    #             JOIN 
    #                 administrative_enheter_kommuner.administrativenhetnavn a
    #             ON 
    #                 k.lokalid = a.kommune_fk
    #             WHERE 
    #                 a.sprak = 'nor'
    #         ),
    #         -- Samler alle fotruter-segmenter og beregner lengden på senterlinjen
    #         fotruter AS (
    #             SELECT 
    #                 s.objid AS fotrute_id,
    #                 ST_Union(s.senterlinje) AS geom
                    
    #             FROM 
    #                 tur_og_friluftsruter.fotrute s
    #             GROUP BY 
    #                 s.objid
    #         )
    #         SELECT 
    #             f.fotrute_id,
    #             f.geom,
    #             s.objid,
    #             s.objtype,
    #             s.senterlinje,
    #             s.lokalid,
    #             s.navnerom,
    #             s.versjonid,
    #             s.datafangstdato,
    #             s.oppdateringsdato,
    #             s.noyaktighet,
    #             s.opphav,
    #             s.omradeid,
    #             s.informasjon,
    #             s.rutefolger,
    #             s.malemetode


    #         FROM 
    #             fotrute f
    #         JOIN 
    #             kommuner k 
    #         ON 
    #             ST_Intersects(s.geom, k.geom)
    #         WHERE 
    #             k.kommunenavn ILIKE 'Ås'"""
    
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
    #if file_name:
    #    create_table()  # Steg 2: Opprett tabell i database
       # import_to_db(file_name)  # Steg 3: Importer data til database

# Kjør skriptet
run_script()
