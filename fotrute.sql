"Query-eksempel for fotrute fra FindinGeo databasen"

"Gjøre om geometry kolonnen til koordinater(long, lat)"
"SELECT ST_AsText(ST_GeomFromWKB(geom)) from public.fotrute_aas;"

"Hvor mange fotruter ble registrert etter 2015?"
"Svar: 7 rader"
SELECT COUNT(*), EXTRACT(YEAR FROM datafangstdato) 
FROM fotrute_aas
WHERE EXTRACT(YEAR FROM datafangstdato) > 2015
GROUP BY EXTRACT(YEAR FROM datafangstdato);


"Kan du hente ut alle fotruter som har blitt målt med stereoinstrument i Ås?" 
"Hente ut objektid som tilhører samme målemetode"
SELECT objtype, malemetode 
FROM fotrute_aas
WHERE malemetode = '20';


"Kan du hente ut de 50 første registrerte fotrutene?"
SELECT objtype, datafangstdato
FROM fotrute_aas
ORDER BY datafangstdato ASC
LIMIT 50;

"Hvilken fotrute ligger lengst vest i Ås?"
--Negative longitude are west of the meridian.
SELECT *, ST_XMin(geom) AS min_lengdegrad
FROM fotrute_aas
ORDER BY min_lengdegrad ASC
LIMIT 1;


"Når var siste oppdaterte fotrute?"
SELECT MAX(oppdateringsdato) 
FROM fotrute_aas;


"Hvor mange fotruter i Ås er lengre enn 10 km?"
"Svar: 0"
SELECT COUNT(*) 
FROM fotrute_aas 
WHERE ST_Length(ST_Transform(geom, 25833)) > 10000;



"Hvor mange kilometer med fotrute er det i Ås?"
"Svar: 107346.91915878214 "
SELECT SUM(ST_Length(ST_Transform(geom, 25833))) AS senterlinje_km   
FROM fotrute_aas
WHERE ST_Length(geom) > 0;




"Hva er tettheten av fotruter i Ås?"


"Hvor mange fotruter er det i Ås?"
"Svar: 456"
SELECT COUNT(objid)
FROM fotrute_aas;


"Hvor mange kilometer er traktorveg i Ås?"
"Svar: 15005.03967010296"
SELECT SUM(ST_Length(ST_Transform(geom, 25833))) AS senterlinje_km   
FROM fotrute_aas
WHERE rutefolger like 'TR%'


"Hvor mange av fotrutene er frihåndstegning på skjerm?"
SELECT COUNT(malemetode = frihåndstegning på skjerm)
FROM fotrute_aas;
WHERE malemetode = 82;


"Hvilken type fotrute er det flest av i Ås?"
"Svar: 67"
SELECT COUNT(*) AS fotrute_count
FROM fotrute_aas
GROUP BY rutefolger
LIMIT 1;


"Hva er den lengste fotruten i Ås?"
SELECT MAX(senterlinje)
FROM fotrute_aas;


"Hvilke fotruter er kartlagt med en nøyaktighet på under 1 meter?"
SELECT objektid, noyaktighet
FROM fotrute_aas
WHERE noyaktighet < 1;


"Hvilke målemetoder er brukt for å kartlegge fotruter i Ås?"
SELECT DISTINCT(malemetode)
FROM fotrute_aas;

"I hvilket år ble det registrert flest fotruter?"
"Svar: 2014, 123"
SELECT EXTRACT(YEAR FROM datafangstdato) AS år, COUNT(*) AS antall_registreringer
FROM fotrute_aas
GROUP BY år
ORDER BY antall_registreringer DESC
LIMIT 1;


"Finn alle turveier som ligger 2 km i nærheten av Ås togstasjon"
"Visualisere med et bufferområde?"
"Denne funker ikke!!"
SELECT ST_AsText(ST_GeomFromWKB(geom)) from public.fotrute_aas;
SELECT * from geom 
FROM public.fotrute_aas
WHERE ST_distance(
    ST_Transform(ST_SetRID(ST_MakePoint(263148.72, 6621417.34), 4258), 3857), 
    ST_Transform(geometry, 3857)
) <= 2000;



"Hvilke ruter er beregnet med nøyaktighet på mer enn 200 cm?"
SELECT objid, noyaktighet
FROM fotrute_aas
WHERE noyaktighet < 200;



examples_fotrute = [
    {   "input": "Hvor mange fotruter ble registrert etter 2015?", 
        "query": "SELECT COUNT(*), EXTRACT(YEAR FROM datafangstdato) FROM fotrute_aas WHERE EXTRACT(YEAR FROM datafangstdato) > 2015 GROUP BY EXTRACT(YEAR FROM datafangstdato);",
    },
    {   "input": "Kan du hente ut alle fotruter som har blitt målt med stereoinstrument i Ås?", 
        "query": "SELECT objtype, malemetode  FROM fotrute_aas WHERE malemetode = '20';",
    },
    {,
        "input": "Kan du hente ut de 50 første registrerte fotrutene?",
        "query": "SELECT objtype, datafangstdato FROM fotrute_aas ORDER BY datafangstdato ASC LIMIT 50;",
    },
    {
        "input": "Hvilke ruter er beregnet med nøyaktighet på mer enn 200 cm?",
        "query": "SELECT objid, noyaktighet FROM fotrute_aas WHERE noyaktighet < 200;",
    },
    {
        "input": "Find the total duration of all tracks.",
        "query": "SELECT SUM(Milliseconds) FROM Track;",
    },
    {
        "input": "Hvilke målemetoder er brukt for å kartlegge fotruter i Ås?",
        "query": "SELECT DISTINCT(malemetode) FROM fotrute_aas;",
    },
    {
        "input": "Hvilke fotruter er kartlagt med en nøyaktighet på under 1 meter?",
        "query": "SELECT objektid, noyaktighet FROM fotrute_aas WHERE noyaktighet < 1;",
    },
    {
        "input": "Hvor mange fotruter er det i Ås?",
        "query": "SELECT COUNT(objid) FROM fotrute_aas;",
    },
    {
        "input": "Når var siste oppdaterte fotrute?",
        "query": "SELECT MAX(oppdateringsdato)  FROM fotrute_aas;",
    },
    {
        "input": "Hva er den lengste fotruten i Ås?",
        "query": "SELECT MAX(senterlinje) FROM fotrute_aas;",
    },
    {
        "input": "Hvor mange kilometer med fotrute er det i Ås?",
        "query": "SELECT SUM(ST_Length(ST_Transform(geom, 25833))) AS senterlinje_km FROM fotrute_aas WHERE ST_Length(geom) > 0;",
    },
    {
        "input": "Hvor mange kilometer er traktorveg i Ås?",
        "query": "SELECT SUM(ST_Length(ST_Transform(geom, 25833))) AS senterlinje_km FROM fotrute_aasWHERE rutefolger like 'TR%'",
    },
    {
        "input": "Hvilken fotrute ligger lengst vest i Ås?",
        "query": "SELECT *, ST_XMin(geom) AS min_lengdegrad FROM fotrute_aas ORDER BY min_lengdegrad ASC LIMIT 1;",
    },
    {
        "input": "Hvor mange fotruter i Ås er lengre enn 10 km?",
        "query": "SELECT COUNT(*) FROM fotrute_aas WHERE ST_Length(ST_Transform(geom, 25833)) > 10000;",
    },        
    {
        "input": "Hvilken type fotrute er det flest av i Ås?",
        "query": "SELECT COUNT(*) AS fotrute_count FROM fotrute_aas GROUP BY rutefolger LIMIT 1;",
    },      
    {
        "input": "I hvilket år ble det registrert flest fotruter?",
        "query": "SELECT EXTRACT(YEAR FROM datafangstdato) AS år, COUNT(*) AS antall_registreringer FROM fotrute_aas GROUP BY år ORDER BY antall_registreringer DESC LIMIT 1;",
    },        
]