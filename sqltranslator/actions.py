from typing import Tuple

from django.contrib import admin, messages
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils.timezone import now

from sqltranslator.gen_ai.pipelines import pipeline

def _run_sql_pipeline(
    request: HttpRequest, input_query: str
) -> Tuple[str, bool, str]:
    response, is_valid, sql, prompt = pipeline(input_query=input_query)
    return response, is_valid, sql