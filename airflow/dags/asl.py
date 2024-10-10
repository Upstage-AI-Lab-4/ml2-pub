from datetime import datetime

import requests
import pandas as pd
import numpy as np
import tag

from sklearn.metrics.pairwise import cosine_similarity 
from implicit.als import AlternatingLeastSquares
from scipy.sparse import csr_matrix

def handler(movie_dt, rating_dt):
    user_item_matrix = csr_matrix((rating_dt['rating'], (rating_dt['userId'], rating_dt['movieId'])))

    print('create ALS model')
    model = AlternatingLeastSquares(factors=10, regularization=0.1, iterations=20)
    model.fit(user_item_matrix)
    
    return tag.ALSWrapper(model)
