import sqlalchemy as sa
import mysql.connector
from sqlalchemy import text
from sqlalchemy import create_engine as ce
from sqltranslator.gen_ai.config import POSTGRESQL_ENGINE_URL 
import pandas as pd
import json

import sqlalchemy as sa
import psycopg2

def send_df_to_postgresql(dataframe, trakt_username):
    """
    Converts DataFrame columns containing lists to strings and sends the DataFrame to a PostgreSQL database.

    This function iterates over each column in the provided DataFrame. If any column contains lists, 
    it converts these lists into comma-separated strings. It then creates a PostgreSQL engine using a predefined 
    connection URL and uploads the DataFrame to a PostgreSQL table named after the `trakt_username`.

    Args
    ----
    - `dataframe` (pd.DataFrame): The DataFrame to be sent to the PostgreSQL database.
    - `trakt_username` (str): The name of the table in the PostgreSQL database where the DataFrame will be stored.

    Returns
    -------
    - None: This function does not return anything.

    The function is particularly useful when dealing with DataFrames containing list-like elements, which 
    are not natively supported in SQL databases. It converts these elements to a SQL-compatible string format.
    Note that the connection URL to the PostgreSQL database must be defined in `POSTGRESQL_ENGINE_URL`.
    """
    # Convert list-like columns to string
    for col in dataframe.columns:
        if dataframe[col].apply(lambda x: isinstance(x, list)).any():
            dataframe[col] = dataframe[col].apply(lambda x: ','.join(map(str, x)))

    # Create the connection URL
    postgresql_engine = sa.create_engine(POSTGRESQL_ENGINE_URL)
    
    # Convert df to SQL and send it to MySQL
    dataframe.to_sql(trakt_username, postgresql_engine, if_exists='replace', index=False)

def query_postgresql(sqlquery):
    """
    Executes a SQL query on a PostgreSQL database and returns the results along with column names.
    
    This function connects to a PostgreSQL database using a predefined connection string. It executes the provided 
    SQL query and fetches all the resulting rows along with the column names. The connection is handled using 
    a context manager, ensuring that it is properly closed after the operation.
    
    Args
    ----
    - `sqlquery` (str): The SQL query to be executed.
    
    Returns
    -------
    - A tuple containing a pandas DataFrame with the query results and a boolean indicating success.
    """
    try:
        # Make sure to replace the connection string with your actual credentials
        postgresql_engine = sa.create_engine(POSTGRESQL_ENGINE_URL)
        with postgresql_engine.connect() as connection:
            # Ensure text() is used to prepare the SQL query
            result = connection.execute(text(sqlquery))
            columns = result.keys()  # Get column names
            rows = result.fetchall()  # Fetch all rows
            pandas_df = pd.DataFrame(rows, columns=columns)
            return pandas_df, True, sqlquery
    except Exception as e:
        print(f"An error occurred: {e}")
        return e, False, sqlquery


def get_postgresql_table_schema(table_name, schema='public'):
    """
    Retrieves the full schema of a table from a PostgreSQL database and formats it as a JSON string.

    Args
    ----
    - `table_name` (str): The name of the table.
    - `schema` (str): The schema of the table (default is 'public').

    Returns
    -------
    - `schema_json` (str): A JSON string representation of the table schema.
    """
    postgresql_engine = sa.create_engine(POSTGRESQL_ENGINE_URL)
    query = f"""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = '{schema}' AND table_name = '{table_name}';
    """
    try:
        with postgresql_engine.connect() as connection:
            result = connection.execute(text(query))
            # Using row._mapping to access columns by name in a dictionary-like fashion.
            columns = [{"name": row._mapping['column_name'], "type": row._mapping['data_type']} for row in result]
            schema_dict = {"table": table_name, "columns": columns}
            schema_json = json.dumps(schema_dict, indent=2)
            return schema_json
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""

def execute_postgresql_command(sqlquery):
    """
    Executes a SQL command (such as DDL statements) on a PostgreSQL database without expecting a result set.
    
    This function connects to a PostgreSQL database using a predefined connection string. It executes the provided 
    SQL command. The connection is handled using a context manager, ensuring that it is properly closed after the operation.
    
    Args
    ----
    - `sqlquery` (str): The SQL command to be executed.
    
    Returns
    -------
    - A boolean indicating success.
    """
    try:
        # Make sure to replace the connection string with your actual credentials
        postgresql_engine = sa.create_engine(POSTGRESQL_ENGINE_URL, echo=True)
        with postgresql_engine.begin() as connection:  # This ensures the transaction is automatically committed
            connection.execute(text(sqlquery))
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
