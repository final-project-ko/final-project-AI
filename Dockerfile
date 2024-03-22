# 파이썬 공식 이미지를 베이스 이미지로 사용
FROM python:3.8-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파이썬 패키지가 명시된 requirements.txt 파일 복사
COPY requirements.txt ./

# requirements.txt에 명시된 파이썬 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 현재 디렉토리의 모든 파일을 컨테이너의 /app 디렉토리로 복사
COPY . .

# 컨테이너가 실행될 때 열릴 포트 번호 지정
EXPOSE 8089

# 컨테이너가 시작될 때 실행될 명령어 설정
CMD ["python", "./main.py"]
