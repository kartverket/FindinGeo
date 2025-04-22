from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.prompts.few_shot import FewShotPromptTemplate


# Few-shot prompt for SQL queries
examples_fewshot = [
    {   
        "input": "Hvor mange fotruter ble registrert etter 2015?", 
        "query": "SELECT COUNT(*), EXTRACT(YEAR FROM datafangstdato) FROM fotrute_aas WHERE EXTRACT(YEAR FROM datafangstdato) > 2015 GROUP BY EXTRACT(YEAR FROM datafangstdato);"
    },
    {
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
        "query": "SELECT COUNT(ST_Length(ST_Transform(geom, 25833)) > 10000) FROM fotrute_aas;",
    },        
    {
        "input": "Hvilken type fotrute er det flest av i Ås?",
        "query": "SELECT COUNT(*) AS fotrute_count FROM fotrute_aas GROUP BY rutefolger LIMIT 1;",
    },      
    {
        "input": "I hvilket år ble det registrert flest fotruter?",
        "query": "SELECT EXTRACT(YEAR FROM datafangstdato) AS år, COUNT(*) AS antall_registreringer FROM fotrute_aas GROUP BY år ORDER BY antall_registreringer DESC LIMIT 1;",
    },
    {   "input": "Kan du hente ut alle veier som har blitt målt med stereoinstrument i Ås?", 
        "query": "SELECT objid, datafangstdato, malemetode FROM forenklet_elveg_aas ORDER BY datafangstdato ASC LIMIT 50;",
    },
    {   
        "input": "Hvor mange veier ble registrert i 2023?", 
        "query": "SELECT EXTRACT(YEAR FROM datafangstdato) AS år, COUNT(*) AS antall_registreringer FROM forenklet_elveg_aas WHERE år = 2023 GROUP BY år ORDER BY antall_registreringer DESC;",
    },
    {
        "input": "Hvor mange riksveier er det i Ås?",
        "query": "SELECT COUNT(vegkategori) FROM forenklet_elveg_aas WHERE vegkategori = 'R';",
    },
    {
        "input": "Hvor mange gangveier finnes i Ås?",
        "query": "SELECT COUNT(*) FROM forenklet_elveg_aas WHERE typeveg = 'gangveg';",
    },
    {
        "input": "Hvor mange sideveier er det i Ås?",
        "query": "SELECT COUNT(sideveg) FROM forenklet_elveg_aas WHERE sideveg = 'JA';",
    },
    {
        "input": "Hvor mange veier er det i Brekkeskog?",
        "query": "SELECT COUNT(*) FROM forenklet_elveg_aas WHERE adressenavn LIKE '%Brekkeskog%';"
    },
    {
        "input": "Kan du hente ut de 50 første registrerte veiene og deres målemetode?",
        "query": "SELECT objid, datafangstdato, malemetode FROM forenklet_elveg_aas ORDER BY datafangstdato ASC LIMIT 50;",
    },
    {
        "input": "Hvor mange bilveier er det i Ås?",
        "query": "SELECT COUNT(typeveg) FROM forenklet_elveg_aas WHERE typeveg = 'enkelBilveg';",
    },
    {
        "input": "Hvor mye varierer målingene i nøyaktighet?",
        "query": "SELECT MAX(noyaktighet), MIN(noyaktighet) FROM forenklet_elveg_aas",
    },
    {
        "input": "Hvor mange veier eldre enn 2015 har ikke blitt oppdatert?",
        "query": "SELECT COUNT(*) FROM forenklet_elveg_aas WHERE EXTRACT(YEAR FROM datafangstdato) < 2015 AND oppdateringsdato IS NULL",
    },
    {
        "input": "Hvor mange veier er oppdatert i det hele tatt?",
        "query": "SELECT COUNT(*) FROM forenklet_elveg_aas WHERE oppdateringsdato IS NOT NULL;",
    },
    {
        "input": "Hvilket år ble flest veier registrert, og hvor mange var det?",
        "query": "SELECT EXTRACT(YEAR FROM datafangstdato) AS år, COUNT(*) AS antall FROM forenklet_elveg_aas GROUP BY år ORDER BY antall DESC LIMIT 1;",
    },
    {
        "input": "Finn de tre lengste veiene i Ås",
        "query": "SELECT objid, adressenavn, geom FROM forenklet_elveg_aas ORDER BY ST_LENGTH(geom) DESC LIMIT 3;",
    },
    {
        "input": "Hvilke vegkategorier finnes i datasettet og hvor mange veier finnes i hver kategori?",
        "query": "SELECT v.description AS vegkategori_beskrivelse, COUNT(*) AS antall_veier FROM forenklet_elveg_aas e JOIN forenklet_elveg_aas_vegkategori v ON e.vegkategori = v.identifier GROUP BY v.description ORDER BY antall_veier DESC;",
    },        
]

prefix = """
You are an agent designed to interact with a PostgreSQL database. You may be asked questions in either English or Norwegian.

Your task is to:

1. Translate the user's question into a syntactically correct PostgreSQL query.
2. Double-check your query exactly once using the sql_db_query_checker.
3. Execute the checked query using sql_db_query.
4. Return your final answer clearly, including both:
   - The exact SQL query used.
   - The result of the query:
     The answer to the user's question based on the query results. The answer should be logically formulated, e.g. "Den lengste bilvegen i Ås er objektid 39320 med en lengde på 3056 m." (Always remember to secify the unit of measure, with correct placement of delimiter.).

Guidelines you MUST follow:

- DO NOT execute DML statements (INSERT, UPDATE, DELETE, DROP, etc.).
- DO NOT repeat query checks more than once if the query is confirmed valid.
- DO NOT create or answer new questions other than the one asked by the user.
- If your query is invalid according to sql_db_query_checker, fix it and check once more before executing.
- If the user's question isn't related to the database or is unclear, respond clearly with: "I don't know."

Tools you have available:
{tool_names}

Tool descriptions:
{tools}

Use the following structured format for your reasoning process:

Question: The original question provided by the user.
Thought: Think clearly about what you need to do to answer the user's question.
Action: Choose ONE from [sql_db_query, sql_db_schema, sql_db_list_tables, sql_db_query_checker].
Action Input: Provide the input needed for the action.
Observation: The output or results of your action.

[You may repeat Thought/Action/Action Input/Observation ONLY if the first query-check fails.]

Thought: Now I have the correct query and results. My query always contains a column with relevant geometry.

Final Answer: [SQL Query: [exact SQL query used]] Nicely formatted answer (with appropriate number of decimal places) to the user's question based on the query results.
"""


suffix = """
User input: {input}
{agent_scratchpad}
\nSQL query:
"""

# Finne chatGroq prompt template 

#https://python.langchain.com/docs/how_to/sql_prompting/
example_prompt = PromptTemplate.from_template("User input: {input}\nSQL query: {query}")
few_shot_prompt = FewShotPromptTemplate(
    examples=examples_fewshot,
    example_prompt=example_prompt,
    prefix=prefix,
    suffix=suffix,
    input_variables=["input"]
)


