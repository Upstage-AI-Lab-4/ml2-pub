import streamlit as st
import pandas as pd
from streamlit_extras.row import row
import requests

st.set_page_config(
    layout='wide'
)

movie_data = pd.read_csv('../datasets/movie.csv')

resp = requests.get(f'http://127.0.0.1:8080/user/currentId/')
data = resp.json()
current_id = data['user_id']
st.caption(f'User ID: {current_id}')


####################
headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJiMmY1N2RmMjUzZjIyZTAwMTQ5MjRjYjdhYmI1MWIxOSIsIm5iZiI6MTcyODU0MjA3Ny44MjExMzYsInN1YiI6IjY3MDFmZTM4Zjg3OGFkZmVkMDg1ODRlMyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.zYZ0rkENIV78YzfmmcC71b49Svd5EXlokyHFF1sKCqI"
}
####################

#movie_list_resp = requests.get(f'http://127.0.0.1:8080/list/movie/recommend/')
#movie_list = movie_list_resp.json()['items']
#base_poster_path = 'https://image.tmdb.org/t/p/original'
#poster_path_arr = []
#image_none_path = '../resources/no_poster.png'
#
#for item in movie_list:
#    if len(movie_data.loc[movie_data['id']==int(item)]) > 0:
#        poster_path_data = movie_data.loc[movie_data['id']==int(item), 'poster_path']
#        poster_str = poster_path_data.values[0]
#        print(f"DEBUG_POSTERPATH:{poster_str}")
#        if type(poster_str) is not str:
#            poster_path_arr.append(image_none_path)
#        else:
#            poster_path_arr.append(base_poster_path + poster_str)
#    else:
#        poster_path_arr.append(image_none_path)
movie_list_resp_contentbased = requests.get(f'http://127.0.0.1:8080/list/movie/recommend/2')
movie_list_contentbased = movie_list_resp_contentbased.json()['items']


movie_list_resp = requests.get(f'http://127.0.0.1:8080/list/movie/recommend/1')
movie_list = movie_list_resp.json()['items']
base_poster_path = 'https://image.tmdb.org/t/p/original'
poster_path_arr = []
movie_name_arr = []
icon_path_arr = []
icon_link_arr = []
image_none_path = '../resources/no_poster.png'
ott_none_path = '../resources/no_ott.png'
icon_root_path = 'https://image.tmdb.org/t/p/w500'

for item in movie_list:
    print(item)
    if len(movie_data.loc[movie_data['id']==int(item)]) > 0:
        poster_path_data = movie_data.loc[movie_data['id']==int(item), 'poster_path']
        poster_str = poster_path_data.values[0]
        if type(poster_str) is not str:
            poster_path_arr.append(image_none_path)            
        else:
            poster_path_arr.append(base_poster_path + poster_str)
            
        movie_name_arr.append(movie_data.loc[movie_data['id']==int(item), 'title'])
        print(movie_data.loc[movie_data['id']==int(item), 'title'])

        url = f'https://api.themoviedb.org/3/movie/{int(item)}/watch/providers'
        response = requests.get(url, headers=headers)
        ott_data = response.json()

        if 'results' in ott_data and 'KR' in ott_data['results'] and 'flatrate' in ott_data['results']['KR']:
            otts = ott_data['results']['KR']['flatrate']
            links = []
            if len(otts)>0:
                for i in otts:
                    links.append(icon_root_path + i['logo_path'])
            icon_link_arr.append(links)
        else:
            icon_link_arr.append([ott_none_path])

    else:
        poster_path_arr.append(image_none_path)
        movie_name_arr.append(movie_data.loc[movie_data['id']==int(item), 'title'])
        print(movie_data.loc[movie_data['id']==int(item), 'title'])
        url = f'https://api.themoviedb.org/3/movie/{int(item)}/watch/providers'
        response = requests.get(url, headers=headers)   
        ott_data = response.json()
        if 'results' in ott_data and 'KR' in ott_data['results'] and 'flatrate' in ott_data['results']['KR']:
            otts = ott_data['results']['KR']['flatrate']
            links = []
            if len(otts)>0:
                for i in otts:
                    links.append(icon_root_path + i['logo_path'])
            icon_link_arr.append(links)
        else:
            icon_link_arr.append([ott_none_path])




movie_list_resp_cb = requests.get(f'http://127.0.0.1:8080/list/movie/recommend/2')
movie_list_cb = movie_list_resp_cb.json()['items']
print(f'dtttt{movie_list_cb}')
poster_path_arr_cb = []
movie_name_arr_cb = []
icon_path_arr_cb = []
icon_link_arr_cb = []

for item in movie_list_cb:
    print(f'item::::::{item}')
    if len(movie_data.loc[movie_data['id']==int(item)]) > 0:
        poster_path_data = movie_data.loc[movie_data['id']==int(item), 'poster_path']
        poster_str = poster_path_data.values[0]
        if type(poster_str) is not str:
            poster_path_arr_cb.append(image_none_path)            
        else:
            poster_path_arr_cb.append(base_poster_path + poster_str)
            
        movie_name_arr_cb.append(movie_data.loc[movie_data['id']==int(item), 'title'])
        print(movie_data.loc[movie_data['id']==int(item), 'title'])

        url = f'https://api.themoviedb.org/3/movie/{int(item)}/watch/providers'
        response = requests.get(url, headers=headers)
        ott_data = response.json()

        if 'results' in ott_data and 'KR' in ott_data['results'] and 'flatrate' in ott_data['results']['KR']:
            otts = ott_data['results']['KR']['flatrate']
            links = []
            if len(otts)>0:
                for i in otts:
                    links.append(icon_root_path + i['logo_path'])
            icon_link_arr_cb.append(links)
        else:
            icon_link_arr_cb.append([ott_none_path])

    else:
        poster_path_arr_cb.append(image_none_path)
        movie_name_arr_cb.append(movie_data.loc[movie_data['id']==int(item), 'title'])
        print(movie_data.loc[movie_data['id']==int(item), 'title'])
        url = f'https://api.themoviedb.org/3/movie/{int(item)}/watch/providers'
        response = requests.get(url, headers=headers)   
        ott_data = response.json()
        if 'results' in ott_data and 'KR' in ott_data['results'] and 'flatrate' in ott_data['results']['KR']:
            otts = ott_data['results']['KR']['flatrate']
            links = []
            if len(otts)>0:
                for i in otts:
                    links.append(icon_root_path + i['logo_path'])
            icon_link_arr_cb.append(links)
        else:
            icon_link_arr_cb.append([ott_none_path])






st.title("당신과 취향이 비슷한 사람들은 이런걸 좋아했어요")

row1 = row(10,vertical_align='center')
for i in range(0,10):
    row1.image(poster_path_arr[i],width=100)
row1_title = row(10,vertical_align='center')
for i in range(0,10):
    row1_title.write(movie_name_arr[i].values[0])
row1_ott = row(10,vertical_align='center')
for i in range(0,10):
    if len(icon_link_arr[i])>0:
        rows = row1_ott.columns(len(icon_link_arr[i]))
        for j in range(0,len(rows)):
            rows[j].image(icon_link_arr[i][j], width=30)
    else:
        row1_ott.image(ott_none_path,width=30)


#row1 = row(10,vertical_align='center')
#row1.image(poster_path_arr[0],width=100)
#row1.image(poster_path_arr[1],width=100)
#row1.image(poster_path_arr[2],width=100)
#row1.image(poster_path_arr[3],width=100)
#row1.image(poster_path_arr[4],width=100)
#row1.image(poster_path_arr[5],width=100)
#row1.image(poster_path_arr[6],width=100)
#row1.image(poster_path_arr[7],width=100)
#row1.image(poster_path_arr[8],width=100)
#row1.image(poster_path_arr[9],width=100)
#row2 = row(10,vertical_align='center')
#row2.radio('movie01', options=['👍', '❌', '👎'], horizontal = False, key='radio01', label_visibility='hidden')
#row2.radio('movie01', options=['👍', '❌', '👎'], horizontal = False, key='radio02', label_visibility='hidden')
#row2.radio('movie01', options=['👍', '❌', '👎'], horizontal = False, key='radio03', label_visibility='hidden')
#row2.radio('movie01', options=['👍', '❌', '👎'], horizontal = False, key='radio04', label_visibility='hidden')
#row2.radio('movie01', options=['👍', '❌', '👎'], horizontal = False, key='radio05', label_visibility='hidden')
#row2.radio('movie01', options=['👍', '❌', '👎'], horizontal = False, key='radio06', label_visibility='hidden')
#row2.radio('movie01', options=['👍', '❌', '👎'], horizontal = False, key='radio07', label_visibility='hidden')
#row2.radio('movie01', options=['👍', '❌', '👎'], horizontal = False, key='radio08', label_visibility='hidden')
#row2.radio('movie01', options=['👍', '❌', '👎'], horizontal = False, key='radio09', label_visibility='hidden')
#row2.radio('movie01', options=['👍', '❌', '👎'], horizontal = False, key='radio10', label_visibility='hidden')


st.title("당신이 좋아하는 영화와 스타일이 비슷한 영화는 이런게 있어요")
row2 = row(10,vertical_align='center')
for i in range(0,10):
    print(f'POSTER={poster_path_arr_cb[i]}')
    row2.image(poster_path_arr_cb[i],width=100)
row2_title = row(10,vertical_align='center')
for i in range(0,10):
    print(f'NAME={movie_name_arr_cb[i]}')

    row2_title.write(movie_name_arr_cb[i].values[0])
row2_ott = row(10,vertical_align='center')
for i in range(0,10):
    if len(icon_link_arr[i])>0:
        print(f'ICON={icon_link_arr_cb[i]}')
        rows = row2_ott.columns(len(icon_link_arr_cb[i]))
        for j in range(0,len(rows)):
            rows[j].image(icon_link_arr_cb[i][j], width=30)
    else:
        row2_ott.image(ott_none_path,width=30)


#row3.image(poster_path_arr[9],width=100)