# Azure – Dockerize FastAPI + Nginx

This step containerizes the FastAPI app with an Nginx reverse proxy for deployment to Azure VM or Container Apps.

## Prerequisites

- Docker and Docker Compose installed
- Azure Storage connection string (from step `01-azure-blob-storage-setup/`)

## Build and Run

```bash
cd infrastructure/azure/06-dockerize-app-and-fastapi

# Set required environment variables
export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=..."
export AZURE_STORAGE_CONTAINER_NAME=models

# Build and start
docker compose up --build
```

API docs available at: `http://localhost/docs`

## Credential Injection

Unlike GCP (which needs a key file), Azure credentials are passed as plain environment variables:

```yaml
environment:
  - AZURE_STORAGE_CONNECTION_STRING=${AZURE_STORAGE_CONNECTION_STRING}
```

For production Container Apps (step 07), managed identity is used instead — no connection
string required, and credentials are never stored in environment variables.

## Image Structure

```
python:3.11-slim-bookworm
└── /app/
    ├── main.py           (FastAPI app — loads models from Azure Blob)
    ├── requirements.txt
    └── scripts/
        └── blob.py       (Azure Blob download utility)
```

The app runs as non-root `appuser`. Port 5000 is exposed internally; Nginx
listens on port 80 and proxies to the app.
