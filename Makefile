SHELL := /bin/bash
PWD := $(shell pwd)


default: build

all:

ladder_filter:
	docker build -f ./ladder_filter/Dockerfile -t "ladder_filter:latest" .
.PHONY: ladder_filter

matches_spliter:
	docker build -f ./matches_spliter/Dockerfile -t "matches_spliter:latest" .
.PHONY: matches_spliter

servers_avg_rating_duration:
	docker build -f ./servers_avg_rating_duration/Dockerfile -t "servers_avg_rating_duration:latest" .
.PHONY: ladder_filter

docker-image:
	docker build -f ./matches_spliter/Dockerfile -t "matches_spliter:latest" .
	docker build -f ./ladder_filter/Dockerfile -t "ladder_filter:latest" .
	docker build -f ./servers_avg_rating_duration/Dockerfile -t "servers_avg_rating_duration:latest" .
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
