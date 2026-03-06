# Deploy ML App Docker with Azure Container Registry (ACR) and Azure Container Instances (ACI)

## 1. Push Docker Image to Azure Container Registry (ACR)
Ensure you have created an Azure Container Registry and are authenticated.

```bash
# Login to ACR
az acr login --name YourRegistryName

# Build your image
docker build -t app-image .

# Tag the image for ACR
docker tag app-image yourregistryname.azurecr.io/mlops-api:latest

# Push the image to ACR
docker push yourregistryname.azurecr.io/mlops-api:latest
```

## 2. Deploy to Azure Container Instances (ACI)
Deploying the container to ACI provides an isolated, fast way to run containers without managing underlying VMs.

```bash
az container create \
    --resource-group mlops-rg \
    --name mlops-api-container \
    --image yourregistryname.azurecr.io/mlops-api:latest \
    --dns-name-label mlops-api-instance \
    --ports 80 \
    --cpu 1 \
    --memory 1.5
```

## 3. API Request Example
```python
import requests
import json

# Replace with the actual FQDN from ACI deployment
url = "http://mlops-api-instance.eastus.azurecontainer.io/api/v1/pose_classifier"
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
