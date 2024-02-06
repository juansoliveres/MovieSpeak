import sqlalchemy as sa
import mysql.connector
from sqlalchemy import text
from sqlalchemy import create_engine as ce
from sqltranslator.gen_ai.config import MYSQL_ENGINE_URL 
import pandas as pd


def send_df_to_mysql(dataframe, trakt_username):
    """
    Converts DataFrame columns containing lists to strings and sends the DataFrame to a MySQL database.

    This function iterates over each column in the provided DataFrame. If any column contains lists, 
    it converts these lists into comma-separated strings. It then creates a MySQL engine using a predefined 
    connection URL and uploads the DataFrame to a MySQL table named after the `trakt_username`.

    Args
    ----
    - `dataframe` (pd.DataFrame): The DataFrame to be sent to the MySQL database.
    - `trakt_username` (str): The name of the table in the MySQL database where the DataFrame will be stored.

    Returns
    -------
    - None: This function does not return anything.

    The function is particularly useful when dealing with DataFrames containing list-like elements, which 
    are not natively supported in SQL databases. It converts these elements to a SQL-compatible string format.
    Note that the connection URL to the MySQL database must be defined in `MYSQL_ENGINE_URL`.
    """
    # Convert list-like columns to string
    for col in dataframe.columns:
        if dataframe[col].apply(lambda x: isinstance(x, list)).any():
            dataframe[col] = dataframe[col].apply(lambda x: ','.join(map(str, x)))
    # Create the connection URL
    mysql_engine = sa.create_engine(MYSQL_ENGINE_URL)
    # Convert df to SQL and send it to MySQL
    dataframe.to_sql(trakt_username, mysql_engine, if_exists='replace', index=False)

def query_mysql(sqlquery):
    """
    Executes a SQL query on a MySQL database and returns the results as a pandas DataFrame along with 
    a boolean indicating the success of the execution and the executed SQL query itself.

    This function connects to a MySQL database using a predefined MySQL engine. It attempts to execute 
    the provided SQL query and fetches all the resulting rows, converting them into a pandas DataFrame. 
    The DataFrame includes both the data rows and column names. The connection is handled using a context 
    manager, ensuring that it is properly closed after the operation. The function includes error handling 
    to set the `is_valid` flag appropriately based on the success of the query execution.

    Args
    ----
    - `sqlquery` (str): The SQL query to be executed.

    Returns
    -------
    - `pandas_df` (pandas.DataFrame): A DataFrame containing the result set of the executed SQL query, 
      if the query was successful. Otherwise, an empty DataFrame.
    - `is_valid` (bool): A boolean value indicating whether the SQL query was executed successfully.
    - `executed_query` (str): The SQL query that was executed.

    Example
    -------
    query = "SELECT * FROM your_table"
    df, is_valid, executed_query = query_mysql(query)
    if is_valid:
        print(df)
    else:
        print("Query execution failed")
    """
    try:
        mysql_engine = sa.create_engine(MYSQL_ENGINE_URL)
        with mysql_engine.connect() as connection:
            result = connection.execute(text(sqlquery))
            columns = result.keys()  # Get column names
            rows = result.fetchall()  # Fetch all rows
            pandas_df = pd.DataFrame(rows, columns=columns)
            return pandas_df, True, sqlquery
    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame(), False, sqlquery

def get_full_table_schema(sqlquery):
    """
    Retrieves the full schema of a table from a MySQL database.

    This function connects to a MySQL database using a predefined MySQL engine. It executes the provided SQL query, usually a 'SHOW CREATE TABLE' statement, to fetch the schema of a specified table. The results are returned as rows and concatenated into a single string to represent the complete schema of the table.

    Args
    ----
    - `sqlquery` (str): The SQL query to retrieve the table schema.

    Returns
    -------
    - `schema_str` (str): A string representation of the table schema, formatted for readability.

    The function is designed for read-only queries and assumes the availability of a MySQL connection engine (`mysql_engine`).
    """
    mysql_engine = sa.create_engine(MYSQL_ENGINE_URL)
    try: 
        with mysql_engine.connect() as connection:
            result = connection.execute(text(sqlquery))
            rows = result.fetchall()  # Fetch all rows
            schema_str = ""
            for row in rows:
                for col in row:
                    schema_str += str(col) + "\n"  # Append each column to a string
                    print(schema_str)
    except Exception as e:
        print(f"An error occurred: {e}")
    return schema_str