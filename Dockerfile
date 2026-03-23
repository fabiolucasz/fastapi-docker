FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .env ./
COPY src/ ./src/

RUN pip install -r requirements.txt --no-cache-dir

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
