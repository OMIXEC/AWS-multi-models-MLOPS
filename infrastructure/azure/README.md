# Azure Infrastructure & Deployment Guide

This directory contains the step-by-step MLOps process for the Microsoft Azure environment. The folders are numbered to guide you through the process sequentially: from data storage to model training, compute setup, local app development, and finally, deployment.

## Prerequisites
- Install the Azure CLI and authenticate with `az login`.
- Ensure your Python environment is set up and install basic dependencies:
  ```bash
  pip install -r requirements.txt
  ```

## Step-by-Step Workflow

1. **`01-azure-blob-storage-setup/`**: Scripts and notebooks to manage Azure Blob Storage for storing models, datasets, and artifacts.
2. **`02-model-training/`**: Jupyter notebooks for training models (e.g., Disaster Tweets, Human Pose, Sentiment Classification). Start here to generate your models before deploying.
3. **`03-azure-vm-setup/`**: Scripts and guides to launch, configure, and manage Azure Virtual Machines.
4. **`04-local-app-development/`**: Local implementations of your ML models using FastAPI (REST API) and Streamlit (Web UI).
5. **`05-deploy-streamlit-vm/`**: Deploying the Streamlit frontend UI to an Azure VM instance.
6. **`06-dockerize-app-and-fastapi/`**: Dockerizing the FastAPI backend, preparing it for a containerized deployment.
7. **`07-deploy-azure-container-apps/`**: Pushing the containerized FastAPI server to Azure Container Registry and deploying it on Azure Container Apps.
