![image](https://github.com/user-attachments/assets/cea52ff7-99bc-46c4-9ea1-844b795a3e1f)# 영화 추천 Service (Movie Recommend Service)
## Team

| <img src="https://avatars.githubusercontent.com/u/97029997?v=4" width="160" height="160"/> | <img src="https://avatars.githubusercontent.com/u/177704202?v=4" width="160" height="160"/> | <img src="https://avatars.githubusercontent.com/u/175805693?v=4" width="160" height="160"/> | <img src="https://avatars.githubusercontent.com/u/1223020?v=4" width="160" height="160"/> | <img src="https://avatars.githubusercontent.com/u/111125866?v=4" width="160" height="160"/> |
| :--------------------------------------------------------------: | :--------------------------------------------------------------: | :--------------------------------------------------------------: | :--------------------------------------------------------------: | :--------------------------------------------------------------: |
|            [이동호](https://github.com/Horidong)             |            [김서현](https://github.com/tjgusKim)             |            [김요셉](https://github.com/sebi0334)             |            [이봉균](https://github.com/deptno)             |            [최수민](https://github.com/raeul0304)             |
|                            팀장, FE UI/API서버 개발                             |                            추천 모델 개발                             |                            추천 모델 개발                             |                            인프라 개발                             |                            추천 모델 개발                             |

## 0. Overview
### Environment
- Python 3.10
- Docker
- MLFlow
- AirFlow
- FastAPI
- Streamlit

### Requirements
- scikitlearn
- pytorch
- pandas
- implicit

## 1. Project Info

### Overview
- 영화 추천 시스템을 구축
- 실시간 및 배치 방식으로 배포
- 사용자 리뷰 및 영화 메타데이터를 바탕으로 개인 맞춤형 추천을 수행하는 시스템 개발
- 정기적으로 데이터를 분석해 추천 결과를 업데이트하는 MLOps 파이프라인을 구축
  
### Timeline

- Sept 27 ~ Oct 4 - 베이스라인 프로토타이핑
- Oct 1 ~ Oct 4 - MLFlow 인프라 구축
- Oct 7 ~ Oct 11 - Airflow 인프라 구축, 추천 모델 개발 및 튜닝, BackEnd API 개발, FrontEnd UI 개발
- Oct 11 - 프로젝트 마감

## 2. Components

### Directory

```
├── src
│   ├── scripts
│   │   ├── pages
│   │   │   ├── page_first.py
│   │   │   └── page_recommend.py
│   │   ├── api_main.py            # API 통신부
│   │   ├── movel_server.py        # 모델 관리 서버
│   │   ├── main_app.py            # 프론트엔드 메인페이지
│   │   ├── parser_moviedata.py    # 영화 데이터 파싱
│   │   ├── movie_update.py        # 변경된 영화 데이터만 업데이트
│   ├── datasets
│   │   ├── movie.csv          # 영화 정보 메타데이터
│   │   ├── rating.csv         # 평점 데이터
│   │   └── credits.csv        # 영화 감독/배우 데이터
│   └── resources            # 이미지를 불러오지 못했을 경우 출력할 임시 이미지
│       ├── no_ott.png
│       └── no_poster.png
├── mlflow                    # MLFlow
└── airflow                   # Airflow

```

## 3. Data descrption

### Dataset overview

- movie.csv    #영화 제목, 장르, 개봉일, 예산, 수익, ID 등의 정보
- rating.csv    #유저별, 영화별 평점과 평점을 입력한 timestamp
- credit.csv    #영화 별 감독과 배우의 id 및 정보

### EDA
- genre가 id와 value의 dict 형태로 되어있으니 알아보기 쉽도록 str형태로 변경
- satus는 현재 개봉이 되었는지, pre-production 단계인지 등을 나타내주는데, 개봉하거나 제작되지 않은 영화는 추천해도 관람이 불가능하므로 제거

### Data Processing
- credit.csv에 있는 영화별 감독과 배우의 정보를 토대로 영화 별 genre와 director, actor 등의 정보를 임베딩
- 개봉년도가 최근일수록 가중치를 부여

## 4. Modeling

### Model descrition

- _Write model information and why your select this model_

### Modeling Process

- _Write model train and test process with capture_

## 5. Result

### Presentation

- [ML Project - 2조.pdf](https://github.com/user-attachments/files/17352832/ML.Project.-.2.pdf)

## etc

### Screenshots
![image](https://github.com/user-attachments/assets/9854b1f0-6b7d-40b3-aa41-dd3d3ac86cb3)

![image](https://github.com/user-attachments/assets/3f036004-773c-4a5e-b3b7-51b0f3f869cf)



### Meeting Log

- https://www.notion.so/2-b078211999444992916fccbba1eb7cc6

