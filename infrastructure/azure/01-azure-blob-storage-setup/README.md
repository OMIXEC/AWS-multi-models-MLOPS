# Azure Blob Storage Setup

This module provides comprehensive tools for managing Azure Blob Storage, including creating containers, uploading/downloading files, and managing ML model artifacts.

## Prerequisites

1. **Install dependencies:**
   ```bash
   pip install -r ../../requirements.txt
   ```

2. **Configure environment variables:**
   
   Create a `.env` file in this directory with your Azure credentials:
   
   ```bash
   # Option 1: Using Connection String (recommended for local development)
   AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=your_account_name;AccountKey=your_account_key;EndpointSuffix=core.windows.net"
   AZURE_STORAGE_CONTAINER_NAME=models
   
   # Option 2: Using Azure AD Authentication
   AZURE_STORAGE_ACCOUNT_URL="https://your_account_name.blob.core.windows.net"
   AZURE_STORAGE_ACCOUNT_NAME=your_account_name
   AZURE_STORAGE_CONTAINER_NAME=models
   ```

3. **Authenticate with Azure:**
   ```bash
   az login
   ```

## Usage

### Python API

```python
from setup_blob_storage import (
    create_container,
    upload_blob,
    download_blob,
    list_blobs,
    delete_blob,
    upload_directory,
    download_directory,
)

# Create a container
create_container("my-container")

# Upload a single file
upload_blob("my-container", "model.pt", "models/model.pt")

# Download a file
download_blob("my-container", "models/model.pt", "model.pt")

# List all blobs
list_blobs("my-container", prefix="models/")

# Upload entire directory
upload_directory("my-container", "./models/", prefix="models/")

# Download directory
download_directory("my-container", "./downloads/", prefix="models/")
```

### Command Line Interface

```bash
# Create container
python setup_blob_storage.py create --container my-container

# Upload file
python setup_blob_storage.py upload --container my-container --file model.pt --blob models/model.pt

# Download file
python setup_blob_storage.py download --container my-container --blob models/model.pt --file model.pt

# List blobs
python setup_blob_storage.py list --container my-container --prefix models/

# Delete blob
python setup_blob_storage.py delete --container my-container --blob models/model.pt

# Upload directory
python setup_blob_storage.py upload-dir --container my-container --dir ./models/ --prefix models/

# Download directory
python setup_blob_storage.py download-dir --container my-container --dir ./downloads/ --prefix models/
```

## Functions

| Function | Description |
|----------|-------------|
| `get_blob_service_client()` | Get BlobServiceClient using connection string or DefaultAzureCredential |
| `get_container_client(container_name)` | Get ContainerClient for specified container |
| `create_container(container_name)` | Create a new blob container if it doesn't exist |
| `upload_blob(container_name, file_path, blob_name)` | Upload a local file to blob storage |
| `download_blob(container_name, blob_name, download_path)` | Download a blob to local file |
| `list_blobs(container_name, prefix)` | List all blobs in a container |
| `delete_blob(container_name, blob_name)` | Delete a blob from storage |
| `upload_directory(container_name, local_dir, prefix)` | Upload all files from a local directory |
| `download_directory(container_name, local_dir, prefix)` | Download all blobs from prefix to local directory |

## Azure CLI Commands

```bash
# Login to Azure
az login

# Create a storage account
az storage account create --name mystorageaccount --resource-group myResourceGroup --location eastus --sku Standard_LRS

# Get connection string
az storage account show-connection-string --name mystorageaccount --resource-group myResourceGroup

# Create container
az storage container create --name models --account-name mystorageaccount

# Upload file
az storage blob upload --container-name models --name models/model.pt --file model.pt --account-name mystorageaccount

# List blobs
az storage blob list --container-name models --account-name mystorageaccount

# Download file
az storage blob download --container-name models --name models/model.pt --file model.pt --account-name mystorageaccount
```
