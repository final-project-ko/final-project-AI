from dotenv import load_dotenv
from pathlib import Path
import os
import mysql.connector

# 환경변수 로드
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# MySQL 접속 정보
host = os.getenv("MYSQL_HOST")
mysql_port = os.getenv("MYSQL_PORT")
user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASSWORD")
database = os.getenv("MYSQL_DATABASE")

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
    # 실행 순서에 따라 동적으로 컬럼 이름을 결정
    column_name = f"summary_news_{execution_order}"
    update_query = f"""
    UPDATE tbl_summary_news
    SET {column_name} = %s
    WHERE summary_news_code = 1
    """
    # 단일 값만 업데이트하므로, 하나의 값만 전달
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

            
# 1. 가상환경 접속 : conda activate langchain 
# 라이브러리를 가상환경에 설치해놓고 실행합니다. 
# 실행하는 가상환경이 같다면, 라이브러리를 추가로 설치하지 않고도 실행할 수 있습니다.
# node_module을 '가상환경'이라는 이름의 폴더에 몽땅 설치해놓고 필요할때 불러와서 쓴다 = 느낌과 거의 비슷합니다!

# 2. 실행 : python dbtest.py

# 2-1. 방화벽에서 실행을 차단했습니다 : 두 항목 모두 체크하고 실행해주세요

# 3. http://0.0.0.0:8089/docs로 가면
# 자동 대화형 API 문서를 볼 수 있습니다. (Swagger UI 제공)


