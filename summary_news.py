import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import mysql.connector
from pydantic import BaseModel
from typing import List, Optional
from fastapi import HTTPException
import re
import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import logging

# 환경변수 로드
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# MySQL 접속 정보
host = os.getenv("MYSQL_HOST")
mysql_port = os.getenv("MYSQL_PORT") 
user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
database = os.getenv("MYSQL_DATABASE")

# 뉴스 데이터 전송 객체 정의
class NewsDTO(BaseModel):
    newsChunk: str

async def summary_news(news_chunk: str):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 뉴스 타이틀 문자열 정형화
    def clean_Chunk(newsChunk):
        newsChunk = newsChunk.replace("\n", " ")
        clean_newsChunk = re.sub(r'[^가-힣A-Za-z0-9 .,!?~()%·\[\]]', '', newsChunk)  
        return clean_newsChunk

    cleaned_Chunk = clean_Chunk(news_chunk)
    logging.info(f"Received keywordData: {cleaned_Chunk}")

    # Google API 키 호출
    google_api_key = os.getenv('GOOGLE_API_KEY')

    # ai프롬포트 : 한국어일시 한국어로, 영어일시 영어로 입력됨
    message_content = "내용을 바탕으로 오늘의 이슈 요약본을 작성해라. 다섯 문단으로 나누어져 있어야 하고, 글자 개수는 반드시 한국어 1500자 이상이어야 한다. ~습니다. 입니다. 로 끝나는 존칭이 담긴 정중한 어투여야 하고, 친절하게 말해야 한다. 인사와 날짜는 생략하고 본론만 이야기 해야 한다. 주제의 끝 마다 엔터를 두 번 작성해 단락을 끊어야 한다."

    # ai 모델: gemini-pro
    model = ChatGoogleGenerativeAI(model="gemini-pro", convert_system_message_to_human=True, temperature=0.3)

    # 정형화된 데이터 출력 및 AI 요약 생성
    try:
        result = model([
            SystemMessage(content=message_content),
            HumanMessage(content=cleaned_Chunk)
        ])
        news_chunk = result.content  
    except Exception as e:
        print(f"Error during AI description generation: {e}")
        news_chunk = "Error"  # 예외가 발생한 경우, 여기에서 할당
        return {"message": "AI description generation failed", "error": str(e)}
    
    
        # 만약에 DB가 연결되었다면 > update_summary_titles_for_news 함수 호출 후 실행한다. 
        # DB 연결 및 요약 데이터 저장
    db_connection = mysql.connector.connect(host=host, port=mysql_port, user=user, password=password, database=database)

    if db_connection.is_connected():
        # 가정: news_list[0]은 업데이트하고자 하는 뉴스 데이터의 예시
        update_result = update_summary_news(db_connection, news_chunk)
        db_connection.close()  # 사용 후 데이터베이스 연결 종료
        print(f"Update Before Summary Result: {update_result}")
    else:
        raise HTTPException(status_code=500, detail="Database connection failed")

    return {"message": "AI 요약 키워드가 성공적으로 업데이트 되었습니다."}
    
    
# 2. DB 업데이트 함수 update_ai_description_for_news
    # 데이터베이스 연결 함수
def get_db_connection():
    return mysql.connector.connect(host=host, port=mysql_port, user=user, password=password, database=database)

def get_current_execution_order(db_connection):
    cursor = db_connection.cursor(dictionary=True)
    select_query = """
    SELECT execution_order FROM tbl_execution_order WHERE id = 1
    """
    cursor.execute(select_query)
    result = cursor.fetchone()
    cursor.close()
    return result['execution_order'] if result else None

def update_execution_order(db_connection, new_order):
    cursor = db_connection.cursor(dictionary=True)
    update_query = """
    UPDATE tbl_execution_order SET execution_order = %s WHERE id = 1
    """
    cursor.execute(update_query, (new_order,))
    db_connection.commit()
    cursor.close()

def update_summary_news(db_connection, news_chunk, execution_order):
    column_name = f"summary_news_{execution_order}"
    update_query = f"""
    UPDATE tbl_summary_news
    SET {column_name} = %s
    WHERE summary_news_code = 1
    """
    update_values = (news_chunk,)
    
    cursor = db_connection.cursor(dictionary=True)
    try:
        cursor.execute(update_query, update_values)
        db_connection.commit()
        print(f"News with code 1 updated successfully in {column_name}.")
    except mysql.connector.Error as error:
        print(f"Failed to update record to database: {error}")
        return "Failed"
    finally:
        if cursor is not None:
            cursor.close()
    # 실행 순서 업데이트 (5번째 실행 후 초기화)
    new_order = 1 if execution_order == 5 else execution_order + 1
    update_execution_order(db_connection, new_order)
    
    return "Success"

# 실제 업데이트 로직 실행
if __name__ == "__main__":
    db_connection = get_db_connection()
    try:
        execution_order = get_current_execution_order(db_connection)
        if execution_order is not None:
            update_summary_news(db_connection, "새로운 뉴스 내용", execution_order)
        else:
            print("Failed to get the current execution order.")
    finally:
        if db_connection.is_connected():
            db_connection.close()