import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI
from process_news import process_news, NewsDTO
from receive_news import receive_news, NewsDTO
from keyword_news import keyword_news, keywordNewsDTO
from summary_news import summary_news, NewsDTO # news_processing.py에서 정의된 클래스와 함수를 가져옵니다.
import logging

# 로그 설정
logging.basicConfig(level=logging.INFO)

app = FastAPI()

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@app.get("/java-connection-test")
async def java_connection_test():
    print("java 서버와 연결되어 있습니다.", f"{current_time}")
    return {"message": "Python 서버와 연결되어 있습니다. " + current_time}

@app.post("/receive-news")
async def receive_news_route(news: NewsDTO):
    return await receive_news(news)

@app.post("/process-news")
async def process_news_route(news: NewsDTO):
    return await process_news(news)

@app.post("/keyword-news")
async def receive_titles(news: keywordNewsDTO):
    return await keyword_news(news.titles)

@app.post("/summary-news")
async def summary_news_route(news: NewsDTO):
    return await summary_news(news.newsChunk)


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

server_port = os.getenv("LOCAL_PORT")

def start_server():
    command = f"uvicorn main:app --reload --host 0.0.0.0 --port {server_port}"
    os.system(command)

if __name__ == "__main__":
    print("# Python 서버 실행중...")
    start_server()


# 1. 가상환경 접속 : conda activate langchain 
# 라이브러리를 가상환경에 설치해놓고 실행합니다. 
# 실행하는 가상환경이 같다면, 라이브러리를 추가로 설치하지 않고도 실행할 수 있습니다.
# node_module을 '가상환경'이라는 이름의 폴더에 몽땅 설치해놓고 필요할때 불러와서 쓴다 = 느낌과 거의 비슷합니다!

# 2. 실행 : python main.py

# 2-1. 방화벽에서 실행을 차단했습니다 : 두 항목 모두 체크하고 실행해주세요

# 3. http://0.0.0.0:8089/docs로 가면
# 자동 대화형 API 문서를 볼 수 있습니다. (Swagger UI 제공)



