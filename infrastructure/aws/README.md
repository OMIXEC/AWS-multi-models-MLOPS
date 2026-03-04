# AWS Infrastructure & Deployment Guide

This directory contains the step-by-step MLOps process for the AWS environment. The folders are numbered to guide you through the process sequentially: from data storage to model training, compute setup, local app development, and finally, deployment.

## Prerequisites
- Install the AWS CLI and run `aws configure`.
- Ensure your Python environment is set up and install basic dependencies:
  ```bash
  pip install -r requirements.txt
  ```

## Step-by-Step Workflow

1. **`01-s3-storage-setup/`**: Scripts and notebooks to manage S3 buckets for storing models, datasets, and artifacts.
2. **`02-model-training/`**: Jupyter notebooks for training models (e.g., Disaster Tweets, Human Pose, Sentiment Classification). Start here to generate your models before deploying.
3. **`03-ec2-compute-setup/`**: Scripts and guides to launch, configure, and manage EC2 instances.
4. **`04-local-app-development/`**: Local implementations of your ML models using FastAPI (REST API) and Streamlit (Web UI).
5. **`05-deploy-streamlit-ec2/`**: Deploying the Streamlit frontend UI to an EC2 instance.
6. **`06-dockerize-fastapi/`**: Dockerizing the FastAPI backend, preparing it for a containerized deployment.
7. **`07-deploy-fastapi-ecs/`**: Pushing the containerized FastAPI server to Amazon ECR and deploying it on Amazon ECS.