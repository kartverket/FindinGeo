"Query-eksempel for forenklet_elveg fra FindinGeo databasen"

"Hvor mange typer veier ble registrert i 2020?"
SELECT COUNT(*) from forenklet_elveg.linjer WHERE year = 2020


"Hvor mange bilveier er det i Ås?"
SELECT COUNT(typeveg)
FROM forenklet_elveg.linjer
WHERE typeveg = "enkelBilveg";


" Hvor mange riksveier er det i Ås?"
SELECT COUNT(vegkategori)
FROM forenklet_elveg.linjer
WHERE vegkategori = "R";


"Kan du hente ut alle veier som har blitt målt med stereoinstrument i Ås?"
SELECT objid, malemetode
FROM forenklet_elveg.linjer
WHERE malemetode = "stereoinstrument";

"Kan du hente ut de 50 første registrerte veiene og deres målemetode?"
SELECT objid, datafangstdato, malemetode
FROM forenklet_elveg.linjer
ORDER BY datafangstdato ASC;
LIMIT 50;


