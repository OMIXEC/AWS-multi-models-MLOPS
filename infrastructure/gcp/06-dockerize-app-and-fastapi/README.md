# GCP – Dockerize FastAPI + Nginx

This step containerizes the FastAPI app with an Nginx reverse proxy for deployment to GCE or Cloud Run.

## Prerequisites

- Docker and Docker Compose installed
- GCP service account key file with `roles/storage.objectViewer` on the GCS bucket
- `.env` file with `GCS_BUCKET_NAME` set

## Build and Run

```bash
cd infrastructure/gcp/06-dockerize-app-and-fastapi

# Place your service account key
mkdir -p ~/.gcloud
cp /path/to/your-service-account-key.json ~/.gcloud/service-account-key.json

# Set bucket name
export GCS_BUCKET_NAME=mlops-multi-models-gcp

# Build and start
docker compose up --build
```

API docs available at: `http://localhost/docs`

## Credential Injection

GCS credentials are injected by mounting `~/.gcloud` into the container:

```yaml
volumes:
  - ~/.gcloud:/gcloud:ro
environment:
  - GOOGLE_APPLICATION_CREDENTIALS=/gcloud/service-account-key.json
```

This avoids baking credentials into the image. For Cloud Run (step 07), the
service account is attached directly to the Cloud Run service — no key file needed.

## Image Structure

```
python:3.11-slim-bookworm
└── /app/
    ├── main.py           (FastAPI app — loads models from GCS)
    ├── requirements.txt
    └── scripts/
        └── gcs.py        (GCS download utility)
```

The app runs as non-root `appuser`. Port 5000 is exposed internally; Nginx
listens on port 80 and proxies to the app.
