from typing import Tuple

from django.contrib import admin, messages
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils.timezone import now

from sqltranslator.gen_ai.pipelines import pipeline, pipeline_GPT4, pipelines_login

""" def _run_sql_pipeline(
    request: HttpRequest, input_query: str
) -> Tuple[str, bool, str]:
    response, is_valid, sql, prompt = pipeline(input_query=input_query)
    return response, is_valid, sql """

def _run_sql_pipeline(request: HttpRequest, input_query: str) -> Tuple[str, bool, str]:
    # Retrieve trakt_username from session
    trakt_username = request.session.get('trakt_username')
    
    response, is_valid, sql, prompt = pipeline(input_query=input_query, trakt_username=trakt_username)
    return response, is_valid, sql

def _run_sql_pipeline_GPT4(request: HttpRequest, input_query: str) -> Tuple[str, bool, str]:
    # Retrieve trakt_username from session
    trakt_username = request.session.get('trakt_username')
    
    response, is_valid, sql, prompt, tmdb_ids = pipeline_GPT4(input_query=input_query, trakt_username=trakt_username)
    return response, is_valid, sql, tmdb_ids

def run_login_pipeline(trakt_username: str) -> Tuple[str, bool, str, str]:
    try:
        # Call pipelines_login function with the provided username
        message, success, user_data, additional_info = pipelines_login(trakt_username)
        
        # Handle the success scenario, e.g., logging, notifying the user, etc.
        if success:
            print("Login pipeline executed successfully for:", trakt_username)
        else:
            # Handle failure scenario
            print("Login pipeline failed for:", trakt_username)
        
        # Return the output for further processing or feedback
        return message, success, user_data, additional_info
    except Exception as e:
        # Handle any unexpected errors during the pipeline execution
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        # Return an error tuple, assuming False for success, and the error message
        return error_message, False, '', ''