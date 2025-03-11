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
                k.kommunenavn ILIKE 'Ås'