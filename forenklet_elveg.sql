"Query-eksempel for forenklet_elveg fra FindinGeo databasen"

"Hvor mange bilveier er det i Ås?"
"Fasit: 4555"
SELECT objid, geom, COUNT(typeveg)
FROM forenklet_elveg_aas
WHERE typeveg = 'enkelBilveg'
GROUP BY objid, geom



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
SELECT objid, geom, datafangstdato, malemetode
FROM forenklet_elveg_aas
ORDER BY datafangstdato ASC
LIMIT 50;


"Hvor mange veier er det i Brekkeskog?"
"Fasit: 16"
SELECT objid, geom, COUNT(*)
FROM forenklet_elveg_aas
WHERE adressenavn LIKE '%Brekkeskog%'
GROUP BY objid, geom;


"Hvor mange veier ble registrert i 2023?"
"Fasit: 1"
SELECT objid, geom, EXTRACT(YEAR FROM datafangstdato) AS aar, COUNT(*) AS antall_registreringer
FROM forenklet_elveg_aas
WHERE EXTRACT(YEAR FROM datafangstdato) = 2023
GROUP BY objid, geom, aar;


"Hvor mye varierer målingene i nøyaktighet?"
"Svar: Fra 0.2 meter til 500 meter."
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


"Hvor lang er den lengste veien i Ås?"
SELECT objid, typeveg, ST_Length(ST_Transform(geom, 25833))/1000 AS senterlinje_km 
FROM forenklet_elveg_aas 
ORDER BY senterlinje_km DESC 
LIMIT 1;


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


"Finn alle skogsveier som er 100 m i nærheten av Audmax"
"Funker ikke"
SELECT objid, geom, vegkategori
FROM forenklet_elveg_aas;
WHERE ST_WITHIN(geom, ST_SetSRID(ST_MakePoint(6621631.05, 262203.05), 4326), 100);  -- point with your coordinates, in SRID 4326 (WGS 84)


examples_elveg = [
    {   "input": "Kan du hente ut alle veier som har blitt målt med stereoinstrument i Ås?", 
        "query": "SELECT objid, geom, datafangstdato, malemetode FROM forenklet_elveg_aas ORDER BY datafangstdato ASC LIMIT 50;",
    },
    {   "input": "Hvor mange veier ble registrert i 2023?", 
        "query": "SELECT objid, geom, EXTRACT(YEAR FROM datafangstdato) AS aar, COUNT(*) AS antall_registreringer FROM forenklet_elveg_aas WHERE EXTRACT(YEAR FROM datafangstdato) = 2023 GROUP BY objid, geom, aar;",
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
        "query": "SELECT objid, geom, COUNT(*) FROM forenklet_elveg_aas WHERE adressenavn LIKE '%Brekkeskog%' GROUP BY objid, geom;",
    },
    {
        "input": "Kan du hente ut de 50 første registrerte veiene og deres målemetode?",
        "query": "SELECT objid, geom, datafangstdato, malemetode FROM forenklet_elveg_aas ORDER BY datafangstdato ASC LIMIT 50;",
    },
    {
        "input": "Hvor mange bilveier er det i Ås?",
        "query": "SELECT objid, geom, COUNT(typeveg) FROM forenklet_elveg_aas WHERE typeveg = 'enkelBilveg' GROUP BY objid, geom",
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
        "input": "Hvor lang er den lengste veien i Ås?",
        "query": "SELECT objid, typeveg, ST_Length(ST_Transform(geom, 25833))/1000 AS senterlinje_km FROM forenklet_elveg_aas ORDER BY senterlinje_km DESC LIMIT 1;",
    },      
    {
        "input": "",
        "query": "",
    },        
]



