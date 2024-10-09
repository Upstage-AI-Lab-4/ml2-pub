import streamlit as st
import pandas as pd
import api
from streamlit_extras.row import row
import requests

st.set_page_config(
    layout='wide'
)
movie_data = pd.read_csv('../datasets/movies_metadata.csv')
icon_thumb_up = '../resources/icons/thumb_up.png'
icon_thumb_down = '../resources/icons/thumb_down.png'

resp = requests.get(f'http://127.0.0.1:8080/user/currentId/')
data = resp.json()
current_id = data['user_id']
#st.sidebar.write(f"Welcome! {current_id}")
st.caption(f'User ID: {current_id}')
st.title("당신이 재밌게 본 영화는?")


movie_list_resp = requests.get(f'http://127.0.0.1:8080/list/movie/firstlist/')
movie_list = movie_list_resp.json()['movie_list']
base_poster_path = 'https://image.tmdb.org/t/p/original'
poster_path_arr = []

for item in movie_list:
    str = movie_data.loc[int(item)]['poster_path']
    poster_path_arr.append(base_poster_path + str)
    print(movie_data.loc[int(item)]['title'])
    print(base_poster_path + str)

ratings = ['4','2','2','2','5','3','4','1','2','2']

rad = []

row1 = row(5,vertical_align='center')
row1.image(poster_path_arr[0],width=180)
row1.image(poster_path_arr[1],width=180)
row1.image(poster_path_arr[2],width=180)
row1.image(poster_path_arr[3],width=180)
row1.image(poster_path_arr[4],width=180)
row2 = row(5,vertical_align='center')
rad.append(row2.radio('movie01', options=['👍', '❌', '👎'], horizontal = True, key='radio01', label_visibility='hidden'))
rad.append(row2.radio('movie01', options=['👍', '❌', '👎'], horizontal = True, key='radio02', label_visibility='hidden'))
rad.append(row2.radio('movie01', options=['👍', '❌', '👎'], horizontal = True, key='radio03', label_visibility='hidden'))
rad.append(row2.radio('movie01', options=['👍', '❌', '👎'], horizontal = True, key='radio04', label_visibility='hidden'))
rad.append(row2.radio('movie01', options=['👍', '❌', '👎'], horizontal = True, key='radio05', label_visibility='hidden'))

row3 = row(5,vertical_align='center')
row3.image(poster_path_arr[5],width=180)
row3.image(poster_path_arr[6],width=180)
row3.image(poster_path_arr[7],width=180)
row3.image(poster_path_arr[8],width=180)
row3.image(poster_path_arr[9],width=180)
row4 = row(5,vertical_align='center')
rad.append(row4.radio('movie01', options=['👍', '❌', '👎'], horizontal = True, key='radio11', label_visibility='hidden'))
rad.append(row4.radio('movie01', options=['👍', '❌', '👎'], horizontal = True, key='radio12', label_visibility='hidden'))
rad.append(row4.radio('movie01', options=['👍', '❌', '👎'], horizontal = True, key='radio13', label_visibility='hidden'))
rad.append(row4.radio('movie01', options=['👍', '❌', '👎'], horizontal = True, key='radio14', label_visibility='hidden'))
rad.append(row4.radio('movie01', options=['👍', '❌', '👎'], horizontal = True, key='radio15', label_visibility='hidden'))



if st.button("SUBMIT"):
    rating_data = []
    for radio_item in rad:
        if radio_item == '👍':
            rating_data.append('4.5')
        elif radio_item == '❌':
            rating_data.append('0')
        elif radio_item == '👎':
            rating_data.append('0.5')
        else:
            rating_data.append('0')

    url='http://127.0.0.1:8080/set_first_rate/'
    data = {
        "movies": movie_list,
        "ratings":rating_data
    }
    resp = requests.post(url, json=data)
    st.switch_page('pages/page_recommend.py')
