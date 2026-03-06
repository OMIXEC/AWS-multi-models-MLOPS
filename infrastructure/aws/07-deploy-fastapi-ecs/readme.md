# AWS ECR & ECS Deployment Guide - Python 3.11.8

This comprehensive guide covers deploying a Dockerized FastAPI ML application to AWS ECS with full security, IAM, and production best practices.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [IAM Permissions](#iam-permissions)
3. [S3 Bucket Setup](#s3-bucket-setup)
4. [ECR Repository Setup](#ecr-repository-setup)
5. [Docker Build & Push](#docker-build--push)
6. [ECS Cluster Setup](#ecs-cluster-setup)
7. [Task Definition](#task-definition)
8. [Load Balancer Setup](#load-balancer-setup)
9. [Security Configuration](#security-configuration)
10. [Health Checks & Monitoring](#health-checks--monitoring)
11. [Testing](#testing)
12. [Troubleshooting](#troubleshooting)

---

## Prerequisites

```bash
# Install AWS CLI v2
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# Verify installation
aws --version

# Configure AWS credentials
aws configure
# Enter your Access Key ID, Secret Access Key, Region (e.g., us-east-1)

# Install Docker
brew install docker
docker --version

# Install ECS CLI (optional, for advanced usage)
brew install amazon-ecs-cli
```

---
# Note: in Docker file with our current AMI do not support apt package manager hence we will use 'yum' or 'dnf' to install 'Curl' - to run Dockerfile locally set the Package manager APT as 'apt-get install curl'

## IAM Permissions

### 1. Create IAM Role for ECS Task Execution

```bash
# Create task execution role
aws iam create-role \
    --role-name ecsTaskExecutionRole \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "ecs-tasks.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }'

# Attach AmazonECSTaskExecutionRolePolicy
aws iam attach-role-policy \
    --role-name ecsTaskExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
```

### 2. Create IAM Role for ECS Task (Application Role)

```bash
# Create task role for application
aws iam create-role \
    --role-name mlopsECSTaskRole \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "ecs-tasks.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }'

# Attach S3 permissions
aws iam put-role-policy \
    --role-name mlopsECSTaskRole \
    --policy-name S3AccessPolicy \
    --policy-document '{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket",
                "s3:GetObjectVersion"
            ],
            "Resource": [
                "arn:aws:s3:::mlops-multi-models",
                "arn:aws:s3:::mlops-multi-models/*"
            ]
        }]
    }'

# Attach CloudWatch Logs permissions
aws iam put-role-policy \
    --role-name mlopsECSTaskRole \
    --policy-name CloudWatchLogsPolicy \
    --policy-document '{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }]
    }'

# Attach ECR permissions for pulling images
aws iam attach-role-policy \
    --role-name mlopsECSTaskRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly
```

### 3. Create Security Group for ECS Tasks

```bash
# Create security group
aws ec2 create-security-group \
    --group-name ecs-security-group \
    --description "Security group for ECS tasks" \
    --vpc-id <YOUR_VPC_ID>

# Allow HTTP/HTTPS traffic
aws ec2 authorize-security-group-ingress \
    --group-name ecs-security-group \
    --protocol tcp \
    --port 5000 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-name ecs-security-group \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

# For production, restrict to your VPC or specific IPs
```

---

## S3 Bucket Setup

### 1. Create S3 Bucket (if not exists)

```bash
# Create bucket
aws s3 mb s3://mlops-multi-models --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
    --bucket mlops-multi-models \
    --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
    --bucket mlops-multi-models \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            }
        }]
    }'

# Block public access
aws s3api put-public-access-block \
    --bucket mlops-multi-models \
    --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

### 2. Upload Model Artifacts

```python
import boto3
import os

s3 = boto3.client('s3')

# Upload model directory
local_model_path = "./tinybert-sentiment-analysis"
bucket_name = "mlops-multi-models"

for root, dirs, files in os.walk(local_model_path):
    for file in files:
        local_path = os.path.join(root, file)
        s3_key = os.path.relpath(local_path, local_model_path)
        s3.upload_file(local_path, bucket_name, f"models/{s3_key}")
        print(f"Uploaded {s3_key}")

# Verify upload
response = s3.list_objects_v2(Bucket=bucket_name, Prefix="models/")
for obj in response.get('Contents', []):
    print(obj['Key'])
```

---

## ECR Repository Setup

### 1. Create ECR Repository

```bash
# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
AWS_REGION="us-east-1"

# Create ECR repository
aws ecr create-repository \
    --repository-name multi-models-mlops-api \
    --image-scanning-configuration scanOnPush=true \
    --encryption-configuration encryptionType=AES256

# Enable immutable image tags (recommended for production)
aws ecr put-image-tag-mutability \
    --repository-name multi-models-mlops-api \
    --image-tag-mutability IMMUTABLE
```

### 2. Docker Build & Push

```bash
# Get login password
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build the image
cd infrastructure/aws/06-dockerize-fastapi
docker build -t multi-models-mlops-api:latest .

# Tag for ECR
docker tag multi-models-mlops-api:latest $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/multi-models-mlops-api:latest

# Push to ECR
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/multi-models-mlops-api:latest

# Verify image
aws ecr list-images --repository-name multi-models-mlops-api
```

---

## ECS Cluster Setup

### 1. Create VPC (if not exists)

```bash
# Get default VPC
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query 'Vpcs[0].VpcId' --output text)

# Get subnet IDs
SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query 'Subnets[*].SubnetId' --output text | tr '\t' ',')
```

### 2. Create ECS Cluster

```bash
# Create cluster with Fargate
aws ecs create-cluster \
    --cluster-name mlops-cluster \
    --cluster-configuration "executeCommandConfiguration={logging=DEFAULT}" \
    --settings "name=containerInsights,value=enabled"

# Verify cluster
aws ecs describe-clusters --cluster mlops-cluster
```

---

## Task Definition

### Create Task Definition (JSON)

```json
{
  "family": "mlops-fastapi-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "executionRoleArn": "arn:aws:iam::ACCOUNT_ID:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::ACCOUNT_ID:role/mlopsECSTaskRole",
  "containerDefinitions": [
    {
      "name": "fastapi-container",
      "image": "ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/multi-models-mlops-api:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 5000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "MODEL_S3_BUCKET",
          "value": "mlops-multi-models"
        },
        {
          "name": "AWS_REGION",
          "value": "us-east-1"
        },
        {
          "name": "LOG_LEVEL",
          "value": "INFO"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/mlops-fastapi-task",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:5000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 120
      },
      "readonlyRootFilesystem": false,
      "privileged": false
    }
  ]
}
```

### Register Task Definition

```bash
aws ecs register-task-definition \
    --cli-input-json file://task-definition.json
```

---

## Load Balancer Setup

### 1. Create Application Load Balancer

```bash
# Create target group
aws elbv2 create-target-group \
    --name mlops-target-group \
    --protocol HTTP \
    --port 5000 \
    --vpc-id <VPC_ID> \
    --target-type ip \
    --health-check-path /health \
    --health-check-interval-seconds 30 \
    --healthy-threshold-count 2 \
    --unhealthy-threshold-count 3

# Create ALB
aws elbv2 create-load-balancer \
    --name mlops-alb \
    --scheme internet-facing \
    --type application \
    --subnets <SUBNET_IDS> \
    --security-groups <SECURITY_GROUP_ID>

# Create listener
aws elbv2 create-listener \
    --load-balancer-arn <ALB_ARN> \
    --protocol HTTP \
    --port 80 \
    --default-actions Type=forward,TargetGroupArn=<TARGET_GROUP_ARN>

# For HTTPS (recommended for production)
aws elbv2 create-listener \
    --load-balancer-arn <ALB_ARN> \
    --protocol HTTPS \
    --port 443 \
    --certificates CertificateArn=<ACM_CERT_ARN> \
    --default-actions Type=forward,TargetGroupArn=<TARGET_GROUP_ARN>
```

---

## Service Deployment

### Create ECS Service

```bash
# Get latest task definition ARN
# We will set 3 tasks
TASK_DEFINITION_ARN=$(aws ecs list-task-definitions \
    --family-prefix mlops-fastapi-task \
    --status ACTIVE \
    --max-items 1 \
    --query 'taskDefinitionArns[0]' \
    --output text)

# Create service
aws ecs create-service \
    --cluster mlops-cluster \
    --service-name mlops-fastapi-service \
    --task-definition "$TASK_DEFINITION_ARN" \
    --desired-count 3 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=<SUBNET_IDS>,securityGroups=<SECURITY_GROUP_ID>,assignPublicIp=ENABLED}" \
    --load-balancers "targetGroupArn=<TARGET_GROUP_ARN>,containerName=fastapi-container,containerPort=5000" \
    --health-check-grace-period-seconds 120 \
    --deployment-configuration "minimumHealthyPercent=50,maximumPercent=200"
```

---

## Security Configuration

### 1. Enable Container Insights

```bash
aws ecs update-cluster-settings \
    --cluster mlops-cluster \
    --settings name=containerInsights,value=enabled
```

### 2. Enable CloudTrail Logging

```bash
# Create S3 bucket for CloudTrail
aws s3 mb s3://mlops-cloudtrail-logs --region us-east-1

# Create trail
aws cloudtrail create-trail \
    --name mlops-trail \
    --s3-bucket-name mlops-cloudtrail-logs \
    --is-multi-region-trail \
    --enable-log-file-validation
```

### 3. Enable GuardDuty (Security)

```bash
# Enable GuardDuty
aws guardduty create-detector \
    --enable
```

### 4. Secrets Management (Optional)

```bash
# Store secrets in Secrets Manager
aws secretsmanager create-secret \
    --name mlops/api-keys \
    --description "API keys for ML application" \
    --secret-string '{"api_key":"your-secret-key"}'

# Grant ECS task access to secrets
aws iam put-role-policy \
    --role-name mlopsECSTaskRole \
    --policy-name SecretsManagerPolicy \
    --policy-document '{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue"
            ],
            "Resource": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:mlops/api-keys-*"
        }]
    }'
```

---

## Health Checks & Monitoring

### 1. CloudWatch Dashboard

```bash
# Create log group
aws logs create-log-group --log-group-name /ecs/mlops-fastapi-task

# View logs
aws logs tail /ecs/mlops-fastapi-task --follow
```

### 2. Custom Metrics with Prometheus

```python
from prometheus_client import Counter, generate_latest
from fastapi import FastAPI, Response

app = FastAPI()

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type="text/plain")
```

---

## Testing

### 1. API Testing Script

```python
import requests
import json
import time

# Get Load Balancer DNS
LB_DNS = "app-lb-2030153789.us-east-1.elb.amazonaws.com"

BASE_URL = f"http://{LB_DNS}"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Check: {response.status_code}")
    return response.status_code == 200

def test_sentiment():
    """Test sentiment classification"""
    url = f"{BASE_URL}/api/v1/sentiment"
    headers = {'Content-Type': 'application/json'}
    payload = json.dumps({
        "texts": ["I love this product!", "This is terrible."]
    })
    
    response = requests.post(url, headers=headers, data=payload)
    print(f"Sentiment: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_pose():
    """Test pose classification"""
    url = f"{BASE_URL}/api/v1/pose_classifier"
    headers = {'Content-Type': 'application/json'}
    payload = json.dumps({
        "url": ["https://images.pexels.com/photos/1755385/pexels-photo-1755385.jpeg"]
    })
    
    response = requests.post(url, headers=headers, data=payload)
    print(f"Pose: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def run_load_test(num_requests=100):
    """Run load test"""
    url = f"{BASE_URL}/api/v1/sentiment"
    headers = {'Content-Type': 'application/json'}
    payload = json.dumps({
        "texts": ["Great product!"]
    })
    
    start = time.time()
    success = 0
    failures = 0
    
    for i in range(num_requests):
        try:
            response = requests.post(url, headers=headers, data=payload, timeout=30)
            if response.status_code == 200:
                success += 1
            else:
                failures += 1
        except Exception as e:
            failures += 1
    
    duration = time.time() - start
    print(f"\nLoad Test Results:")
    print(f"Total Requests: {num_requests}")
    print(f"Successful: {success}")
    print(f"Failed: {failures}")
    print(f"Duration: {duration:.2f}s")
    print(f"RPS: {num_requests/duration:.2f}")

if __name__ == "__main__":
    print("Running tests...\n")
    
    # Wait for service to be ready
    time.sleep(10)
    
    test_health()
    test_sentiment()
    test_pose()
    run_load_test(100)
```

### 2. Run Tests

```bash
# Test from local machine
python test_api.py

# Test with authentication
import requests
import json

# With API key
headers = {
    'Content-Type': 'application/json',
    'X-API-Key': 'your-api-key'
}
response = requests.post(url, headers=headers, data=payload)
```

---

## Troubleshooting

### Common Issues

```bash
# 1. Check task status
aws ecs describe-tasks --cluster mlops-cluster --tasks <TASK_ID>

# 2. View container logs
aws logs tail /ecs/mlops-fastapi-task --follow

# 3. Check service events
aws ecs describe-services --cluster mlops-cluster --services mlops-fastapi-service

# 4. Check load balancer target health
aws elbv2 describe-target-health --target-group-arn <TARGET_GROUP_ARN>

# 5. Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/ECS \
    --metric-name CPUUtilization \
    --start-time 2024-01-01T00:00:00Z \
    --end-time 2024-01-02T00:00:00Z \
    --period 3600 \
    --statistics Average
```

### Debug Commands

```bash
# Restart service
aws ecs update-service \
    --cluster mlops-cluster \
    --service mlops-fastapi-service \
    --force-new-deployment

# Scale service
aws ecs update-service \
    --cluster mlops-cluster \
    --service mlops-fastapi-service \
    --desired-count 4

# Get task definition details
aws ecs describe-task-definition --task-definition mlops-fastapi-task
```

---

## Cleanup

```bash
# Delete service
aws ecs delete-service \
    --cluster mlops-cluster \
    --service mlops-fastapi-service \
    --force

# Delete cluster
aws ecs delete-cluster --cluster mlops-cluster

# Delete ALB
aws elbv2 delete-load-balancer --load-balancer-arn <ALB_ARN>

# Delete target group
aws elbv2 delete-target-group --target-group-arn <TARGET_GROUP_ARN>

# Delete ECR repository
aws ecr delete-repository \
    --repository-name multi-models-mlops-api \
    --force

# Delete S3 bucket (careful!)
aws s3 rb s3://mlops-multi-models --force
```

---

## Production Checklist

- [ ] Enable HTTPS with ACM certificate
- [ ] Configure custom domain with Route 53
- [ ] Set up WAF for protection
- [ ] Enable GuardDuty
- [ ] Configure CloudWatch alarms
- [ ] Set up automated scaling
- [ ] Enable VPC flow logs
- [ ] Configure backup for model artifacts
- [ ] Set up CI/CD pipeline
- [ ] Enable AWS Config
