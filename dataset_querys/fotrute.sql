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
					f.objid AS objid, 
                    ST_Union(f.senterlinje) AS geom,
					f.objtype AS objtype,
                    ST_Length(ST_Union(f.senterlinje)) AS senterlinje,
                    f.lokalid AS lokalid,
                    f.navnerom AS navnerom,
                    f.versjonid AS versjonid,
                    f.datafangstdato AS datafangstdato,
                    f.oppdateringsdato AS oppdateringsdato,
                    f.noyaktighet AS noyaktighet,
                    f.opphav AS opphav,
                    f.omradeid AS omradeid,
                    f.informasjon AS informasjon,
                    f.rutefolger AS rutefolger,
                    f.malemetode AS malemetode
					
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
					f.objid,
					f.geom,
					f.objtype,
					f.senterlinje,
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


            FROM 
                fotrute f
            JOIN 
                kommuner k 
            ON 
                ST_Intersects(f.geom, k.geom)
            WHERE 
                k.kommunenavn ILIKE 'Ås'





















