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
This is the original PostgresSQL query:
{{ sep }}
{{ original_sql }}
{{ sep }}
This is the error message obtained when running the original SQL query:
{{ sep }}
{{ error_msg }}
{{ sep }}
Rewrite the original SQL query to fix the error. OUTPUT JUST THE NEW SQL, IT MUST EXECUTABLE IN POSTGRESQL.
"""

SQL_RETRY = """\
This is the text: {{ text_query }}

This is the reference SQL: {{ reference_sql }}

The reference SQL could be right or wrong.

If the reference SQL is correct, output the reference SQL.
If the reference SQL is not correct, output the fixed SQL.
"""

BIGQUERY_SQL = """\
I have a table called {{ trakt_username }} in PostgreSQL. This is the schema of the table as condensed as JSON:
{{ schema }}
I will give you a question asked in a natural language, and you will traduce that question into EXECUTABLE POSTGRESQL CODE AND NOTHING ELSE, based on the schema of the table.
You need to take into account the following information:
- Columns genres and actors are of type array. When asked about who is the actor/genre which appears in most movies you need
to apply the UNNEST function to separate the items inside the array and compute its individual occurences, not as a group. 
- All genres are written in lowercase, so when asked about genres always use lowercase to write them.
============
question: {{ question }}
"""

