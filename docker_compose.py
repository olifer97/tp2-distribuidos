import sys

BASE = """
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

  <JOINERS_3>

  join_controller_4:
    container_name: join_controller_4
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
      - LEFT_INPUT_QUEUE=team_islands_matches
      - RIGHT_INPUT_QUEUE=players_greater_2000
      - OUTPUT_QUEUES_SUFFIX=match_proplayers_joiner_
      - LEFT_BY=token
      - RIGHT_BY=match

  <JOINERS_4>      

  groupby_match_controller:
    container_name: groupby_match_controller
    image: groupby_controller:latest
    entrypoint: python3 /main.py
    restart: on-failure
    depends_on:
      - rabbitmq
    links: 
      - rabbitmq
    environment:
      - PYTHONUNBUFFERED=1
      - K_REDUCERS=%d
      - INPUT_QUEUE=players_clone_1
      - OUTPUT_QUEUES_SUFFIX=players_reducer_
      - GROUP_BY=match
      - SENTINELS=1

  <GROUPBY_MATCH_REDUCERS>

  groupby_civ_controller_3:
    container_name: groupby_civ_controller_3
    image: groupby_controller:latest
    entrypoint: python3 /main.py
    restart: on-failure
    depends_on:
      - rabbitmq
    links: 
      - rabbitmq
    environment:
      - PYTHONUNBUFFERED=1
      - K_REDUCERS=%d
      - INPUT_QUEUE=joined_players_matches
      - OUTPUT_QUEUES_SUFFIX=civ_type3_reducer_
      - GROUP_BY=civ
      - SENTINELS=%d
  
  <GROUPBY_CIV_REDUCERS_3>

  groupby_civ_controller_4:
    container_name: groupby_civ_controller_4
    image: groupby_controller:latest
    entrypoint: python3 /main.py
    restart: on-failure
    depends_on:
      - rabbitmq
    links: 
      - rabbitmq
    environment:
      - PYTHONUNBUFFERED=1
      - K_REDUCERS=%d
      - INPUT_QUEUE=joined_proplayers_matches
      - OUTPUT_QUEUES_SUFFIX=civ_type4_reducer_
      - GROUP_BY=civ
      - SENTINELS=%d
  
  <GROUPBY_CIV_REDUCERS_4>
    
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
      - SENTINELS=%d
    
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

  winner_filter_percentage_calculator:
    container_name: winner_filter_percentage_calculator
    image: winner_filter_percentage_calculator:latest
    entrypoint: python3 /main.py
    restart: on-failure
    depends_on:
      - rabbitmq
    links: 
      - rabbitmq
    environment:
      - PYTHONUNBUFFERED=1
      - INPUT_QUEUE=groupby_civ_3
      - OUTPUT_QUEUE=3
      - SENTINELS=%d

  top_civilizations:
    container_name: top_civilizations
    image: top_civilizations:latest
    entrypoint: python3 /main.py
    restart: on-failure
    depends_on:
      - rabbitmq
    links: 
      - rabbitmq
    environment:
      - PYTHONUNBUFFERED=1
      - INPUT_QUEUE=groupby_civ_4
      - OUTPUT_QUEUE=4
      - TOP_N=5
      - SENTINELS=%d
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

GROUPBY_CIV_REDUCER_FORMAT = """

  groupby_civ_reducer_type%d_%d:
    container_name: groupby_civ_reducer_type%d_%d
    image: groupby_civ_reducer:latest
    entrypoint: python3 /main.py
    restart: on-failure
    depends_on:
      - rabbitmq
    links: 
      - rabbitmq
    environment:
      - PYTHONUNBUFFERED=1
      - INPUT_QUEUE=%s 
      - OUTPUT_QUEUE=%s
      - GROUP_BY=civ

"""

JOINERS_FORMAT = """

  joiner_type%d_%d:
    container_name: joiner_type%d_%d
    image: joiner:latest
    entrypoint: python3 /main.py
    restart: on-failure
    depends_on:
      - rabbitmq
    links: 
      - rabbitmq
    environment:
      - PYTHONUNBUFFERED=1
      - INPUT_QUEUE=%s 
      - OUTPUT_QUEUE=%s
      - LEFT_BY=token
      - RIGHT_BY=match

"""

def main():
    reducers = int(sys.argv[1])
    joiners = int(sys.argv[2])

    reducers_section = ""
    for i in range(reducers):
        reducers_section += GROUPBY_MATCH_REDUCER_FORMAT % (i, i, i)

    joiners3_section = ""
    for i in range(joiners):
        joiners3_section += JOINERS_FORMAT % (3,i,3, i, "match_players_joiner_{}".format(i), "joined_players_matches")

    joiners4_section = ""
    for i in range(joiners):
        joiners4_section += JOINERS_FORMAT % (4,i,4, i, "match_proplayers_joiner_{}".format(i), "joined_proplayers_matches")

    reducers3_section = ""
    for i in range(reducers):
        reducers3_section += GROUPBY_CIV_REDUCER_FORMAT % (3,i,3, i, "civ_type3_reducer_{}".format(i), "groupby_civ_3")

    reducers4_section = ""
    for i in range(reducers):
        reducers4_section += GROUPBY_CIV_REDUCER_FORMAT % (4,i,4, i, "civ_type4_reducer_{}".format(i), "groupby_civ_4")

    base = BASE % (joiners, joiners, reducers, reducers, joiners, reducers, joiners,reducers, reducers, reducers)
    compose = base.replace("<GROUPBY_MATCH_REDUCERS>", reducers_section) \
                  .replace("<JOINERS_3>", joiners3_section) \
                  .replace("<JOINERS_4>", joiners4_section) \
                  .replace("<GROUPBY_CIV_REDUCERS_3>", reducers3_section) \
                  .replace("<GROUPBY_CIV_REDUCERS_4>", reducers4_section) \

    with open("docker-compose.yml", "w") as compose_file:
        compose_file.write(compose)

if __name__ == "__main__":
    main()