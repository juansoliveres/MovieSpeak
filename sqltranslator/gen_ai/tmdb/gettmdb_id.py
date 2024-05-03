import pandas as pd
from sqltranslator.gen_ai.mysql.postgresql_interactions import query_postgresql, get_postgresql_table_schema, execute_postgresql_command, send_df_to_postgresql

def get_tmdb_id(dataframe, username):
    """
    Retrieves The Movie Database (TMDB) IDs for a list of movie titles stored in a DataFrame.

    This function extracts movie titles from a given DataFrame and constructs a SQL query to 
    fetch corresponding TMDB IDs from a PostgreSQL database table associated with a specific user. 
    The titles are properly escaped to prevent SQL injection and formatted for inclusion in a SQL 
    "IN" clause. The function uses the `query_postgresql` function to execute the SQL query.

    Args
    ----
    - `dataframe` (DataFrame): A pandas DataFrame containing at least one column named 'title' with movie titles.
    - `username` (str): The username associated with the specific PostgreSQL table from which the TMDB IDs are fetched.

    Returns
    -------
    - List[int]: A list of TMDB IDs if the query is successful and the 'title' column exists in the dataframe;
      otherwise, an empty list.
    """
    if 'title' in dataframe.columns:
        titles = dataframe['title']
        titles = list(titles)
        escaped_titles = [title.replace("'", "''") for title in titles]
        formatted_titles = ', '.join(f"'{title}'" for title in escaped_titles)
        sql = f"SELECT tmdb_id FROM {username} WHERE title IN ({formatted_titles})"
        pandas_df, is_valid, sql_query = query_postgresql(sql)
        if is_valid:
            return pandas_df['tmdb_id'].tolist()
    else:
        return []

### Save the list in somewhere accessible by the JS file    