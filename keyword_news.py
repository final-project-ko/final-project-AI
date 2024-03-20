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

# 뉴스 제목 문자열을 받는 새로운 DTO 정의
class keywordNewsDTO(BaseModel):
    titles: str  # 2000자로 제한된 뉴스 제목 문자열

async def keyword_news(titles: str):
    
            # 제목에서 필요 없는 문자 제거
    def clean_title(title):
        title = title.replace("\n", " ")
        clean_text = re.sub(r'[^가-힣A-Za-z0-9 .,!?~()%·\[\]]', '', title)
        return clean_text

    # 여기서는 titles가 이미 모든 제목을 포함하는 하나의 문자열이므로, 별도의 조합 과정 필요 없음
    final_titles = clean_title(titles)  # 2000자로 제한된 문자열을 정제
    logging.info(f"Received keywordData: {final_titles}")
    
    # Google API 키 호출
    google_api_key = os.getenv('GOOGLE_API_KEY')

    # ai프롬포트 
    message_content = "내용 중에서 가장 인기 많은 핫토픽 키워드를 20개 추출해라. 쉼표로 구분된 하나의 문장으로 답해야 하고, 한국어로 대답해라. 키워드 단어 20개만 작성한다. 각 단어는 반드시 15글자 이내여야 한다."

    # ai 모델: gemini-pro
    model = ChatGoogleGenerativeAI(model="gemini-pro", convert_system_message_to_human=True, temperature=0.3)

    # 프롬포트 및 명령어 삽입 후 ai 변환 실행
    try:
        result = model([
            SystemMessage(content=message_content),
            HumanMessage(content=final_titles)
        ])
        extracted_keywords = result.content 
    except Exception as e:
        print(f"Error during AI description generation: {e}")
        extracted_keywords = "Error"  # 예외가 발생한 경우, 여기에서 할당
        return {"message": "AI description generation failed", "error": str(e)}
    
    
    
    # DB 연결
    db_connection = mysql.connector.connect(host=host, port=mysql_port, user=user, password=password, database=database)

    # 만약에 DB가 연결되었다면 > update_keyword_titles_for_news 함수 호출 후 실행한다. 
    if db_connection.is_connected():

        update_result = update_keyword_titles_for_news(db_connection, extracted_keywords) 
        db_connection.close()  # 사용 후 데이터베이스 연결 종료
        print(f"Update AI Description Result: {update_result}")
        
    else:
        raise HTTPException(status_code=500, detail="데이터베이스 연결에 실패했습니다.")
    
    return {"message": "AI 키워드 추출이 성공적으로 업데이트 되었습니다."}
    
    
# 2. DB 업데이트 함수 update_keyword_titles_for_news
def update_keyword_titles_for_news(db_connection,  extracted_keywords):
    cursor = db_connection.cursor(dictionary=True)
    
    try:
        # title을 ,으로 분리하고 첫 15개 항목만 선택
        keywords = extracted_keywords.split(',')[:15]
        # 누락된 항목을 처리하기 위해 길이 체크 후 부족한 만큼 빈 문자열로 채움
        keywords += [''] * (15 - len(keywords))
        
        # 현재 시간을 YYYY-MM-DD HH:MM:SS 형식으로 포맷
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        update_query = """
        INSERT INTO tbl_keyword_news (keyword_1, keyword_2, keyword_3, keyword_4, keyword_5,
                                        keyword_6, keyword_7, keyword_8, keyword_9, keyword_10,
                                        keyword_11, keyword_12, keyword_13, keyword_14, keyword_15,
                                        keyword_news_code, date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1, %s)
        ON DUPLICATE KEY UPDATE 
            keyword_1 = VALUES(keyword_1), keyword_2 = VALUES(keyword_2), keyword_3 = VALUES(keyword_3),
            keyword_4 = VALUES(keyword_4), keyword_5 = VALUES(keyword_5), keyword_6 = VALUES(keyword_6),
            keyword_7 = VALUES(keyword_7), keyword_8 = VALUES(keyword_8), keyword_9 = VALUES(keyword_9),
            keyword_10 = VALUES(keyword_10), keyword_11 = VALUES(keyword_11), keyword_12 = VALUES(keyword_12),
            keyword_13 = VALUES(keyword_13), keyword_14 = VALUES(keyword_14), keyword_15 = VALUES(keyword_15),
            date = VALUES(date);
        """
        

        # 쿼리에 들어갈 값 설정 (keyword_news_code에는 1을, date에는 현재 시간을 사용)
        update_values = tuple(keywords + [current_time])

        # SQL 쿼리 실행
        cursor.execute(update_query, update_values)

        # 데이터베이스에 변경사항 적용
        db_connection.commit()

        print("News updated successfully.")
        return "Success"
    
    except Exception as e:
        print(f"An error occurred: {e}")
        db_connection.rollback()
        return "Failure"

    finally:
        if cursor is not None:
            cursor.close()

