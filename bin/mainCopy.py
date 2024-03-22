# 레디스 연동 후 가동 예정

# import os
# from dotenv import load_dotenv
# from pathlib import Path
# from datetime import datetime
# from fastapi import FastAPI, HTTPException
# import aioredis
# from process_news import process_news, NewsDTO as ProcessNewsDTO
# from receive_news import receive_news, NewsDTO as ReceiveNewsDTO
# from keyword_news import keyword_news, keywordNewsDTO
# from summary_news import summary_news, summaryDTO 
# from pydantic import BaseModel
# from typing import Optional


# # 환경 변수 로드
# env_path = Path('.') / '.env'
# load_dotenv(dotenv_path=env_path)

# app = FastAPI()

# # Redis 연결 설정
# redis = aioredis.from_url("redis://localhost:6379", encoding="utf-8", decode_responses=True)

# async def request_already_processed(key: str) -> bool:
#     exists = await redis.exists(key)
#     if exists:
#         return True
#     else:
#         # 요청 처리 표시를 위해 키를 설정하고, 10초 후에 자동으로 만료되도록 설정합니다.
#         await redis.setex(key, 10, "processing")
#         return False

# current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# @app.get("/java-connection-test")
# async def java_connection_test():
#     print("java 서버와 연결되어 있습니다.", f"{current_time}")
#     return {"message": "Python 서버와 연결되어 있습니다. " + current_time}

# @app.post("/receive-news")
# async def receive_news_route(news: ReceiveNewsDTO):
#     key = f"news:{news.code}"
#     if await request_already_processed(key):
#         raise HTTPException(status_code=400, detail="이미 처리 중인 Ai 뉴스입니다.")
#     # 뉴스 처리 로직
#     return await receive_news(news)

# @app.post("/process-news")
# async def process_news_route(news: ProcessNewsDTO):
#     key = f"news:process:{news.code}"
#     if await request_already_processed(key):
#         raise HTTPException(status_code=400, detail="이미 처리 중인 Ai 번역입니다.")
#     return await process_news(news)

# @app.post("/keyword-news")
# async def receive_titles(news: keywordNewsDTO):
#     key = f"news:keyword:{news.keywordNewsCode}"
#     if await request_already_processed(key):
#         raise HTTPException(status_code=400, detail="이미 처리 중인 키워드 뉴스입니다.")
#     return await keyword_news(news.titles, news.keywordNewsCode)

# @app.post("/summary-news")
# async def summary_news_route(request_body: summaryDTO):
#     key = f"news:summary:{request_body.summaryNewsCode}"
#     if await request_already_processed(key):
#         raise HTTPException(status_code=400, detail="이미 처리 중인 요약 뉴스입니다.")
#     return await summary_news(request_body.newsChunk, request_body.summaryNewsCode)

# server_port = os.getenv("LOCAL_PORT")

# def start_server():
#     command = f"uvicorn main:app --reload --host 0.0.0.0 --port {server_port}"
#     os.system(command)

# if __name__ == "__main__":
#     print("# Python 서버 실행중...")
#     start_server()




# ------- 백업본 2024.03.22




