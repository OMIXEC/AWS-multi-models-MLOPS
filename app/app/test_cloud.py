from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"health": "200", "mode": "aws-s3-cloud"}


def test_get_sentiment_legacy():
    response = client.get("/get_sentiment/helloworld")
    assert response.status_code == 200
    assert response.json() == {
        "text": "helloworld",
        "sentiment": "positive",
        "user_id": None,
    }


def test_get_sentiment_api_v1_path():
    response = client.get("/api/v1/get_sentiment/helloworld?user_id=123")
    assert response.status_code == 200
    assert response.json() == {
        "text": "helloworld",
        "sentiment": "positive",
        "user_id": "123",
    }


def test_get_sentiment_api_v1_query():
    response = client.get("/api/v1/get_sentiment/?text=helloworld&user_id=123")
    assert response.status_code == 200
    assert response.json() == {
        "text": "helloworld",
        "sentiment": "positive",
        "user_id": "123",
    }


def test_post_sentiment_analysis():
    payload = {"text": ["This is a test review"], "user_id": "test@example.com"}
    response = client.post("/api/v1/sentiment_analysis", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "tinybert-sentiment-analysis"
    assert data["text"] == ["This is a test review"]
    assert "labels" in data
    assert "scores" in data
    assert "prediction_time" in data
