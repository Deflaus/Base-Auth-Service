# Base-Auth-Service

Base of FastAPI microservice for authentication

![alt text](https://img.shields.io/badge/python-3.10.8-green)

## Technology stack

1. FastAPI
2. PostgreSQL
3. Redis
4. Docker-compose

## Run

#### Run local environment stack
```shell
docker-compose up -d --build
```

#### Install poetry
```shell
pip install poetry
```
 
#### Install the project dependencies
```shell
cd src && poetry install
```

#### Spawn a shell within the virtual environment
```shell
poetry shell
```

#### Run the server
```shell
uvicorn main:app --reload
```