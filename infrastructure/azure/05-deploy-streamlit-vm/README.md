# Azure – Deploy Streamlit to Azure VM

This step deploys the Streamlit frontend to an Azure VM so it is accessible from the internet on port 8501.

## Prerequisites

- Azure VM created in step `03-azure-vm-setup/`
- FastAPI already running on the same VM (port 5000)
- Azure CLI authenticated (`az login`)

## Steps

### 1. Copy Streamlit app to the VM

```bash
# Get the VM's public IP
PUBLIC_IP=$(az vm show -d -g YOUR_RESOURCE_GROUP -n YOUR_VM_NAME --query publicIps -o tsv)

scp infrastructure/azure/04-local-app-development/streamlit/app.py \
    azureuser@${PUBLIC_IP}:~/streamlit-app/
```

### 2. Install dependencies on the VM

```bash
ssh azureuser@${PUBLIC_IP} "pip install streamlit requests"
```

### 3. Open NSG port 8501

```bash
az network nsg rule create \
    --resource-group YOUR_RESOURCE_GROUP \
    --nsg-name YOUR_NSG_NAME \
    --name allow-streamlit \
    --protocol tcp \
    --priority 1100 \
    --destination-port-range 8501 \
    --access allow
```

### 4. Run Streamlit in the background

```bash
ssh azureuser@${PUBLIC_IP} \
    "nohup streamlit run ~/streamlit-app/app.py \
        --server.port 8501 \
        --server.address 0.0.0.0 \
        > ~/streamlit.log 2>&1 &"
```

### 5. Access the app

```
http://PUBLIC_IP:8501
```

## Notebook

See `vm-streamlit-deploy.ipynb` for the SDK-based automated version of the steps above.
