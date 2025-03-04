
# Simple Map Demo with Encore

## Run backend 

```docker run -e PORT=8081 -p 8081:8081 encoredemo```

## Build Image:

```docker compose up --build```

## Build and Run frontend

```
docker build -t frontend

docker run frontend
```

## Docker compose

```

docker compose up --build

docker compose -f docker-compose.yml up

```

## Save Docker Image

```
 docker save -o encoredemo.tar encoredemo:latest 

docker load -i encoredemo.tar
  ```
