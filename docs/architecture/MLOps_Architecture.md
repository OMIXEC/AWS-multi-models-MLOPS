# MLOps Architecture

This document outlines the high-level architecture of the Machine Learning Operations (MLOps) pipeline used in this project.

## System Architecture Diagram

```mermaid
graph TD
    subgraph Training_Environment ["Training & Development"]
        Data[(Data Source)]
        TS[Training Server]
    end

    subgraph AWS_Cloud ["AWS Cloud Infrastructure"]
        S3[(Amazon S3)]
        
        subgraph EC2_Environment ["EC2 Instance"]
            subgraph Docker_Container ["Docker Container"]
                FA((FastAPI Server))
                API_Endpoint{REST API}
            end
        end
    end

    Actor((End User / Actor))

    %% Data flow
    Data --> TS
    Data --> S3
    
    %% Model artifact flow
    TS -->|Uploads Model Artifacts| S3
    S3 <-->|Downloads Artifacts/Data| EC2_Environment
    
    %% API and User interactions
    FA <--> API_Endpoint
    API_Endpoint <-->|HTTP/REST Requests| Actor
```

## Architecture Explanation

1. **Training Server & Data:** This is where the initial data processing and model training occur. The data can either be fed directly into the training server or stored in the cloud.
2. **Amazon S3 (Simple Storage Service):** Acts as the central artifact repository. Once a model is trained (e.g., a `.pt` or `.bin` file), it is uploaded to an S3 bucket. Data assets (like sample images) can also be stored here.
3. **AWS EC2 (Elastic Compute Cloud):** A cloud virtual machine that hosts the production environment.
4. **Docker Container:** Inside the EC2 instance, the application is containerized using Docker to ensure consistency across environments.
5. **FastAPI:** A modern, fast web framework used to build the RESTful API within the Docker container. It loads the model weights from S3 and serves predictions.
6. **Actor (User):** The end-user or client application that sends requests to the FastAPI endpoint and receives predictions in response.
