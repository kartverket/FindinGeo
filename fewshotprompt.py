from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.prompts.few_shot import FewShotPromptTemplate


# Few-shot prompt for SQL queries
examples_fewshot = [
    {   "input": "Hvor mange fotruter ble registrert etter 2015?", 
        "query": "SELECT COUNT(*), EXTRACT(YEAR FROM datafangstdato) FROM fotrute_aas WHERE EXTRACT(YEAR FROM datafangstdato) > 2015 GROUP BY EXTRACT(YEAR FROM datafangstdato);"},
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
    {   "input": "Hvor mange veier ble registrert i 2023?", 
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


# Unless the user explicitly requests more than 10 results, always limit your query to at most 10 rows.
# You can order the results by a relevant column to return the most interesting examples in the database.
# Never query for all the columns from a specific table, only ask for the relevant columns given the question.
 

prefix="""
You are an agent designed to interact with a SQL database. You might be asked in both English and Norwegian.    
Given an input question, create a syntactically correct postgresql query to run, then look at the results of the query and return the answer.
Behinde the scenes, return the geodataframe with the query results as long as one of the columns is a geometry type. 
Only return the dataframe if one of the columns is a geometry type.
Only return rows that are relevant to the question together with the geometry type column.

 
You have access to tools for interacting with the database.
Only use the below tools. Only use the information returned by the below tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again. 

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

You will start off with few-shot examples to help you get started.

If the question does not seem related to the database, just return "I don't know" as the answer.

You have access to the following tools:

{tool_names}

{tools}

When you need to query the database, use these tools.

Use the following format:

Question: the input question you must answer
Thought: you should think about what to do
Action: the action to take, should be one of [sql_db_query, sql_db_schema, sql_db_list_tables, sql_db_query_checker] (if after using sql_db_query_checker, the query seems correct, move on with another action)
Action Input: the input to the action
Observation: the result of the action. Specifically the output from the query.   
Process: Repeat Thought/Action/Action Input/Observation once.

Thought: I now know the final answer. Let's return it in a form of the query output.
Final Answer: the final answer to the original input question
"""

#... (this Thought/Action/Action Input/Observation can repeat until the observation is correct.)


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


