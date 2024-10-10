import pandas as pd
import get_latest_file

def handler():
    base_path = './datasets'
    movie_path = get_latest_file.handler(base_path, 'movies_metadata')
    rating_path = get_latest_file.handler(base_path, 'ratings_small')

    print(f'load movie data: {movie_path}')
    movie_dt = pd.read_csv(movie_path)
    print(f'load rating data: {rating_path}')
    rating_dt = pd.read_csv(rating_path)

    return (movie_dt, rating_dt)


