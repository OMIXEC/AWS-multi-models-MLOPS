# GCP – Deploy to Cloud Run

This step pushes the Docker image to Google Artifact Registry and deploys it as a Cloud Run service.

> **Note:** The `artifact_registry_cloud_run/` folder at the root of `infrastructure/gcp/` contains the original setup. This folder (`07-deploy-cloud-run/`) is the canonical version with full Python SDK documentation and least-privilege IAM setup.

## Prerequisites

- Docker image built (step `06-dockerize-app-and-fastapi/`)
- Artifact Registry repository created
- Service account with:
  - `roles/artifactregistry.writer` on the GAR repository
  - `roles/run.developer` at project level
  - `roles/storage.objectViewer` on the GCS bucket

## Quick Deploy (CLI)

```bash
# Authenticate Docker with GAR
gcloud auth configure-docker ${GCP_REGION}-docker.pkg.dev

# Build and tag
docker build -t mlops-api ../06-dockerize-app-and-fastapi/
docker tag mlops-api ${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${GAR_REPOSITORY_NAME}/mlops-api:latest

# Push
docker push ${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${GAR_REPOSITORY_NAME}/mlops-api:latest

# Deploy to Cloud Run
gcloud run deploy mlops-api \
    --image ${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${GAR_REPOSITORY_NAME}/mlops-api:latest \
    --region ${GCP_REGION} \
    --platform managed \
    --allow-unauthenticated \
    --port 5000 \
    --service-account mlops-least-privilege@${GCP_PROJECT_ID}.iam.gserviceaccount.com \
    --set-env-vars GCS_BUCKET_NAME=${GCS_BUCKET_NAME}
```

## SDK-based Deploy

See `gcp-cloud-run-deployment.ipynb` for the full Python SDK version.

## Test the Endpoint

```python
import requests, json

url = "https://YOUR_CLOUD_RUN_URL/api/v1/pose_classifier"
payload = {"url": ["https://images.pexels.com/photos/1755385/pexels-photo-1755385.jpeg"]}
response = requests.post(url, json=payload)
print(response.json())
```
