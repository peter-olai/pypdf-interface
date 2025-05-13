# PDF Tools - Docker Setup

This document explains how to build and run the PDF Tools application using Docker.

## Prerequisites

- Docker installed on your system. If you don't have Docker installed, please visit [Docker's official website](https://www.docker.com/get-started) to download and install it.
- Docker Compose is recommended and usually comes with Docker Desktop installations.

## Option 1: Using Docker Compose (Recommended)

If you have Docker Compose installed, the setup is very simple:

1. Open a terminal/command prompt
2. Navigate to the project directory (where the docker-compose.yml file is located)
3. Run the following command:

```
docker-compose up
```

This will build the image and start the container. The application will be accessible at http://localhost:5000.

To stop the application, press Ctrl+C in the terminal or run:

```
docker-compose down
```

## Option 2: Using Docker Commands

### Building the Docker Image

1. Open a terminal/command prompt
2. Navigate to the project directory (where the Dockerfile is located)
3. Run the following command to build the Docker image:

```
docker build -t pdf-tools .
```

This will create a Docker image named "pdf-tools" using the instructions in the Dockerfile.

### Running the Docker Container

After successfully building the image, you can run the application in a Docker container:

```
docker run -p 5000:5000 pdf-tools
```

This command:
- Creates and starts a container from the "pdf-tools" image
- Maps port 5000 of the container to port 5000 on your host machine
- The application will be accessible at http://localhost:5000

### Stopping the Container

To stop the running container:

1. Find the container ID using `docker ps`
2. Run `docker stop [CONTAINER_ID]`

## Additional Notes

- The container includes all necessary dependencies to run the PDF Tools application
- Files uploaded to the application are stored temporarily within the container
- If you make changes to the code, you'll need to rebuild the Docker image

## Troubleshooting

If you encounter any issues:

1. Make sure ports are not already in use
2. Check Docker logs using `docker logs [CONTAINER_ID]`
3. Verify that your Docker installation is working properly with `docker info`
