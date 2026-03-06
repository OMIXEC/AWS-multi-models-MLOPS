# Deploy ML App Docker with GCP Artifact Registry and Cloud Run

## 1. Tag and Push Docker Image to Google Artifact Registry (GAR)
Ensure you are authenticated with `gcloud` and have configured Docker to use GAR.

```bash
# Configure Docker to use GAR
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build your image
docker build -t app-image .

# Tag the image for GAR
docker tag app-image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/YOUR_REPO_NAME/mlops-api:latest

# Push the image to GAR
docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/YOUR_REPO_NAME/mlops-api:latest
```

## 2. Deploy to Cloud Run
Deploying the container to Cloud Run provides a scalable, serverless endpoint.

```bash
gcloud run deploy mlops-api \
    --image us-central1-docker.pkg.dev/YOUR_PROJECT_ID/YOUR_REPO_NAME/mlops-api:latest \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --port 80
```

## 3. API Request Example
```python
import requests
import json

url = "https://mlops-api-xxxxxxxx-uc.a.run.app/api/v1/pose_classifier"
headers = {
  'Content-Type': 'application/json'
}

payload = json.dumps({
  "url": [
    "https://images.pexels.com/photos/1755385/pexels-photo-1755385.jpeg"
  ]
})

response = requests.request("POST", url, headers=headers, data=payload)
print(response.text)
```
