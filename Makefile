SHELL := /bin/bash
PWD := $(shell pwd)


default: build

all:

consumer:
	docker build -f ./consumer/Dockerfile -t "consumer:latest" .
.PHONY: consumer

producer:
	docker build -f ./producer/Dockerfile -t "producer:latest" .
.PHONY: producer

docker-image:
	docker build -f ./producer/Dockerfile -t "producer:latest" .
	docker build -f ./consumer/Dockerfile -t "consumer:latest" .
.PHONY: docker-image

up: docker-image
	docker-compose up -d --build
.PHONY: up

down:
	docker-compose stop -t 1
	docker-compose down
.PHONY: down

logs:
	docker-compose logs -f
.PHONY: logs
