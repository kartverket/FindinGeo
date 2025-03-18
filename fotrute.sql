"Query-eksempel for fotrute fra FindinGeo databasen"

"Hvor mange fotruter ble registrert etter 2015?"
SELECT COUNT(*) from tur_og_friluftsruter.fotrute WHERE year > 2015

"Hvor mange fotruter har belysning på veien i Ås?"
"Belysning kategorien har verdien [0,1]"
SELECT COUNT(belysning) from tur_og_friluftsruter.fotrute WHERE belysning = 1;


"Hvor mange grusstier er det i Ås?"
SELECT COUNT(underlagstype)
FROM tur_og_friluftsruter.fotrute 
WHERE underlagstyper = 2;


"Kan du hente ut alle fotruter som har blitt målt med flybåren laserskanner i Ås?"
"Hente ut objektid som tilhører samme målemetode"
SELECT objektid, malemetode 
FROM tur_og_friluftsruter.fotrute
WHERE malemetode = 36;


"Kan du hente ut de 50 første registrerte fotrutene?"
SELECT objektid, datafangstdato
FROM tur_og_friluftsruter.fotrute
ORDER BY datafangstdato ASC;
LIMIT 50;


"Hvilken fotrute ligger lengst vest?"


"Når var siste oppdaterte fotrute?"


"Hvor mange fotruter i Ås er lengre enn 10 km?"


"Hvor mange kilometer med fotrute er det i Ås?"


"Hva er tettheten av fotruter i Ås?"
"Hvor mange fotruter er det i Ås?"


"Hvor mange kilometer er traktorveg i Ås?"


"Hvor mange av fotrutene er frihåndstegning på skjerm?"

"Hvilken type fotrute er det flest av i Ås?"

"Hva er den lengste fotruten i Ås?"

"Hvilke fotruter er kartlagt med en nøyaktighet på under 1 meter?"


"Hvilke målemetoder er brukt for å kartlegge fotruter i Ås?"

"I hvilket år ble det registrert flest fotruter?"