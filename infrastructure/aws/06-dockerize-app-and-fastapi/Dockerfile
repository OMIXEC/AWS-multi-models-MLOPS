FROM python:3.11-slim

WORKDIR /app

COPY ./app /app

COPY app/requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
