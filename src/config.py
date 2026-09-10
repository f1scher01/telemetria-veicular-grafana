"""
Configurações e Parâmetros de Execução do Sistema de Telemetria.
"""

import os

# Configurações do InfluxDB 2.x
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "telemetria-super-secret-token-maua-2026")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "maua_racing")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "telemetria")

# Parâmetros de Simulação
SAMPLING_RATE_HZ = int(os.getenv("SAMPLING_RATE_HZ", "10"))  # 10 amostras por segundo
VEHICLE_ID = os.getenv("VEHICLE_ID", "Carro_01_Formula_Maua")
CIRCUIT_NAME = "Autodromo_Jose_Carlos_Pace_Interlagos"

# Coordenadas Base do Autódromo de Interlagos (São Paulo - SP)
INTERLAGOS_SECTORS = [
    {"name": "Reta dos Boxes",      "lat": -23.70110, "lon": -46.69720, "speed_target": 235, "gear": 6},
    {"name": "S do Senna 1",       "lat": -23.70320, "lon": -46.69610, "speed_target": 115, "gear": 3},
    {"name": "S do Senna 2",       "lat": -23.70420, "lon": -46.69580, "speed_target": 130, "gear": 3},
    {"name": "Curva do Sol",       "lat": -23.70580, "lon": -46.69680, "speed_target": 175, "gear": 4},
    {"name": "Reta Oposta",        "lat": -23.70750, "lon": -46.69980, "speed_target": 248, "gear": 6},
    {"name": "Curva do Lago",      "lat": -23.70610, "lon": -46.70250, "speed_target": 140, "gear": 3},
    {"name": "Ferradura",          "lat": -23.70400, "lon": -46.70380, "speed_target": 165, "gear": 4},
    {"name": "Laranjinha",         "lat": -23.70280, "lon": -46.70320, "speed_target": 120, "gear": 3},
    {"name": "S do Pinheirinho",   "lat": -23.70350, "lon": -46.70150, "speed_target": 95,  "gear": 2},
    {"name": "Bico de Pato",       "lat": -23.70460, "lon": -46.70080, "speed_target": 78,  "gear": 2},
    {"name": "Mergulho",           "lat": -23.70380, "lon": -46.69950, "speed_target": 185, "gear": 4},
    {"name": "Junção",             "lat": -23.70220, "lon": -46.69870, "speed_target": 110, "gear": 3},
    {"name": "Subida dos Boxes",   "lat": -23.70140, "lon": -46.69780, "speed_target": 205, "gear": 5}
]
