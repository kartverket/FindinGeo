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
                -- Samler alle skiløype-segmenter og beregner lengden på senterlinjen
                skiløyper AS (
                    SELECT 
                        s.objid AS skiloype_id,
                        ST_Union(s.senterlinje) AS geom
                    FROM 
                        tur_og_friluftsruter.skiloype s
                    GROUP BY 
                        s.objid
                )
                SELECT 
                    s.skiloype_id,
                    s.geom
                FROM 
                    skiløyper s
                JOIN 
                    kommuner k 
                ON 
                    ST_Intersects(s.geom, k.geom)
                WHERE 
                    k.kommunenavn ILIKE 'Ås'