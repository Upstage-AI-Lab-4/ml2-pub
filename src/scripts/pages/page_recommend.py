import streamlit as st
import pandas as pd
import api
from streamlit_image_select import image_select
import numpy as np
from PIL import Image
from streamlit_extras.row import row
import requests

st.set_page_config(
    layout='wide'
)

movie_data = pd.read_csv('../datasets/movies_metadata.csv', low_memory=False)
icon_thumb_up = '../resources/icons/thumb_up.png'
icon_thumb_down = '../resources/icons/thumb_down.png'


resp = requests.get(f'http://127.0.0.1:8080/user/currentId/')
data = resp.json()
current_id = data['user_id']
st.caption(f'User ID: {current_id}')


movie_list_resp = requests.get(f'http://127.0.0.1:8080/list/movie/recommend/')
movie_list = movie_list_resp.json()['items']
base_poster_path = 'https://image.tmdb.org/t/p/original'
poster_path_arr = []

for item in movie_list:
    str = movie_data.loc[int(item)]['poster_path']
    poster_path_arr.append(base_poster_path + str)
    print(movie_data.loc[int(item)]['title'])
    print(base_poster_path + str)

st.title("당신과 취향이 비슷한 사람들은 이런걸 좋아했어요")
poster_path = 'https://image.tmdb.org/t/p/original' + movie_data.loc[1]['poster_path']
row1 = row(10,vertical_align='center')
row1.image(poster_path_arr[0],width=100)
row1.image(poster_path_arr[1],width=100)
row1.image(poster_path_arr[2],width=100)
row1.image(poster_path_arr[3],width=100)
row1.image(poster_path_arr[4],width=100)
row1.image(poster_path_arr[5],width=100)
row1.image(poster_path_arr[6],width=100)
row1.image(poster_path_arr[7],width=100)
row1.image(poster_path_arr[8],width=100)
row1.image(poster_path_arr[9],width=100)
row2 = row(10,vertical_align='center')
row2.radio('movie01', options=['👍', '❌', '👎'], horizontal = False, key='radio01', label_visibility='hidden')
row2.radio('movie01', options=['👍', '❌', '👎'], horizontal = False, key='radio02', label_visibility='hidden')
row2.radio('movie01', options=['👍', '❌', '👎'], horizontal = False, key='radio03', label_visibility='hidden')
row2.radio('movie01', options=['👍', '❌', '👎'], horizontal = False, key='radio04', label_visibility='hidden')
row2.radio('movie01', options=['👍', '❌', '👎'], horizontal = False, key='radio05', label_visibility='hidden')
row2.radio('movie01', options=['👍', '❌', '👎'], horizontal = False, key='radio06', label_visibility='hidden')
row2.radio('movie01', options=['👍', '❌', '👎'], horizontal = False, key='radio07', label_visibility='hidden')
row2.radio('movie01', options=['👍', '❌', '👎'], horizontal = False, key='radio08', label_visibility='hidden')
row2.radio('movie01', options=['👍', '❌', '👎'], horizontal = False, key='radio09', label_visibility='hidden')
row2.radio('movie01', options=['👍', '❌', '👎'], horizontal = False, key='radio10', label_visibility='hidden')

c1 = st.container(height=200,border=True)
c1_arr = c1.columns(20)
c1_arr[0].image(poster_path,width=100)
c1_arr[1].write(' ')
c1_arr[2].image(poster_path,width=100)
c1_arr[3].write(' ')
c1_arr[4].image(poster_path,width=100)
c1_arr[5].write(' ')
c1_arr[6].image(poster_path,width=100)
c1_arr[7].write(' ')
c1_arr[8].image(poster_path,width=100)
c1_arr[9].write(' ')
c1_arr[10].image(poster_path,width=100)
c1_arr[11].write(' ')
c1_arr[12].image(poster_path,width=100)
c1_arr[13].write(' ')
c1_arr[14].image(poster_path,width=100)
c1_arr[15].write(' ')
c1_arr[16].image(poster_path,width=100)
c1_arr[17].write(' ')
c1_arr[18].image(poster_path,width=100)
c1_arr[19].write(' ')

c1__container = st.container(height=30)
c1__arr = c1__container.columns(20)

st.title("당신이 좋아하는 감독과 스타일이 비슷한 영화는 이런게 있어요")
poster_path = 'https://image.tmdb.org/t/p/original' + movie_data.loc[5]['poster_path']
c2 = st.container(height=200,border=True)
c2_arr = c2.columns(10)

c2_arr[0].image(poster_path,width=100)
c2_arr[1].image(poster_path,width=100)
c2_arr[2].image(poster_path,width=100)
c2_arr[3].image(poster_path,width=100)
c2_arr[4].image(poster_path,width=100)
c2_arr[5].image(poster_path,width=100)
c2_arr[6].image(poster_path,width=100)
c2_arr[7].image(poster_path,width=100)
c2_arr[8].image(poster_path,width=100)
c2_arr[9].image(poster_path,width=100)