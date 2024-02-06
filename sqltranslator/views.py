from django.views import View
from django.shortcuts import render

from sqltranslator.actions import _run_sql_pipeline

class IndexView(View):
    def get(self, request):
        return render(request, "sqltranslator/index.html")

    def post(self, request):
        # handle POST request here
        input_query: str = request.POST["input_text"]
        # do something with input_text
        output_text, is_valid, sql_query = _run_sql_pipeline(
            request=request, input_query=input_query
        )
        return render(
            request,
            "sqltranslator/index.html",
            {
                "output_text": output_text,
                "input_text": input_query,
                "is_valid": is_valid,
                "sql_query": sql_query,
            },
        )