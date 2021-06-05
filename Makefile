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
.PHONY: servers_avg_rating_duration

players_clone_rating_filter:
	docker build -f ./players_clone_rating_filter/Dockerfile -t "players_clone_rating_filter:latest" .
.PHONY: players_clone_rating_filter

groupby_match_controller:
	docker build -f ./groupby_match_controller/Dockerfile -t "groupby_match_controller:latest" .
.PHONY: groupby_match_controller

groupby_match_reducer:
	docker build -f ./groupby_match_controller/Dockerfile -t "groupby_match_reducer:latest" .
.PHONY: groupby_match_reducer

winner_vs_loser_filter:
	docker build -f ./winner_vs_loser_filter/Dockerfile -t "winner_vs_loser_filter:latest" .
.PHONY: winner_vs_loser_filter

map_no_mirror_filter:
	docker build -f ./map_no_mirror_filter/Dockerfile -t "map_no_mirror_filter:latest" .
.PHONY: map_no_mirror_filter

docker-image:
	docker build -f ./matches_spliter/Dockerfile -t "matches_spliter:latest" .
	docker build -f ./ladder_filter/Dockerfile -t "ladder_filter:latest" .
	docker build -f ./players_clone_rating_filter/Dockerfile -t "players_clone_rating_filter:latest" .
	docker build -f ./servers_avg_rating_duration/Dockerfile -t "servers_avg_rating_duration:latest" .
	docker build -f ./groupby_match_controller/Dockerfile -t "groupby_match_controller:latest" .
	docker build -f ./groupby_match_reducer/Dockerfile -t "groupby_match_reducer:latest" .
	docker build -f ./winner_vs_loser_filter/Dockerfile -t "winner_vs_loser_filter:latest" .
	docker build -f ./map_no_mirror_filter/Dockerfile -t "map_no_mirror_filter:latest" .
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
