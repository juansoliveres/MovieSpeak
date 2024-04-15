from django.views import View
from django.shortcuts import render, redirect

from sqltranslator.actions import _run_sql_pipeline, _run_sql_pipeline_GPT4, run_login_pipeline

class IndexView(View):
    def get(self, request):
        return render(request, "sqltranslator/index.html")

    def post(self, request):
        # handle POST request here
        input_query: str = request.POST["input_text"]
        # do something with input_text
        output_text, is_valid, sql_query = _run_sql_pipeline_GPT4(
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

class LoginView(View):
    def get(self, request):
        return render(request, "sqltranslator/login_traktid.html")

    def post(self, request):
        # Extract the Trakt username from the POST request
        trakt_username = request.POST.get("trakt_username")

        # Run part of the processing with the Trakt username
        run_login_pipeline(trakt_username)

        request.session['trakt_username'] = trakt_username

        # Store the processed data in the session or pass it to the next view as needed 
        # Redirect to the IndexView with the processed data
        # Note: You might need to adapt this depending on how you plan to use the data
        return redirect('index')  # Ensure you have a URL named 'index_view_url_name' pointing to IndexView