"""
Configurações e parâmetros de execução do simulador de telemetria.
"""

import os

# InfluxDB 2.x (valores de desenvolvimento local, os mesmos do docker-compose.yml)
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "telemetria-super-secret-token-2026")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "telemetria_org")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "telemetria")

# Simulação
SAMPLING_RATE_HZ = int(os.getenv("SAMPLING_RATE_HZ", "10"))
VEHICLE_ID = os.getenv("VEHICLE_ID", "veiculo_simulado_01")
CIRCUIT_NAME = "Autodromo_Jose_Carlos_Pace_Interlagos"
GRAVIDADE = 9.80665  # m/s²

# Traçado de Interlagos dividido em 13 setores, no sentido anti-horário da corrida.
#
# lat/lon       ponto inicial do setor (referência aproximada do traçado público)
# comprimento_m extensão do setor; a soma fecha os 4.309 m oficiais do circuito
# raio_m        raio médio da curva, estimado para ordem de grandeza (None em reta)
# sentido       +1 curva à esquerda, -1 curva à direita (sinal do G lateral)
# speed_target  velocidade-alvo no setor (km/h) e gear, a marcha usada nele
#
# Comprimentos e raios são estimativas, não levantamento topográfico. Servem para
# que tempo de volta e aceleração lateral saiam da física (distância/velocidade e
# v²/R) em vez de constantes escolhidas à mão.
INTERLAGOS_SECTORS = [
    {"name": "Reta dos Boxes",    "lat": -23.70110, "lon": -46.69720, "comprimento_m": 350, "raio_m": None, "sentido": 0,  "speed_target": 235, "gear": 6},
    {"name": "S do Senna 1",      "lat": -23.70320, "lon": -46.69610, "comprimento_m": 150, "raio_m": 55,   "sentido": 1,  "speed_target": 115, "gear": 3},
    {"name": "S do Senna 2",      "lat": -23.70420, "lon": -46.69580, "comprimento_m": 200, "raio_m": 70,   "sentido": -1, "speed_target": 130, "gear": 3},
    {"name": "Curva do Sol",      "lat": -23.70580, "lon": -46.69680, "comprimento_m": 350, "raio_m": 130,  "sentido": 1,  "speed_target": 175, "gear": 4},
    {"name": "Reta Oposta",       "lat": -23.70750, "lon": -46.69980, "comprimento_m": 650, "raio_m": None, "sentido": 0,  "speed_target": 248, "gear": 6},
    {"name": "Curva do Lago",     "lat": -23.70610, "lon": -46.70250, "comprimento_m": 300, "raio_m": 90,   "sentido": -1, "speed_target": 140, "gear": 3},
    {"name": "Ferradura",         "lat": -23.70400, "lon": -46.70380, "comprimento_m": 300, "raio_m": 110,  "sentido": -1, "speed_target": 165, "gear": 4},
    {"name": "Laranjinha",        "lat": -23.70280, "lon": -46.70320, "comprimento_m": 200, "raio_m": 60,   "sentido": -1, "speed_target": 120, "gear": 3},
    {"name": "S do Pinheirinho",  "lat": -23.70350, "lon": -46.70150, "comprimento_m": 250, "raio_m": 40,   "sentido": 1,  "speed_target": 95,  "gear": 2},
    {"name": "Bico de Pato",      "lat": -23.70460, "lon": -46.70080, "comprimento_m": 200, "raio_m": 28,   "sentido": -1, "speed_target": 78,  "gear": 2},
    {"name": "Mergulho",          "lat": -23.70380, "lon": -46.69950, "comprimento_m": 300, "raio_m": 150,  "sentido": 1,  "speed_target": 185, "gear": 4},
    {"name": "Junção",            "lat": -23.70220, "lon": -46.69870, "comprimento_m": 250, "raio_m": 55,   "sentido": 1,  "speed_target": 110, "gear": 3},
    {"name": "Subida dos Boxes",  "lat": -23.70140, "lon": -46.69780, "comprimento_m": 809, "raio_m": None, "sentido": 0,  "speed_target": 205, "gear": 5},
]
