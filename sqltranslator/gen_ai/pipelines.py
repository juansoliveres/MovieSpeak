import requests
import json
import asyncio
import aiohttp
import logging

from typing import Dict, List, Literal, Optional, Tuple, Union
from sqltranslator.gen_ai.config import HEADERS, OPENAI_API_KEY
from sqltranslator.gen_ai.trakt.trakt_functions import read_trakt_history, select_title_and_id, add_movie_details1
from sqltranslator.gen_ai.trakt.trakt_functions_optimized import retrieve_trakt_history, main
from sqltranslator.gen_ai.gpt.textgeneration import TextGeneratorGPT3_5, TextGeneratorGPT4
from sqltranslator.gen_ai.mysql.mysql_interactions import send_df_to_mysql, query_mysql, get_full_table_schema
from sqltranslator.gen_ai.mysql.postgresql_interactions import query_postgresql, get_postgresql_table_schema, execute_postgresql_command, send_df_to_postgresql
from openai import OpenAI

def pipeline(input_query: str, trakt_username: str) -> Tuple[str, bool, str, str]:
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
    # Retrieve the schema from the table in MySQL
    text_examples = get_postgresql_table_schema(trakt_username)
    print(text_examples)
    # Instantiate the predictor model
    model = TextGeneratorGPT3_5(OPENAI_API_KEY)
    reference_sql, prompt = model.predict_sql(
        text=input_query,
        text_examples=text_examples,
        trakt_username = trakt_username,
        # extract_sql=True,
    )

    final_response, is_valid, sql_query = query_postgresql(reference_sql)
    
    if is_valid == True:
        return final_response, is_valid, sql_query, prompt
    
    elif not is_valid:
        # final_response will be equal to the error
        print('Original SQL failed, proceeding to fix it!')
        improved_sql, prompt = model.fix_sql(
            original_sql = sql_query,
            error_msg = final_response,
            )
        final_response, is_valid, sql_query = query_postgresql(improved_sql)
        return final_response, is_valid, sql_query, prompt

def pipeline_GPT4(input_query: str, trakt_username: str) -> Tuple[str, bool, str, str]:
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
    # Retrieve the schema from the table in MySQL
    text_examples = get_postgresql_table_schema(trakt_username)
    print(text_examples)
    # Instantiate the predictor model
    model = TextGeneratorGPT4(OPENAI_API_KEY)
    reference_sql, prompt = model.predict_sql(
        text=input_query,
        text_examples=text_examples,
        trakt_username = trakt_username,
        # extract_sql=True,
    )

    final_response, is_valid, sql_query = query_postgresql(reference_sql)

    if is_valid == True:
        return final_response, is_valid, sql_query, prompt
    
    elif not is_valid:
        # final_response will be equal to the error
        print('Original SQL failed, proceeding to fix it!')
        improved_sql, fix_prompt = model.fix_sql(
            original_sql = sql_query,
            error_msg = final_response,
            )
        final_response, is_valid, sql_query = query_postgresql(improved_sql)
        return final_response, is_valid, sql_query, fix_prompt


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def pipelines_login(trakt_username: str) -> Tuple[str, bool, str, str]:
    """
    Processes a Trakt user's watch history to generate and store relevant movie data in a MySQL database.
    This function performs several steps to process and utilize a user's watch history from Trakt. 
    It first retrieves the watch history for the given username, then selects specific details (title and IMDb ID) 
    from this data. Next, it enriches this list with additional movie details through an external API call or database. 
    This enriched data is then formatted into a DataFrame, which is subsequently sent to a MySQL database for storage.
    Lastly, it prints a confirmation message upon successful execution.
    
    The process assumes that the Trakt history is available and accessible, and that the MySQL database is set up to 
    receive and store the data. It also assumes the existence of functions for data retrieval, processing, and database communication.

    Args:
    ----
    - `trakt_username` (str): The Trakt username for which to process the watch history.

    Returns:
    -------
    - `message` (str): A confirmation message indicating the outcome of the database operation.
    - `is_valid` (bool): Indicates whether the database operation was successful.
    - `user_data` (str): Processed user data that was sent to the MySQL database.
    - `additional_info` (str): Any additional information or context about the operation.

    Note:
    -----
    This function is a high-level overview of processing a user's watch history from Trakt. 
    Implementers should ensure that all called functions (`read_trakt_history`, `select_title_and_id`, 
    `add_movie_details1`, `send_df_to_mysql`) are defined and properly handle errors and exceptions 
    that may arise during their execution.
    """
    try:
        # Create a new event loop for the current thread if necessary
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError("The event loop is closed")
        except RuntimeError as e:
            logger.info("Creating a new event loop: %s", e)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Now you can run your async code using the loop
        trakt_history = retrieve_trakt_history(trakt_username)  # Assuming this is synchronous
        final_df = loop.run_until_complete(main(trakt_history))

        # Proceed with your synchronous code
        print(final_df.head())
        send_df_to_postgresql(final_df, trakt_username)
        
        alter_genres = f"ALTER TABLE {trakt_username} ALTER COLUMN genres TYPE text[] USING string_to_array(genres, ',');"
        alter_actors = f"ALTER TABLE {trakt_username} ALTER COLUMN actors TYPE text[] USING string_to_array(actors, ',');"

        try: 
            execute_postgresql_command(alter_genres)
            execute_postgresql_command(alter_actors)
            return True
        except Exception as e:
            return('The command was not succesfully executed') 
        
        return "Successfully sent dataframe to MySQL DB.", True, "Data processed for user: " + trakt_username, "No additional info."
    except Exception as e:
        logger.error("An error occurred in the login pipeline for %s: %s", trakt_username, e, exc_info=True)
        return f"Failed to process data for {trakt_username}: {str(e)}", False, '', "Error occurred during processing."
    finally:
        # It's a good practice to close the loop at the end if you created a new one
        if loop and not loop.is_running():
            loop.close()