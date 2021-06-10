# TP2 Distribuidos: Middlewares y coordinacion de procesos

Para correrlo se necesita:

1) Bajarse los csv del kaggle https://www.kaggle.com/ezetowers/aoe2-tp2-draft

2) `pip install -r requirements.txt`

3) `python3 docker_compose.py CANT_REDUCER CANT_JOINERS CANT_FILTERS`

4) `make up`

5) `make logs`

6) en otra terminal: `python3 client.py LINEAS_A_PROCESAR LINEAS_A_MANDAR_POR_VEZ`

Para correr los tests:

Se debe tener levantado el sistema y en la carpeta tests correr:

`python3 test_1.py` o test_2.py o test_3_4.py

Recordar que entre corrida y corrida se debe bajar el sistema y volver a levantar

Cosas a mejorar del tp que no se hicieron por el tiempo:

- Un diseño con clases y no todo en el main de cada proceso
- Evitar la repeticion de codigo entre algunos filtros que se podria haber unificado
- Agregar la parametrizacion en todo los nodos
- Automatizar mejor los tests
- Gracefull quit del sistema cuando termina de procesar
- Uso de fanout y routing_key (capaz)
- Agregar mas diagramas
- Agregar replicacion en los filtros que se podia
- Mejorar script de generacion de docker-compose.yml

