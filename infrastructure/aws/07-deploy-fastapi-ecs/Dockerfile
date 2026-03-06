FROM python:3.11-slim

WORKDIR /app
COPY app/requirements.txt .

RUN pip install -r requirements.txt

RUN sudo dnf install curl --allowerasing -y 

COPY ./app /app


CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
