TEXT_GENERAL = """\
{% if initial_statement %}\
{{ initial_statement }}
{% endif %}\
{% if examples %}\
{{ sep }}\
{% for example in examples %}
{{ example }}
{% if not loop.last %}{{ sep }}{% endif %}\
{% endfor %}\
{{ sep }}
{% endif %}\
{{ query }}\
"""

SQL = """\
{% if examples|length > 1 %}\
This are several tables:
{{ sep }}\
{% for example in examples %}
Table {{ loop.index }}.
Table's name: {{ example.name }}.
Table's columns: `{{ example['fields']|join('`, `') }}`.
Table's data: {{ example.example }}
{% if not loop.last %}{{ sep }}{% endif %}\
{% endfor %}\
{% else %}\
This is a table called `{{ examples[0].name }}`:
{{ sep }}
{{ examples[0].example }}
{{ sep }}
The columns of the table are: `{{ examples[0]['fields']|join('`, `') }}`.
{% endif %}\
{{ sep }}
This is the text: {{ query }}
{{ sep }}
Translate the text to SQL query based on the table and columns. Print just the SQL.
"""

SQL_WITH_ERROR_FIX = """\
This is the original SQL query:
{{ sep }}
{{ original_sql }}
{{ sep }}
This is the error message obtained when running the original SQL query:
{{ sep }}
{{ error_msg }}
{{ sep }}
Rewrite the original SQL query to fix the error. Output just the new SQL.
"""

SQL_RETRY = """\
This is the text: {{ text_query }}

This is the reference SQL: {{ reference_sql }}

The reference SQL could be right or wrong.

If the reference SQL is correct, output the reference SQL.
If the reference SQL is not correct, output the fixed SQL.
"""

BIGQUERY_SQL = """\
I have a table called 'movies2' in MySQL. This is the schema of the table as described by MySQL:
{{ schema }}
I will give you a question asked in a natural language, and you will traduce that question into a MySQL code and nothing else, based on the schema of the table.
============
question: {{ question }}
"""

BIGQUERY_SQL_BASE = """\
{% if examples|length == 1 %}\
{% set table_name = examples[0].name %}\
{% set table_schema_dict = examples[0].schema %}\
I have a table called `{{ table_name }}` in BigQuery. This is the schema of the table condensed as JSON:
{{ table_schema_dict }}
I will give you a question asked in a natural language, and you will traduce that question into a BigQuery SQL code and nothing else, based on the schema of the table.
{% elif examples|length > 1 %}\
{% set table_name = examples[0].name %}\
I have several tables stored in BigQuery. I am going to pass you below, for each table, its name and schema, condensed as JSON:
{% for example in examples %}\
Table name: `{{ example.name }}`
Table schema: {{ example.schema }}
{% endfor %}\
I will give you a question asked in a natural language, and you will traduce that question into a BigQuery SQL code and nothing else, based on the name and schema of the tables.
{% else %}\
{{ error() }}
{% endif %}\
You have to take into account the following caveats:
- The conversion rate is defined as the ratio of the sum of gross policies to the sum of completed quotes, multiplied by 100 to return a percentage.
Examples: question: show me the first 5 registries of {{ table_name }}.
answer: SELECT * FROM `{{ table_name }}` LIMIT 5;
question: what is the conversion rate registered on February?
answer: SELECT SUM({{ translation_names.NUM_POL_BRUTAS_NB }}) / SUM({{ translation_names.NUM_COT_COMP_NB }}) * 100 AS conversion_rate FROM `pruebasverti01.cotizaciones_polizas` WHERE EXTRACT(MONTH FROM {{ translation_names.FEC_DATA }}) = 2;
question: Out of all annulments, what percentage of them have been made with validity?
answer: SELECT SUM(CASE WHEN {{ translation_names.TIPOANUL }} = '{{ translation_values.ANULCONV }}' THEN {{ translation_names.NUM_MOVIMIENTOS }} ELSE 0 END) / SUM(CASE WHEN {{ translation_names.TIPOANUL }} IS NOT NULL THEN {{ translation_names.NUM_MOVIMIENTOS }} ELSE 0 END ) * 100 AS percentage_of_annulments_with_validity FROM `pruebasverti01.movimientos`;
============
question: {{ question }}
"""