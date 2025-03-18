"Query-eksempel for fotrute fra FindinGeo databasen"

"Gjøre om geometry kolonnen til koordinater(long, lat)"
"SELECT ST_AsText(ST_GeomFromWKB(geom)) from public.fotrute_aas;"

"Hvor mange fotruter ble registrert etter 2015?"
SELECT COUNT(*) from tur_og_friluftsruter.fotrute_aas WHERE year > 2015

"Hvor mange fotruter har belysning på veien i Ås?"
"Belysning kategorien har verdien [0,1]"
SELECT COUNT(belysning) from tur_og_friluftsruter.fotrute_aas WHERE belysning = 1;


"Hvor mange grusstier er det i Ås?"
SELECT COUNT(underlagstype)
FROM tur_og_friluftsruter.fotrute_aas
WHERE underlagstyper = 2;


"Kan du hente ut alle fotruter som har blitt målt med flybåren laserskanner i Ås?"
"Hente ut objektid som tilhører samme målemetode"
SELECT objektid, malemetode 
FROM tur_og_friluftsruter.fotrute_aas
WHERE malemetode = 36;


"Kan du hente ut de 50 første registrerte fotrutene?"
SELECT objektid, datafangstdato
FROM tur_og_friluftsruter.fotrute_aas
ORDER BY datafangstdato ASC;
LIMIT 50;


"Hvilken fotrute ligger lengst vest?"
--Negative longitude are west of the meridian.
SELECT * 




"Når var siste oppdaterte fotrute?"
SELECT MAX(oppdateringsdato) 
FROM tur_og_friluftsruter.fotrute_aas;


"Hvor mange fotruter i Ås er lengre enn 10 km?"
SELECT COUNT(senterlinje)
FROM tur_og_friluftsruter.fotrute_aas
WHERE ST_senterlinje > 10000;



"Hvor mange kilometer med fotrute er det i Ås?"
SELECT ST_Transform(senterlinje, 25833) AS senterlinje_km   
FROM tur_og_friluftsruter.fotrute_aas
WHERE ST_Length(senterlinje) > 0;




"Hva er tettheten av fotruter i Ås?"


"Hvor mange fotruter er det i Ås?"
SELECT COUNT(objektid)
FROM tur_og_friluftsruter.fotrute_aas;


"Hvor mange kilometer er traktorveg i Ås?"
SELECT SUM(ST_Length(ST_Transform(senterlinje, 25833)) / 1000) AS total_length
FROM tur_og_friluftsruter.fotrute_aas
WHERE
    rutefolger = "TR"


"Hvor mange av fotrutene er frihåndstegning på skjerm?"
SELECT COUNT(malemetode == frihåndstegning på skjerm)
FROM tur_og_friluftsruter.fotrute_aas;



"Hvilken type fotrute er det flest av i Ås?"
SELECT COUNT(*) AS fotrute_count
FROM tur_og_friluftsruter.fotrute_aas
GROUP BY rutefolger
LIMIT 1;


"Hva er den lengste fotruten i Ås?"
SELECT MAX(senterlinje)
FROM tur_og_friluftsruter.fotrute_aas;


"Hvilke fotruter er kartlagt med en nøyaktighet på under 1 meter?"
SELECT objektid, noyaktighet
FROM tur_og_friluftsruter.fotrute_aas
WHERE noyaktighet < 1;


"Hvilke målemetoder er brukt for å kartlegge fotruter i Ås?"
SELECT DISTINCT(malemetode)
FROM tur_og_friluftsruter.fotrute_aas;

"I hvilket år ble det registrert flest fotruter?"
SELECT EXTRACT(YEAR FROM datafangstdato) AS år, COUNT(*) AS antall_registreringer
FROM tur_og_friluftsruter.fotrute_aas
GROUP BY år
ORDER BY antall_registreringer DESC
LIMIT 1;


"Finn alle turveier som ligger 20 meter i nærheten av Ås togstasjon"
"Visualisere med et bufferområde?"
SELECT ST_BUFFER(
    ST_SetSRID(ST_Point(10.7944517, 59.6632577), 4326),  -- 4326 is the WGS84 projection
    10000   -- buffer of 20 km in meters.
);

SELECT * 
FROM tur_og_friluftsruter.fotrute_aas
WHERE ST_INTERSECT()



"Hvilke ruter er beregnet med nøyaktighet på mer enn 200 cm?"
SELECT objid, noyaktighet
FROM tur_og_friluftsruter.fotrute_aas
WHERE noyaktighet < 200;