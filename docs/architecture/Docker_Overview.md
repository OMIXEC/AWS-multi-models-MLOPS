# Docker Guide

## What is Docker?
* Lightweight, open, secure platform.
* Simplifies building, shipping, and running apps.
* Runs natively on Linux or Windows Server.
* Runs on Windows or Mac development machines (via virtual machine).
* Relies on "images" and "containers".

## What is a Container?
* Standardized packaging for software and dependencies.
* Isolates apps from each other.
* Shares the same OS kernel (unlike Virtual Machines which have separate Guest OSs and a Hypervisor).
* Works for all major Linux distributions and Windows Server 2016+.

## The Role of Images and Containers
* **Docker Image:** The blueprint. E.g., Ubuntu with Node.js and Application Code. The basis of a Docker container; represents a full application.
* **Docker Container:** Created by using an image. It is the standard unit in which the application service resides and executes.

## The Docker Workflow
1. **Build (Developers):** Create Development Environments.
2. **Ship:** Create and Store Images in registries.
3. **Run (IT Operations):** Deploy, Manage, and Scale containers on the host servers.

## Docker Vocabulary
* **Docker Image:** The basis of a container.
* **Docker Container:** The running instance of an image.
* **Docker Engine:** Creates, ships, and runs Docker containers.
* **Registry Service:** (e.g., Docker Hub, ECR) Cloud or server-based storage for your images.

## Basic Docker Commands
```bash
$ docker image pull node:latest
$ docker image ls
$ docker container run -d -p 5000:5000 --name node node:latest
$ docker container ps
$ docker container stop node (or <container id>)
$ docker container rm node (or <container id>)
$ docker image rmi (or <image id>)
$ docker build -t node:2.0 .
$ docker image push node:2.0
$ docker --help
```

## Docker Compose & Dockerfile
A `Dockerfile` defines the environment (e.g., `FROM node:12.16.3`, `WORKDIR /code`, `RUN npm install`).
A `docker-compose.yml` file is used to orchestrate multi-container applications (e.g., defining an `app` service and an `nginx` reverse proxy service, mapping ports, and mounting volumes).

## Docker Bridge Networking and Port Mapping
Containers have their own internal IP address (e.g., `10.0.0.8:80`).
By using port mapping (`-p 8080:80`), you map the Docker host's port (`8080`) to the Container's port (`80`) via a Docker Bridge, allowing external access to the containerized application.
