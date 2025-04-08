SELECT 
    objid,
    senterlinje AS geom,
    objtype,
    lokalid,
    navnerom,
    versjonid,
    datafangstdato,
    oppdateringsdato,
    verifiseringsdato,
    kommunenummer,
    malemetode,
    noyaktighet,
    synbarhet,
    malemetodehoyde,
    noyaktighethoyde,
    maksimaltavvik,
    typeveg,
    detaljniva,
    konnekteringslenke,
    adressekode,
    adressenavn,
    sideveg,
    vegkategori,
    vegfase,
    vegnummer
FROM 
    "forenklet_elveg"."linjer"
WHERE 
    kommunenummer = '3238'
    OR kommunenummer = '3234'
    OR kommunenummer = '3236'
    OR kommunenummer = '3232'
    OR kommunenummer = '3201'
    OR kommunenummer = '3212'
    OR kommunenummer = '3203'
    OR kommunenummer = '3214'
    OR kommunenummer = '3216'
    OR kommunenummer = '3218'
    OR kommunenummer = '3207'
    OR kommunenummer = '3226'
    OR kommunenummer = '3220'
    OR kommunenummer = '3222'
    OR kommunenummer = '3224'
    OR kommunenummer = '3205'
    OR kommunenummer = '3228'
    OR kommunenummer = '3230'
    OR kommunenummer = '3209'
    OR kommunenummer = '3240'
    OR kommunenummer = '3242';