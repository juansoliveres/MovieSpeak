import requests
from django.http import HttpRequest, HttpResponseRedirect
import pandas as pd
from sqltranslator.gen_ai.config import HEADERS
import asyncio
import aiohttp
import certifi
import ssl

def retrieve_trakt_history(trakt_user_name):
    response = requests.get(f"https://api.trakt.tv/users/{trakt_user_name}/ratings/movies", headers = HEADERS)
    data = response.json()
    
    titles, imdb_id, user_rating = ([] for _ in range(3))  
    for movie in data:
        titles.append(movie['movie']['title'])
        imdb_id.append(movie['movie']['ids']['imdb'])
        user_rating.append(movie['rating'])

    data_tuples = list(zip(titles,imdb_id,user_rating))
    title_imdbid = pd.DataFrame(data_tuples, columns=['Title','IMDB_id','User_rating'])
    title_imdbid = title_imdbid.dropna()
    return title_imdbid

async def fetch_movie_details(session, movieid):
    url = f"https://api.trakt.tv/movies/{movieid}?extended=full"
    async with session.get(url, headers=HEADERS) as response:
        return await response.json()

async def fetch_movie_people(session, movieid):
    url = f"https://api.trakt.tv/movies/{movieid}/people"  # Hypothetical endpoint
    async with session.get(url, headers=HEADERS) as response:
        return await response.json()

async def main(title_imdbid):
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    # Use the SSLContext with the TCPConnector
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(connector=connector) as session:
    # async with aiohttp.ClientSession() as session:
        details_tasks = [fetch_movie_details(session, movieid) for movieid in title_imdbid['IMDB_id']]
        people_tasks = [fetch_movie_people(session, movieid) for movieid in title_imdbid['IMDB_id']]
        
        # print(details_tasks)
        # print(people_tasks)

        # Wait for all tasks to complete
        details_results = await asyncio.gather(*details_tasks)
        people_results = await asyncio.gather(*people_tasks)

        #print(details_results)    
        #print(people_results)

        year, runtime, country, rating, votes, language, genres, certification, directors, actors =  ([] for _ in range(10)) 

        for movie_details in details_results:
            year.append(movie_details.get('year'))
            runtime.append(movie_details.get('runtime'))
            country.append(movie_details.get('country'))
            rating.append(movie_details.get('rating'))
            votes.append(movie_details.get('votes'))
            language.append(movie_details.get('language'))
            genres.append(movie_details.get('genres', []))  # Default to empty list if genres is missing
            certification.append(movie_details.get('certification'))
        
        # Assigning lists to the dictionary
        title_imdbid['year'] = year
        title_imdbid['runtime'] = runtime
        title_imdbid['country'] = country
        title_imdbid['rating'] = rating
        title_imdbid['votes'] = votes
        title_imdbid['language'] = language
        title_imdbid['genres'] = genres
        title_imdbid['certification'] = certification
        # Extend this pattern to include details and stats as needed
        

        for people in people_results:
            actors_list = []         
            for actor in people['cast'][0:5]:
                actors_list.append(actor['person']['name'])
            actors.append(actors_list)            
            
            directors_list = [] 
            for movie in people['crew']['directing']:
                if movie['job'] == 'Director':
                    directors_list.append(movie['person']['name'])
            directors.append(directors_list)

        #print(actors)
        #print(directors)
        title_imdbid['actors'] = actors
        title_imdbid['director'] = directors
        
        return title_imdbid
        
  
        
