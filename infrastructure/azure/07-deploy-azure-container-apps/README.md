# Azure – Deploy to Azure Container Apps

This step pushes the Docker image to Azure Container Registry and deploys it as an Azure Container App.

> **Note:** The `container_registry_aci/` folder at the root of `infrastructure/azure/` contains the original ACR/ACI setup. This folder (`07-deploy-azure-container-apps/`) is the canonical version with full Python SDK documentation and least-privilege RBAC.

## Prerequisites

- Docker image built (step `06-dockerize-app-and-fastapi/`)
- Azure Container Registry created
- Service Principal with:
  - `AcrPush` on the ACR resource
  - `Storage Blob Data Reader` on the storage account

## Quick Deploy (CLI)

```bash
# Login to ACR
az acr login --name ${ACR_NAME}

# Build and tag
docker build -t mlops-api ../06-dockerize-app-and-fastapi/
docker tag mlops-api ${ACR_NAME}.azurecr.io/mlops-api:latest

# Push
docker push ${ACR_NAME}.azurecr.io/mlops-api:latest

# Create Container Apps environment
az containerapp env create \
    --name mlops-env \
    --resource-group ${RESOURCE_GROUP} \
    --location ${AZURE_LOCATION}

# Deploy Container App
az containerapp create \
    --name mlops-api \
    --resource-group ${RESOURCE_GROUP} \
    --environment mlops-env \
    --image ${ACR_NAME}.azurecr.io/mlops-api:latest \
    --registry-server ${ACR_NAME}.azurecr.io \
    --target-port 5000 \
    --ingress external \
    --env-vars AZURE_STORAGE_CONNECTION_STRING=secretref:storage-connection
```

## SDK-based Deploy

See `azure-container-apps-deployment.ipynb` for the full Python SDK version.

## Test the Endpoint

```python
import requests

url = "https://YOUR_CONTAINER_APP_URL/api/v1/pose_classifier"
payload = {"url": ["https://images.pexels.com/photos/1755385/pexels-photo-1755385.jpeg"]}
response = requests.post(url, json=payload)
print(response.json())
```
