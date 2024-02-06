import requests
import json
from typing import Dict, List, Literal, Optional, Tuple, Union
from sqltranslator.gen_ai.config import HEADERS, OPENAI_API_KEY
from sqltranslator.gen_ai.trakt.trakt_functions import read_trakt_history, select_title_and_id, add_movie_details1
from sqltranslator.gen_ai.gpt.textgeneration import TextGeneratorGPT3_5
from sqltranslator.gen_ai.mysql.mysql_interactions import send_df_to_mysql, query_mysql, get_full_table_schema
from openai import OpenAI

def pipeline(input_query: str) -> Tuple[str, bool, str, str]:
    """
    This function takes an input query in natural language and returns
    the results of a SQL query executed on MySQL.

    The function first loads the user watchlist file from Trakt into memory. It then 
    uses the `GPT` model to predict the SQL query given the natural language query text. 
    The predicted SQL query is then refined with a second call to the `GPT` model, using a prompt-fixing template.
    The watchlist is then sent to MySQL DB. Finally, the SQL query is executed on MySQL and the results are returned.
    If the query is not valid, the `GPT` model is used to fix the SQL query and the query is executed again.
    
    Args
    ----
    - `input_query` (str): The natural language query text.

    Returns
    -------
    - `response` (str): The response from MySQL.
    - `is_valid` (bool): Whether the SQL query is valid (successful execution).
    - `sql` (str): The SQL query itself.
    - `prompt` (str): The final prompt passed to the LLM model.
    """
    # Retrieving user's trakt history. When view is ready change juan_trakt by user_name
    trakt_history = read_trakt_history('juan_trakt') 
    # Selecting the values in which we are interested (title and id) from the trakt_history file
    title_imdbid = select_title_and_id(trakt_history)
    # Add movie details to the list of movies
    final_df = add_movie_details1(title_imdbid)
    # Send created dataframe to MySQL DB
    send_df_to_mysql(final_df, 'juan_trakt')
    # Retrieve the schema from the table in MySQL
    text_examples = get_full_table_schema('show create table test.movies2;')
    print(text_examples)
    # Instantiate the predictor model
    model = TextGeneratorGPT3_5(OPENAI_API_KEY)
    reference_sql, prompt = model.predict_sql(
        text=input_query,
        text_examples=text_examples,
        # extract_sql=True,
    )

    # VER QUE TIPO DE VARIABLE DEVUELVE LA FUNCION PARA EJECUTAR LAS QUERIES EN BIGQUERY
    final_response, is_valid, sql_query = query_mysql(reference_sql)

    return final_response, is_valid, sql_query, prompt





