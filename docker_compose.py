import sys

BASE_COMPOSE = """
version: '3'
services:
  rabbitmq:
    build:
      context: ./rabbitmq
      dockerfile: rabbitmq.dockerfile
    ports:
      - 15672:15672
      - 5672:5672
    healthcheck:
        test: ["CMD", "curl", "-f", "http://localhost:15672"]
        interval: 10s
        timeout: 5s
        retries: 10

  matches_spliter:
    container_name: matches_spliter
    image: matches_spliter:latest
    entrypoint: python3 /main.py
    restart: on-failure
    depends_on:
      - rabbitmq
    links: 
      - rabbitmq
    environment:
      - PYTHONUNBUFFERED=1

  ladder_filter:
    container_name: ladder_filter
    image: ladder_filter:latest
    entrypoint: python3 /main.py
    restart: on-failure
    depends_on:
      - rabbitmq
    links: 
      - rabbitmq
    environment:
      - PYTHONUNBUFFERED=1

  servers_avg_rating_duration:
    container_name: servers_avg_rating_duration
    image: servers_avg_rating_duration:latest
    entrypoint: python3 /main.py
    restart: on-failure
    depends_on:
      - rabbitmq
    links: 
      - rabbitmq
    environment:
      - PYTHONUNBUFFERED=1

  players_clone_rating_filter:
    container_name: players_clone_rating_filter
    image: players_clone_rating_filter:latest
    entrypoint: python3 /main.py
    restart: on-failure
    depends_on:
      - rabbitmq
    links: 
      - rabbitmq
    environment:
      - PYTHONUNBUFFERED=1

  join_controller_3:
    container_name: join_controller_3
    image: join_controller:latest
    entrypoint: python3 /main.py
    restart: on-failure
    depends_on:
      - rabbitmq
    links: 
      - rabbitmq
    environment:
      - PYTHONUNBUFFERED=1
      - K_JOINERS=%d
      - LEFT_INPUT_QUEUE=1v1_arena_matches
      - RIGHT_INPUT_QUEUE=players_clone_2
      - OUTPUT_QUEUES_SUFFIX=match_players_joiner_
      - LEFT_BY=token
      - RIGHT_BY=match

  <JOINERS>
      

  groupby_match_controller:
    container_name: groupby_match_controller
    image: groupby_match_controller:latest
    entrypoint: python3 /main.py
    restart: on-failure
    depends_on:
      - rabbitmq
    links: 
      - rabbitmq
    environment:
      - PYTHONUNBUFFERED=1
      - K_REDUCERS=%d

  <GROUPBY_MATCH_REDUCERS>
    
  winner_vs_loser_filter:
    container_name: winner_vs_loser_filter
    image: winner_vs_loser_filter:latest
    entrypoint: python3 /main.py
    restart: on-failure
    depends_on:
      - rabbitmq
    links: 
      - rabbitmq
    environment:
      - PYTHONUNBUFFERED=1
      - INPUT_QUEUE=1v1_players
      - OUTPUT_QUEUE=2
    
  arena_filter:
    container_name: arena_filter
    image: map_no_mirror_filter:latest
    entrypoint: python3 /main.py
    restart: on-failure
    depends_on:
      - rabbitmq
    links: 
      - rabbitmq
    environment:
      - PYTHONUNBUFFERED=1
      - INPUT_QUEUE=1v1_matches
      - OUTPUT_QUEUE=1v1_arena_matches
      - MAP=arena
      - NO_MIRROR=true

  islands_filter:
    container_name: islands_filter
    image: map_no_mirror_filter:latest
    entrypoint: python3 /main.py
    restart: on-failure
    depends_on:
      - rabbitmq
    links: 
      - rabbitmq
    environment:
      - PYTHONUNBUFFERED=1
      - INPUT_QUEUE=team_matches
      - OUTPUT_QUEUE=team_islands_matches
      - MAP=islands
      - NO_MIRROR=null
"""

GROUPBY_MATCH_REDUCER_FORMAT = """

  groupby_match_reducer_%d:
    container_name: groupby_match_reducer_%d
    image: groupby_match_reducer:latest
    entrypoint: python3 /main.py
    restart: on-failure
    depends_on:
      - rabbitmq
    links: 
      - rabbitmq
    environment:
      - PYTHONUNBUFFERED=1
      - INPUT_QUEUE=players_reducer_%d
      - OUTPUT_QUEUE=1v1_players

"""

JOINERS_FORMAT = """

  joiner_%d:
    container_name: joiner_%d
    image: joiner:latest
    entrypoint: python3 /main.py
    restart: on-failure
    depends_on:
      - rabbitmq
    links: 
      - rabbitmq
    environment:
      - PYTHONUNBUFFERED=1
      - INPUT_QUEUE=match_players_joiner_%d
      - OUTPUT_QUEUE=joined_players_matches
      - LEFT_BY=token
      - RIGHT_BY=match

"""

def main():
    groupby_match_reducers = int(sys.argv[1])
    joiners = int(sys.argv[2])

    reducers_section = ""
    for i in range(groupby_match_reducers):
        reducers_section += GROUPBY_MATCH_REDUCER_FORMAT % (i, i, i)

    joiners_section = ""
    for i in range(joiners):
        joiners_section += JOINERS_FORMAT % (i, i, i)

    base = BASE_COMPOSE % (joiners, groupby_match_reducers)
    compose = base.replace("<GROUPBY_MATCH_REDUCERS>", reducers_section).replace("<JOINERS>", joiners_section)

    with open("docker-compose.yml", "w") as compose_file:
        compose_file.write(compose)

if __name__ == "__main__":
    main()