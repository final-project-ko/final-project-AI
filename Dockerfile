FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV LOCAL_PORT=8089

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8089

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $LOCAL_PORT"]
