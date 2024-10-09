import streamlit as st
import requests
import json

st.set_page_config(
    page_title="Movie Recommend Service",
    layout='wide'
)

current_id = ''

id_label = st.text_input(label='ID를 입력해주세요')


if st.button("JOIN"):
    resp = requests.get(f'http://127.0.0.1:8080/user/exist/{id_label}')
    data = resp.json()
    print(data['exist'])
    if data['exist'] == True:
        current_id = int(id_label)
        print(current_id)
        resp = requests.post(f'http://127.0.0.1:8080/user/login/{id_label}')
        st.switch_page('pages/page_recommend.py')
    print('?')

if st.button("REGISTER"):
    resp = requests.post(f'http://127.0.0.1:8080/user/create/')
    reg_data = resp.json()
    current_id = int(reg_data['user_id'])
    st.switch_page('pages/page_first.py',)