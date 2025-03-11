WITH kommuner AS (
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

-- Samler alle forenkelt_elveg.linjer-segmenter og beregner lengden på senterlinjen
forenklet_elveg_linjer AS ( 
            SELECT 
                f.objid AS objid_,
                ST_Union(f.senterlinje) AS geom,
                f.objtype AS rutetype,
                f.lokalid AS lokal,
                f.navnerom AS navn,
                f.versjonid AS versjon,
                f.datafangstdato AS datafangstdato_,
                f.oppdateringsdato AS oppdateringsdato_,
                f.verifiseringsdato AS verifiseringsdato_,
                f.kommunenummer AS kommunenummer,
                f.malemetode AS malemetode_,
                f.noyaktighet AS noyaktighet_,
                f.synbarhet AS synbarhet_,
                f.malemetodehoyde AS malemetodehoyde_,
                f.noyaktighethoyde AS noyaktighethoyde_,
                f.maksimaltavvik AS maksimaltavvik_,
                f.typeveg AS typeveg_,
                f.detaljniva AS detaljniva_,
                f.konnekteringslenke AS konnekteringslenke_,
                f.adressekode AS adressekode_,
                f.adressenavn AS adressenavn_,
                f.sideveg AS sideveg_,
                f.vegkategori AS vegkategori_,
                f.vegfase AS vegfase_,
                f.vegnummer AS vegnummer_
                
            FROM 
                forenklet_elveg.linjer f
            GROUP BY 
                f.objid,
                f.objtype,
                f.lokalid,
                f.navnerom,
                f.versjonid,
                f.datafangstdato,
                f.oppdateringsdato,
                f.verifiseringsdato,
                f.kommunenummer,
                f.malemetode,
                f.noyaktighet,
                f.synbarhet,
                f.malemetodehoyde,
                f.noyaktighethoyde,
                f.maksimaltavvik,
                f.typeveg,
                f.detaljniva,
                f.konnekteringslenke,
                f.adressekode,
                f.adressenavn,
                f.sideveg,
                f.vegkategori,
                f.vegfase,
                f.vegnummer
)

            SELECT 
                f.objid_,
                f.geom,
                f.rutetype,
                f.lokal,
                f.navn,
                f.versjon,
                f.datafangstdato_,
                f.oppdateringsdato_,
                f.verifiseringsdato_,
                f.kommunenummer,
                f.malemetode_,
                f.noyaktighet_,
                f.synbarhet_,
                f.malemetodehoyde_,
                f.noyaktighethoyde_,
                f.maksimaltavvik_,
                f.typeveg_,
                f.detaljniva_,
                f.konnekteringslenke_,
                f.adressekode_,
                f.adressenavn_,
                f.sideveg_,
                f.vegkategori_,
                f.vegfase_,
                f.vegnummer_
            FROM 
                forenklet_elveg_linjer f
            JOIN 
                kommuner k 
            ON 
                ST_Intersects(f.geom, k.geom)
            WHERE 
                k.kommunenavn ILIKE 'Ås';