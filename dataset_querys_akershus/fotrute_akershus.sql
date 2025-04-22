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
				f.malemetode,
                k.kommunenavn 

            FROM 
                fotrute f 
            JOIN 
                kommuner k
            ON 
                ST_Intersects(f.geom, k.geom)
            WHERE 
                k.kommunenavn ILIKE 'Nannestad' 
                OR k.kommunenavn ILIKE 'Lunner'
                OR k.kommunenavn ILIKE 'Jevnaker' 
                OR k.kommunenavn ILIKE 'Nittedal'
                OR k.kommunenavn ILIKE 'Bærum'
                OR k.kommunenavn ILIKE 'Nesodden'
                OR k.kommunenavn ILIKE 'Asker'
                OR k.kommunenavn ILIKE 'Frogn' 
                OR k.kommunenavn ILIKE 'Vestby'
                OR k.kommunenavn ILIKE  'Ås'
                OR k.kommunenavn ILIKE  'Nordre Follo'
                OR k.kommunenavn ILIKE 'Aurskog-Høland'
                OR k.kommunenavn ILIKE 'Enebakk'
                OR k.kommunenavn ILIKE 'Lørenskog'
                OR k.kommunenavn ILIKE 'Rælingen'
                OR k.kommunenavn ILIKE 'Lillestrøm'
                OR k.kommunenavn ILIKE 'Nes'
                OR k.kommunenavn ILIKE 'Gjerdrum'
                OR k.kommunenavn ILIKE 'Ullensaker'
                OR k.kommunenavn ILIKE 'Eidsvoll'
                OR k.kommunenavn ILIKE 'Hurdal';