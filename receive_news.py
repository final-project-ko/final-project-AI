import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import mysql.connector
from pydantic import BaseModel
from typing import Optional
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
    code: int   
    title: str   
    category: str   
    description: str    
    url: Optional[str] = None   
    aidescription: Optional[str] = None  
    transdescription: Optional[str] = None  
    
    
# 1. 뉴스 ai 처리 함수
async def receive_news(news: NewsDTO):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 뉴스-내용_ 문자열 정형화
    def clean_description(description):
        description = description.replace("\n", " ")
        clean_text = re.sub(r'[^가-힣A-Za-z0-9 .,!?~()%·\[\]]', '', description)  
        return clean_text

    cleaned_description = clean_description(news.description)
    logging.info(f"Received description: {cleaned_description}")
    
    # Google API 키 호출
    google_api_key = os.getenv('GOOGLE_API_KEY')

    # ai프롬포트 : 한국어일시 한국어로, 영어일시 영어로 입력됨
    if re.search("[가-힣]", news.description):
        message_content = "다음 기사를 요약해라. 정중한 말투로 작성해야 하고, 뉴스 기사 같이 읽는 목적의 긴 문장이어야 한다. 타이틀, 인사, 마크다운 기호 등을 생략하고 내용만 작성한다. 반드시 1500자 이상이어야 한다."
    else:
        message_content = "Summarize the following article. It must be written in a polite way and a long sentence for the purpose of reading like a news article. Write only the contents, omitting titles, greetings, and markdown symbols. It must be at least 1500 characters long."

    # ai 모델: gemini-pro
    model = ChatGoogleGenerativeAI(model="gemini-pro", convert_system_message_to_human=True, temperature=0.3)

    # 프롬포트 및 명령어 삽입 후 ai 변환 실행
    try:
        result = model([
            SystemMessage(content=message_content),
            HumanMessage(content=cleaned_description)
        ])
        news.aidescription = result.content  
    except Exception as e:
        print(f"Error during AI description generation: {e}")
        news.aidescription = "Error"  # 예외가 발생한 경우, 여기에서 할당
        return {"message": "AI description generation failed", "error": str(e)}
    
    # DB 연결
    db_connection = mysql.connector.connect(host=host, port=mysql_port, user=user, password=password, database=database)

    # 만약에 DB가 연결되었다면 > update_ai_description_for_news 함수 호출 후 실행한다. 
    if db_connection.is_connected():

        update_result = update_ai_description_for_news(db_connection, news)
        db_connection.close()  # 사용 후 데이터베이스 연결 종료
        print(f"Update AI Description Result: {update_result}")
        
    else:
        raise HTTPException(status_code=500, detail="데이터베이스 연결에 실패했습니다.")
    
    return {"message": "AI 설명이 성공적으로 업데이트 되었습니다. " + current_time}
    
    
    
# 2. DB 업데이트 함수 update_ai_description_for_news
def update_ai_description_for_news(db_connection, news):
    
    cursor = db_connection.cursor(dictionary=True)
    
    try:
        # ai_description이 'null' 혹은 'Error'인 경우, 해당 뉴스를 삭제
        if news.aidescription is None or news.aidescription == "Error":
            delete_query = """
            DELETE FROM tbl_news
            WHERE news_code = %s
            """
            delete_values = (news.code,)
            cursor.execute(delete_query, delete_values)
            db_connection.commit()
            
            print(f"안전선 기준에 위배된 뉴스 내용을 삭제했습니다. code number: {news.code}")
            return "안전선 기준에 위배된 뉴스 내용을 삭제했습니다."
        
        else:
            # tbl_news 테이블에 ai_description을 업데이트하는 SQL 쿼리
            update_query = """
            UPDATE tbl_news
            SET ai_description = %s
            WHERE news_code = %s
            """
            
            update_values = (news.aidescription, news.code)
            
            # SQL 쿼리 실행
            cursor.execute(update_query, update_values)
            
            # 데이터베이스에 변경사항 적용
            db_connection.commit()
            
            print(f"ai뉴스가 업로드 되었습니다. 코드번호: {news.code}")
            return "Success"
    
        
    except mysql.connector.Error as error:
        print(f"Failed to update record to database: {error}")
        return "Failed"
        
    finally:
        if cursor is not None:
            cursor.close()
            