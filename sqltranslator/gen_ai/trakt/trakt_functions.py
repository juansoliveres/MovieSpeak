import requests
import pandas as pd
from sqltranslator.gen_ai.config import HEADERS


def read_trakt_history(user_name):
    """
    Fetches a user's movie history from the Trakt API.

    This function iterates through the pages of a user's movie history on Trakt and accumulates all the 
    movies into a list. Each page's data is requested from the Trakt API, and the function continues to 
    request data until there are no more items to fetch.

    Args
    ----
    - `user_name` (str): The Trakt username whose movie history is to be fetched.

    Returns
    -------
    - `trakt_history` (list): A list of dictionaries, each representing a movie from the user's history.

    The function utilizes the Trakt API to fetch the user's movie history. Each item in the returned list 
    contains detailed information about a single movie.
    """
    trakt_history = []
    page = 1
    has_more_items = True
    while has_more_items:
        url = f"https://api.trakt.tv/users/{user_name}/history/movies?page={page}"
        response = requests.get(url, headers=HEADERS)
        data = response.json()
        trakt_history.extend(data)
        page += 1
        has_more_items = len(data) > 0
    return trakt_history

def select_title_and_id(trakt_history):
    """
    Extracts titles and IMDb IDs from a Trakt history list.

    This function processes a list of movie data (as obtained from the Trakt API) and extracts the title 
    and IMDb ID of each movie. It then constructs a DataFrame containing these details.

    Args
    ----
    - `trakt_history` (list): A list of dictionaries where each dictionary contains details of a movie.

    Returns
    -------
    - `title_imdbid` (pd.DataFrame): A DataFrame with columns 'Title' and 'IMDB_id', containing the 
      title and IMDb ID of each movie, respectively.

    This function is useful for further processing or analysis of a user's movie history, particularly when 
    needing to reference or lookup additional information using IMDb IDs.
    """
    titles, imdb_id = ([] for _ in range(2)) 
    for movie in trakt_history:
        titles.append(movie['movie']['title'])
        imdb_id.append(movie['movie']['ids']['imdb'])
    data_tuples = list(zip(titles,imdb_id))
    title_imdbid = pd.DataFrame(data_tuples, columns=['Title','IMDB_id'])
    return title_imdbid

def add_movie_details1(title_imdbid):
    """
    Enhances a DataFrame of movie titles and IMDb IDs with additional details.

    This function iterates over the 'IMDB_id' column of the provided DataFrame and fetches additional 
    details for each movie from the Trakt API. The additional details include year, runtime, country, 
    rating, votes, language, genres, and certification. The function constructs a new DataFrame with these 
    details and concatenates it with the input DataFrame.

    Args
    ----
    - `title_imdbid` (pd.DataFrame): A DataFrame with columns 'Title' and 'IMDB_id'.

    Returns
    -------
    - `final_df` (pd.DataFrame): A DataFrame that contains the original data along with the additional 
      movie details.

    This function is useful for creating a comprehensive dataset of movies, combining basic identifiers 
    with richer metadata for each movie. It handles HTTP request errors gracefully by printing error messages 
    and skipping over movies for which details cannot be retrieved.
    """
    movie_data = []
    for movieid in title_imdbid['IMDB_id']:
        try:
            # Getting movie details for each movie in users watchlist 
            url = f"https://api.trakt.tv/movies/{movieid}?extended=full"
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code

            movie_details = response.json()

            # Append movie details to the list
            movie_data.append({
                'year': movie_details.get('year'),
                'runtime': movie_details.get('runtime'),
                'country': movie_details.get('country'),
                'rating': movie_details.get('rating'),
                'votes': movie_details.get('votes'),
                'language': movie_details.get('language'),
                'genres': movie_details.get('genres'),
                'certification': movie_details.get('certification')
            })
            # print(movie_data)

        except requests.RequestException as e:
            print(f"Request error for movie ID {movieid}: {e}")

    movie_df = pd.DataFrame(movie_data)
    final_df = pd.concat([title_imdbid,movie_df],axis = 1)
    print(final_df.head())
    return final_df