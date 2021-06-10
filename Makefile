SHELL := /bin/bash
PWD := $(shell pwd)


default: build

all:

broadcasters:
	docker build -f ./broadcasters/matches_spliter/Dockerfile -t "matches_spliter:latest" .
	docker build -f ./broadcasters/players_clone_rating_filter/Dockerfile -t "players_clone_rating_filter:latest" .
.PHONY: broadcasters

filters:
	docker build -f ./filters/ladder_filter/Dockerfile -t "ladder_filter:latest" .
	docker build -f ./filters/servers_avg_rating_duration/Dockerfile -t "servers_avg_rating_duration:latest" .
	docker build -f ./filters/winner_vs_loser_filter/Dockerfile -t "winner_vs_loser_filter:latest" .
	docker build -f ./filters/map_no_mirror_filter/Dockerfile -t "map_no_mirror_filter:latest" .
.PHONY: filters

groupby:
	docker build -f ./groupby/groupby_controller/Dockerfile -t "groupby_controller:latest" .
	docker build -f ./groupby/groupby_match_reducer/Dockerfile -t "groupby_match_reducer:latest" .
	docker build -f ./groupby/groupby_civ_reducer/Dockerfile -t "groupby_civ_reducer:latest" .
.PHONY: groupby

join:
	docker build -f ./join/join_controller/Dockerfile -t "join_controller:latest" .
	docker build -f ./join/joiner/Dockerfile -t "joiner:latest" .
.PHONY: join

calculators:
	docker build -f ./calculators//winner_filter_percentage_calculator/Dockerfile -t "winner_filter_percentage_calculator:latest" .
	docker build -f ./calculators/top_civilizations/Dockerfile -t "top_civilizations:latest" .
.PHONY: calculators

image:
	make filters
	make broadcasters
	make groupby
	make calculators
	make join
.PHONY: image

up: image
	docker-compose up -d --build
.PHONY: up

down:
	docker-compose stop -t 1
	docker-compose down
.PHONY: down

logs:
	docker-compose logs -f
.PHONY: logs
