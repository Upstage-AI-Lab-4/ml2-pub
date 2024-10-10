import streamlit as st
import pandas as pd
from streamlit_extras.row import row
import requests

st.set_page_config(
    layout='wide'
)
movie_data = pd.read_csv('../datasets/movie.csv')
#movie_data = pd.read_csv('../datasets/movies_metadata.csv')
#icon_thumb_up = '../resources/icons/thumb_up.png'
#icon_thumb_down = '../resources/icons/thumb_down.png'



####################
headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJiMmY1N2RmMjUzZjIyZTAwMTQ5MjRjYjdhYmI1MWIxOSIsIm5iZiI6MTcyODU0MjA3Ny44MjExMzYsInN1YiI6IjY3MDFmZTM4Zjg3OGFkZmVkMDg1ODRlMyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.zYZ0rkENIV78YzfmmcC71b49Svd5EXlokyHFF1sKCqI"
}
####################




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
movie_name_arr = []
image_none_path = '../resources/no_poster.png'

for item in movie_list:
    if len(movie_data.loc[movie_data['id']==int(item)]) > 0:
        poster_path_data = movie_data.loc[movie_data['id']==int(item), 'poster_path']
        poster_str = poster_path_data.values[0]
        if type(poster_str) is not str:
            poster_path_arr.append(image_none_path)
            movie_name_arr.append(movie_data.loc[movie_data['id']==int(item), 'title'])
            
        else:
            poster_path_arr.append(base_poster_path + poster_str)
            movie_name_arr.append(movie_data.loc[movie_data['id']==int(item), 'title'])

    else:
        poster_path_arr.append(image_none_path)
        movie_name_arr.append(movie_data.loc[movie_data['id']==int(item), 'title'])





#if 'selected_option' not in st.session_state:
#    st.session_state.selected_option = '❌'
#
#selected_option = st.radio("Choose an option:", ['👍', '❌', '👎'], index=['👍', '❌', '👎'].index(st.session_state.selected_option))
#st.session_state.selected_option = selected_option

rad = []
row1 = row(5,vertical_align='center')
for i in range(0,5):
    row1.image(poster_path_arr[i],width=180)
row1_title = row(5,vertical_align='center')
for i in range(0,5):
    row1_title.write(movie_name_arr[i].values[0])


row1_rate = row(5,vertical_align='center')
for i in range(0,5):
    rad.append(row1_rate.radio('movie01', options=['👍', '❌', '👎'], horizontal = True, key='radio'+str(i), label_visibility='hidden'))



row2 = row(5,vertical_align='center')
for i in range(5,10):
    row2.image(poster_path_arr[i],width=180)
row2_title = row(5,vertical_align='center')
for i in range(5,10):
    row2_title.write(movie_name_arr[i].values[0])


row2_rate = row(5,vertical_align='center')
for i in range(5,10):
    rad.append(row2_rate.radio('movie01', options=['👍', '❌', '👎'], horizontal = True, key='radio'+str(i), label_visibility='hidden'))




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
