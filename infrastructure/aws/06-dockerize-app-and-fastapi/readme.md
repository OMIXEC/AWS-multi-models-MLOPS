### 1. **Introduction**
   - Overview of Docker and FastAPI
   - Why use Docker and FastAPI? Benefits in development and deployment.

### 2. **Setting Up Docker**
   - **Docker Installation**
   - Ensure Docker Desktop is Running (Important Note)
   - **Basic Docker Commands**
     - `docker --help`, `docker run --help`, `docker ps --help`
     - **Top 10 Important Docker Commands**:
       - `docker run`
       - `docker ps`
       - `docker tag`
       - `docker images`
       - `docker pull`
       - `docker push`
       - `docker build`
       - `docker exec`
       - `docker stop`
       - `docker rm`

### 3. **Dockerfile and Docker Compose**
   - **Creating a Dockerfile**
     - Explanation of key instructions (FROM, RUN, CMD, etc.)
   - **Introduction to Docker Compose**
     - **Top 10 Important Docker Compose Commands**:
       - `docker-compose up`
       - `docker-compose down`
       - `docker-compose build`
       - `docker-compose ps`
       - `docker-compose logs`
       - `docker-compose exec`
       - `docker-compose stop`
       - `docker-compose rm`
       - `docker-compose restart`
       - `docker-compose scale`
   - **Scaling with Docker Compose**
     - Example: Scaling up with `--scale` (multiple instances with different ports)
   - **Nginx as a Reverse Proxy**
     - Basic setup of Nginx for load balancing and reverse proxy.

### 4. **Working with Docker Images**
   - **Pushing to Docker Hub**
     - **Docker Credentials Setup**
       - `docker login` (enter username and password)
     - Tagging and Pushing Images
       - `docker tag your-image-name omixec/your-image-name:latest`
       - `docker push omixec/your-image-name:latest`
   - **Saving and Loading Docker Images**
     - Save image to a tar/zip file: `docker save -o your-image-name.tar omixec/your-image-name:latest`
     - Load image from tar/zip file: `docker load -i your-image-name.tar`

### 5. **Integrating ML Code with Docker**
   - Adding and running ML code inside Docker containers.

### 6. **Deploying Docker Containers to Cloud**

#### **1. Build and Push to AWS ECR**
AWS ECR is the private registry where your Docker images live. Unlike S3 (which is for static files), ECR is optimized for container images.

**Step A: Create the Repository**
```bash
aws ecr create-repository --repository-name my-app-repo --region us-east-1
```

**Step B: Authenticate Docker to ECR**
You must give Docker permission to "talk" to AWS.
```bash
# Replace <aws_account_id> with your actual ID
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com
```

**Step C: Build, Tag, and Push**
```bash
# 1. Build the image
docker build -t my-app .

# 2. Tag it for the AWS registry
docker tag my-app:latest <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/my-app-repo:latest

# 3. Push it
docker push <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/my-app-repo:latest
```

#### **2. Deploying to AWS ECS (Recommended)**
ECS is the managed "orchestrator." It handles running the containers so you don't have to manage the underlying OS.

**Step A: Create a Cluster**
```bash
aws ecs create-cluster --cluster-name my-app-cluster
```

**Step B: Register a Task Definition**
The Task Definition is a JSON file that tells AWS which image to use, how much CPU/RAM it needs, and which ports to open.
```bash
# Register the task (assuming you have a task-definition.json file)
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

**Step C: Create the Service**
This command actually starts the containers.
```bash
aws ecs create-service \
    --cluster my-app-cluster \
    --service-name my-app-service \
    --task-definition my-app-task \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
```

#### **3. Deploying to AWS EC2 (Manual Approach)**
If you prefer a raw Virtual Machine (EC2), you have to manually pull and run the image.

**Step A: Connect to your EC2**
```bash
ssh -i "your-key.pem" ec2-user@your-ec2-public-ip
```

**Step B: Install Docker & Authenticate**
Once inside the EC2 instance:
```bash
sudo yum update -y
sudo amazon-linux-extras install docker
sudo service docker start
sudo usermod -a -G docker ec2-user
# Logout and log back in for permissions to take effect
```

**Step C: Pull and Run**
```bash
# Authenticate (same as Step 1B)
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com

# Pull and Run
docker pull <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/my-app-repo:latest
docker run -d -p 80:8080 <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/my-app-repo:latest
```

#### **4. Deploying with Terraform (Infrastructure as Code)**
Using Terraform allows you to define your infrastructure as code for reproducible deployments.

**ECR Repository Example:**
```hcl
resource "aws_ecr_repository" "app_repo" {
  name                 = "my-app-repo"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}
```

**ECS Cluster & Service Example:**
```hcl
resource "aws_ecs_cluster" "main" {
  name = "my-app-cluster"
}

resource "aws_ecs_task_definition" "app" {
  family                   = "my-app-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"

  container_definitions = jsonencode([
    {
      name      = "my-app"
      image     = "${aws_ecr_repository.app_repo.repository_url}:latest"
      essential = true
      portMappings = [
        {
          containerPort = 8080
          hostPort      = 8080
        }
      ]
    }
  ])
}
```

#### **Summary of Commands**
| Action | Service | Key Command |
| :--- | :--- | :--- |
| **Store** | ECR | `docker push` |
| **Manage** | ECS | `aws ecs create-service` |
| **Compute** | Fargate/EC2 | `aws ecs register-task-definition` |

> **Note on S3:** While you mentioned S3, it is rarely used for Docker images. However, if your app has a frontend (React/Vue), you would build the static files and use `aws s3 sync ./build s3://my-bucket-name` to deploy the UI separately.
   
### 7. **Final Project**
   - Build a FastAPI application, containerize it, and deploy it using Docker and AWS.

### 8. **Docker Installation**
- sudo apt-get remove docker docker-engine docker.io containerd runc
- sudo apt-get update
- sudo apt-get install docker.io
- sudo systemctl start docker

- sudo systemctl enable docker
- sudo usermod -aG docker $USER

- sudo systemctl status docker

