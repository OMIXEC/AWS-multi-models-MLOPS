# GCP – Deploy Streamlit to Compute Engine

This step deploys the Streamlit frontend to a GCE instance so it is accessible from the internet on port 8501.

## Prerequisites

- GCE instance created in step `03-gce-compute-setup/`
- FastAPI already running on the same instance (port 5000)
- `gcloud` CLI authenticated (`gcloud auth login`)

## Steps

### 1. Copy Streamlit app to GCE

```bash
gcloud compute scp \
    infrastructure/gcp/04-local-app-development/streamlit/app.py \
    YOUR_INSTANCE_NAME:~/streamlit-app/ \
    --zone us-central1-a
```

### 2. Install dependencies on the instance

```bash
gcloud compute ssh YOUR_INSTANCE_NAME --zone us-central1-a -- \
    "pip install streamlit requests"
```

### 3. Open firewall port 8501

```bash
gcloud compute firewall-rules create allow-streamlit \
    --allow tcp:8501 \
    --target-tags streamlit-server \
    --description "Allow Streamlit traffic"

# Add the tag to your instance
gcloud compute instances add-tags YOUR_INSTANCE_NAME \
    --tags streamlit-server \
    --zone us-central1-a
```

### 4. Run Streamlit in the background

```bash
gcloud compute ssh YOUR_INSTANCE_NAME --zone us-central1-a -- \
    "nohup streamlit run ~/streamlit-app/app.py \
        --server.port 8501 \
        --server.address 0.0.0.0 \
        > ~/streamlit.log 2>&1 &"
```

### 5. Get the public URL

```bash
gcloud compute instances describe YOUR_INSTANCE_NAME \
    --zone us-central1-a \
    --format="get(networkInterfaces[0].accessConfigs[0].natIP)"
```

Then open: `http://EXTERNAL_IP:8501`

## Notebook

See `gce-streamlit-deploy.ipynb` for the SDK-based automated version of the steps above.
