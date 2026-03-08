# Azure – Local Streamlit Frontend

This Streamlit app connects to the FastAPI backend running locally on port 5000.

## Prerequisites

The FastAPI server must be running before launching Streamlit:

```bash
# Start FastAPI (from infrastructure/azure/04-local-app-development/fastapi)
uvicorn main:app --host 0.0.0.0 --port 5000
```

## Setup

```bash
pip install streamlit requests
```

## Run

```bash
streamlit run app.py
# Opens at http://localhost:8501
```

## Usage

The app has three tabs:

| Tab | Endpoint | Input |
|-----|----------|-------|
| Sentiment Analysis | `POST /api/v1/sentiment_analysis` | Text |
| Disaster Tweet | `POST /api/v1/disaster_classifier` | Text |
| Pose Classifier | `POST /api/v1/pose_classifier` | Image URL |

> **Note:** This frontend is cloud-agnostic — it only talks to `http://localhost:5000`.
> Whether the backend loads models from Azure Blob Storage or locally does not affect the frontend.
