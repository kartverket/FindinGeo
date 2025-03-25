"Query-eksempel for forenklet_elveg fra FindinGeo databasen"

"Hvor mange bilveier er det i Ås?"
"Fasit: 4555"
SELECT COUNT(typeveg)
FROM forenklet_elveg_aas
WHERE typeveg = 'enkelBilveg';



" Hvor mange riksveier er det i Ås?"
"Fasit: 0"
SELECT COUNT(vegkategori)
FROM forenklet_elveg_aas
WHERE vegkategori = 'R';


"Kan du hente ut alle veier som har blitt målt med stereoinstrument i Ås?"
SELECT objid, malemetode
FROM forenklet_elveg_aas
WHERE malemetode = 'stereoinstrument';


"Kan du hente ut de 50 første registrerte veiene og deres målemetode?"
SELECT objid, datafangstdato, malemetode
FROM forenklet_elveg_aas
ORDER BY datafangstdato ASC
LIMIT 50;


"Hvor mange veier er det i Brekkeskog?"
"Fasit: 16"
SELECT COUNT(*)
FROM forenklet_elveg_aas
WHERE adressenavn LIKE '%Brekkeskog%';


"Hvor mange veier ble registrert i 2023?"
"Fasit: 1"
SELECT EXTRACT(YEAR FROM datafangstdato) AS år, COUNT(*) AS antall_registreringer
FROM forenklet_elveg_aas
WHERE år = 2023
GROUP BY år
ORDER BY antall_registreringer DESC;


"Hvor mye varierer målingene i nøyaktighet?"
SELECT MAX(noyaktighet), MIN(noyaktighet)
FROM forenklet_elveg_aas


"Hvor mange sideveier er det i Ås?"
"Fasit: 895"
SELECT COUNT(sideveg)
FROM forenklet_elveg_aas
WHERE sideveg = 'JA';


"Hvor mange veier eldre enn 2015 har ikke blitt oppdatert?"
"Fasit: 2444"
SELECT COUNT(*)
FROM forenklet_elveg_aas
WHERE EXTRACT(YEAR FROM datafangstdato) < 2015 AND oppdateringsdato IS NULL;


"Hvor mange veier er oppdatert i det hele tatt?"
"Fasit: 811"
SELECT COUNT(*)
FROM forenklet_elveg_aas
WHERE oppdateringsdato IS NOT NULL;


"Hvor mange gangveier finnes i Ås?"
"Fasit: 352"
SELECT COUNT(*)
FROM forenklet_elveg_aas
WHERE typeveg = 'gangveg';


"Hvilket år ble flest veier registrert, og hvor mange var det?"
"Fasit: 2018, 2209"
SELECT EXTRACT(YEAR FROM datafangstdato) AS år, COUNT(*) AS antall
FROM forenklet_elveg_aas
GROUP BY år
ORDER BY antall DESC
LIMIT 1;


"Finn de tre lengste veiene i Ås"
SELECT objid, adressenavn, geom
FROM forenklet_elveg_aas
ORDER BY ST_LENGTH(geom) DESC
LIMIT 3;

"Hvilke vegkategorier finnes i datasettet og hvor mange veier finnes i hver kategori?"
SELECT v.description AS vegkategori_beskrivelse, COUNT(*) AS antall_veier
FROM forenklet_elveg_aas e
JOIN forenklet_elveg_aas_vegkategori v
  ON e.vegkategori = v.identifier
GROUP BY v.description
ORDER BY antall_veier DESC;


"Finn veier som er ved siden av hverandre"
SELECT vegkategori = 'P', ST_AsText(ST_Buffer(location, 50)) AS road_buffer
FROM forenklet_elveg_aas;


examples_elveg = [
    {   "input": "Kan du hente ut alle veier som har blitt målt med stereoinstrument i Ås?", 
        "query": "SELECT objid, datafangstdato, malemetode FROM forenklet_elveg_aas ORDER BY datafangstdato ASC LIMIT 50;",
    },
    {   "input": "Hvor mange veier ble registrert i 2023?", 
        "query": "SELECT EXTRACT(YEAR FROM datafangstdato) AS år, COUNT(*) AS antall_registreringer FROM forenklet_elveg_aas WHERE år = 2023 GROUP BY år ORDER BY antall_registreringer DESC;",
    },
    {,
        "input": "Hvor mange riksveier er det i Ås?",
        "query": "SELECT COUNT(vegkategori) FROM forenklet_elveg_aas WHERE vegkategori = 'R';",
    },
    {
        "input": "Hvor mange gangveier finnes i Ås?",
        "query": "SELECT COUNT(*) FROM forenklet_elveg_aas WHERE typeveg = 'gangveg';",
    },
    {
        "input": "Hvor mange sideveier er det i Ås?",
        "query": "SELECT COUNT(sideveg) FROM forenklet_elveg_aas WHERE sideveg = 'JA';",
    },
    {
        "input": "Hvor mange veier er det i Brekkeskog?",
        "query": "SELECT COUNT(*) FROM forenklet_elveg_aas WHERE adressenavn LIKE '%Brekkeskog%';"
    },
    {
        "input": "Kan du hente ut de 50 første registrerte veiene og deres målemetode?",
        "query": "SELECT objid, datafangstdato, malemetode FROM forenklet_elveg_aas ORDER BY datafangstdato ASC LIMIT 50;",
    },
    {
        "input": "Hvor mange bilveier er det i Ås?",
        "query": "SELECT COUNT(typeveg) FROM forenklet_elveg_aas WHERE typeveg = 'enkelBilveg';",
    },
    {
        "input": "Hvor mye varierer målingene i nøyaktighet?",
        "query": "SELECT MAX(noyaktighet), MIN(noyaktighet) FROM forenklet_elveg_aas",
    },
    {
        "input": "Hvor mange veier eldre enn 2015 har ikke blitt oppdatert?",
        "query": "SELECT COUNT(*) FROM forenklet_elveg_aas WHERE EXTRACT(YEAR FROM datafangstdato) < 2015 AND oppdateringsdato IS NULL",
    },
    {
        "input": "Hvor mange veier er oppdatert i det hele tatt?",
        "query": "SELECT COUNT(*) FROM forenklet_elveg_aas WHERE oppdateringsdato IS NOT NULL;",
    },
    {
        "input": "Hvilket år ble flest veier registrert, og hvor mange var det?",
        "query": "SELECT EXTRACT(YEAR FROM datafangstdato) AS år, COUNT(*) AS antall FROM forenklet_elveg_aas GROUP BY år ORDER BY antall DESC LIMIT 1;",
    },
    {
        "input": "Finn de tre lengste veiene i Ås",
        "query": "SELECT objid, adressenavn, geom FROM forenklet_elveg_aas ORDER BY ST_LENGTH(geom) DESC LIMIT 3;",
    },
    {
        "input": "Hvilke vegkategorier finnes i datasettet og hvor mange veier finnes i hver kategori?",
        "query": "SELECT v.description AS vegkategori_beskrivelse, COUNT(*) AS antall_veier FROM forenklet_elveg_aas e JOIN forenklet_elveg_aas_vegkategori v ON e.vegkategori = v.identifier GROUP BY v.description ORDER BY antall_veier DESC;",
    },        
    {
        "input": "",
        "query": "",
    },      
    {
        "input": "",
        "query": "",
    },        
]



