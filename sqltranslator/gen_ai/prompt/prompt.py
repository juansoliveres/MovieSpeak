import io
from functools import cached_property
from typing import Any, Dict, List, Literal, Optional, Union
from jinja2 import Template
from sqltranslator.gen_ai.config import DEFAULT_EXAMPLES_SEPARATOR
from sqltranslator.gen_ai.prompt.templates import BIGQUERY_SQL

def prompt_sql_generator(
    question: str,
    text_examples: str,
    trakt_username: str, 
    #file_examples: Union[Dict[str, str], List[Dict[str, str]], None] = None,
    input_sep: str = DEFAULT_EXAMPLES_SEPARATOR,
    # context_type: Union[Literal["examples"], Literal["schema"]] = "examples",
) -> str:
    """
    Generate an SQL prompt with placeholders for data examples and file data,
    using a Jinja template.

    Args
    ----
    - `question` (str): The natural language question to ask for.
    - `data_examples` (Union[TableExample, List[TableExample], None], optional):
        A single or list of `TableExample` instances that represent examples of
        the data that the SQL query will be executed on. Default is None.
    - `file_examples` (Union[Dict[str, str], List[Dict[str, str]], None], optional):
        A single or list of dictionaries containing the name and path of the files
        that will be used as input data for the SQL query. Default is None.
    - `input_sep` (str, optional):
        The separator string to use when displaying the data examples in the SQL prompt.
        Default is '###'.
    - `context_type` (str)
        It can be either "examples" or "schema". If "examples" is selected,
        then the prompt will include a few records from the tables. If "schema" is selected,
        then the prompt will just include the definition of the schema together with some
        values for the categorical fields. Default is "examples".

    Returns
    -------
    - str: A string representing the generated SQL prompt.

    Raises
    ------
    - AssertionError: If the input arguments are not in the expected format.

    The function generates an SQL prompt by rendering a Jinja template with the input SQL query and data examples.
    It first checks that the input arguments are in the expected format.
    The `data_examples` argument should be a list or tuple of `TableExample` instances,
    while the `file_examples` argument should be a list of dictionaries containing the
    name and path of the files to be used as input data.

    The resulting SQL prompt is returned as a string.
    """
    template: Template = Template(source=BIGQUERY_SQL)
    context = {
        "question": question,
        "schema": text_examples,
        "trakt_username": trakt_username,
        }
    result = template.render(context)
    return result


def prompt_sql_fixer(
    original_sql: str, error_msg: str, input_sep: str = DEFAULT_EXAMPLES_SEPARATOR
) -> str:
    """
    Generates a formatted prompt for fixing SQL query errors based on the original
    SQL and the corresponding error message.

    Args
    ----
    - `original_sql` (str): The original SQL query that produced the error.
    - `error_msg` (str): The error message obtained when running the original SQL query.
    - `input_sep` (str, optional): The separator string used to separate sections
    in the output prompt. Defaults to DEFAULT_EXAMPLES_SEPARATOR.

    Returns
    -------
    - `str`: A formatted prompt string that includes the original SQL query, the error message, and a request to rewrite the original SQL query to fix the error.

    Note
    ----
    - The function uses a template string to generate the prompt.
    - The `input_sep` argument allows customizing the separator string used between sections.
    """
    template: Template = Template(SQL_WITH_ERROR_FIX)
    context = {
        "original_sql": original_sql,
        "error_msg": error_msg,
        "sep": input_sep,
    }
    result = template.render(context)
    return result


def prompt_sql_refine(text_query: str, reference_sql: str) -> str:
    """
    Process a text query and a reference SQL statement to build
    a prompt to refine the SQL statement.

    Args
    ----
    - `text_query` (str): The text query provided by the user.
    - `reference_sql` (str): The reference SQL statement that needs to be refined.

    Returns
    -------
    - `str`: The prompt to ask for a refined SQL statement.

    Note
    ----
    This function uses a template called SQL_RETRY, which contains placeholders for the text query
    and reference SQL. Ensure that the template is defined correctly and contains the necessary
    placeholders for the function to work as intended.
    """
    template: Template = Template(SQL_RETRY)
    context = {
        "text_query": text_query,
        "reference_sql": reference_sql,
    }
    result = template.render(context)
    return result
