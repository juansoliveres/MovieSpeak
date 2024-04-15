from django.contrib import admin
from typing import List

import pandas as pd
from django.contrib import admin
from django.db.models import Count, QuerySet
from django.http import HttpRequest, HttpResponse
from django.template.defaultfilters import truncatewords
from sqltranslator.actions import (
    _run_sql_pipeline,
    _run_sql_pipeline_GPT4
)
from sqltranslator.models import (
    GPT3_5,
    GPT_4
)


@admin.display(description="Export selected objects to Excel")
def export_xls(
    modeladmin: admin.ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet,
) -> HttpResponse:
    """
    Export a queryset of SQL queries to an Excel file.

    Args
    ----
    - `modeladmin` (django.contrib.admin.ModelAdmin): The admin model instance.
    - `request` (django.http.HttpRequest): The HTTP request object.
    - `queryset` (django.db.models.query.QuerySet): The queryset of SQL queries to export.

    Returns
    -------
    - `django.http.HttpResponse`: The HTTP response with the Excel file.
    """
    # Create an HTTP response with the MIME type for Excel files and a filename.
    response = HttpResponse(content_type="application/vnd.ms-excel")
    response["Content-Disposition"] = "attachment; filename=SQLqueries.xlsx"

    # Define the columns to include in the Excel file.
    columns: List[str] = [
        "name",
        "query",
        "prediction",
        "query_result",
        "query_is_valid",
        "temperature",
        "max_output_tokens",
       # "top_k",
        "top_p",
        "last_run",
    ]

    # Annotate the queryset with the count of related file examples and select the columns.
    data = queryset.annotate(num_file_examples=Count("file_examples")).values_list(
        *columns, "num_file_examples"
    )

    # Create a Pandas DataFrame from the selected data, using the columns as column names.
    df = pd.DataFrame.from_records(data, columns=data._fields)

    # Convert the datetime columns to naive datetimes, to avoid Excel issues with timezones.
    date_columns = df.select_dtypes(include=["datetime64[ns, UTC]"]).columns
    for col in date_columns:
        df[col] = df[col].dt.tz_localize(None)

    # Use a Pandas ExcelWriter to write the DataFrame to the HTTP response.
    with pd.ExcelWriter(response) as writer:
        # Apply cell styles based on the value of query_is_valid.
        def style_query_is_valid(val):
            if val:
                return "background-color: #90EE90"
            else:
                return "background-color: #FFC0CB"

        styler = df.style.applymap(style_query_is_valid, subset=["query_is_valid"])
        styler.to_excel(
            writer, index=False, sheet_name="SQLQueries", freeze_panes=(1, 0)
        )
        worksheet = writer.sheets["SQLQueries"]
        # Get the dimensions of the dataframe.
        (max_row, max_col) = df.shape
        # Set the autofilter.
        worksheet.autofilter(0, 0, max_row, max_col - 1)
        worksheet.set_column(0, max_col - 1, width=20)

    # Return the HTTP response with the Excel file.
    return response


class ModelAdminMixin:
    """
    Adds a common method for running model from admin panel.
    """

    def response_change(self, request: HttpRequest, obj):
        if "_run-model" in request.POST:
            if isinstance(obj, GPT3_5):
                return _run_sql_pipeline(request=request, admin_model=self, obj=obj)
            elif isinstance(obj, GPT_4):
                return _run_sql_pipeline_GPT4(request=request, admin_model=self, obj=obj)     
        return super().response_change(request, obj)

    @admin.display(description="query", ordering="query")
    def get_query(self, obj) -> str:
        return truncatewords(obj.query, 20)

@admin.register(GPT3_5)
class GPT3_5Admin(ModelAdminMixin, admin.ModelAdmin):
    change_form_template = 'admin/change_form.html'
    list_display = (
        "id",
        "name",
        "get_query",
        "temperature",
       # "top_k",
        "top_p",
        "max_output_tokens",
        "last_run",
    )
    list_filter = ("last_run",)
    search_fields = ("name",)
    readonly_fields = ("final_prompt", "prediction", "last_run")
    # inlines = [FileAdmin, TextExampleAdmin]
    fieldsets = (
        ("BBDD", {"fields": ("name",)}),
        (
            "LLM parameters",
            {
                "fields": (
                    "query",
                    #"initial_statement",
                    #"separator",
                    "temperature",
                   #  "top_k",
                    "top_p",
                    "max_output_tokens",
                )
            },
        ),
        (
            "Prompt",
            {
                "fields": ("final_prompt",),
                "classes": ("collapse",),
            },
        ),
        (
            "Output",
            {
                "fields": ("prediction", "last_run"),
            },
        ),
    )


@admin.register(GPT_4)
class GPT_4Admin(ModelAdminMixin, admin.ModelAdmin):
    change_form_template = 'admin/sqltranslator/change_form.html'
    actions = [export_xls]
    list_display = (
        "id",
        "name",
        "get_query",
        "temperature",
        # "top_k",
        "top_p",
        "max_output_tokens",
        "last_run",
        "query_is_valid",
    )
    list_filter = ("last_run", "query_is_valid")
    search_fields = ("name",)
    readonly_fields = (
        "final_prompt",
        "prediction",
        "query_result",
        "query_is_valid",
        "last_run",
    )
    # inlines = [SQLFileAdmin]
    fieldsets = (
        ("BBDD", {"fields": ("name",)}),
        (
            "LLM parameters",
            {
                "fields": (
                    "query",
                    #"separator",
                    "temperature",
                    # "top_k",
                    "top_p",
                    "max_output_tokens",
                )
            },
        ),
        (
            "Prompt",
            {
                "fields": ("final_prompt",),
                "classes": ("collapse",),
            },
        ),
        (
            "Output",
            {
                "fields": ("prediction", "query_result", "query_is_valid", "last_run"),
            },
        ),
    )

