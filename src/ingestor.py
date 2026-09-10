"""
Ingestor de Telemetria Veicular para o InfluxDB 2.x.
Transmite dados de sensores mecânicos e GPS em tempo real ou em lote.
"""

import time
import sys
import argparse
from datetime import datetime, timezone, timedelta

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

try:
    from influxdb_client import InfluxDBClient, Point, WritePrecision
    from influxdb_client.client.write_api import SYNCHRONOUS
    INFLUX_AVAILABLE = True
except ImportError:
    INFLUX_AVAILABLE = False

from .config import (
    INFLUXDB_URL,
    INFLUXDB_TOKEN,
    INFLUXDB_ORG,
    INFLUXDB_BUCKET,
    SAMPLING_RATE_HZ,
    VEHICLE_ID,
    CIRCUIT_NAME
)
from .simulator import TelemetrySimulator


def create_influx_points(data_point: dict, point_time=None) -> list:
    """Converte um snapshot de telemetria em objetos Point do InfluxDB."""
    ts = point_time or datetime.now(timezone.utc)
    
    # 1. Ponto de Motor / Termodinâmica
    p_motor = Point("motor") \
        .tag("veiculo", data_point["vehicle_id"]) \
        .tag("circuito", data_point["circuit"]) \
        .tag("setor", data_point["sector"]) \
        .tag("volta", str(data_point["lap"])) \
        .field("rpm", int(data_point["rpm"])) \
        .field("pressao_oleo_bar", float(data_point["oil_pressure_bar"])) \
        .field("temp_oleo_c", float(data_point["oil_temp_c"])) \
        .field("temp_agua_c", float(data_point["coolant_temp_c"])) \
        .time(ts, WritePrecision.NS)

    # 2. Ponto de Dinâmica Veicular
    p_dinamica = Point("dinamica") \
        .tag("veiculo", data_point["vehicle_id"]) \
        .tag("circuito", data_point["circuit"]) \
        .field("velocidade_kmh", float(data_point["speed_kmh"])) \
        .field("marcha", int(data_point["gear"])) \
        .field("tps_percent", float(data_point["tps_percent"])) \
        .field("freio_bar", float(data_point["brake_bar"])) \
        .field("g_lat", float(data_point["g_lat"])) \
        .field("g_long", float(data_point["g_long"])) \
        .time(ts, WritePrecision.NS)

    # 3. Ponto de Geolocalização GPS
    p_gps = Point("gps") \
        .tag("veiculo", data_point["vehicle_id"]) \
        .tag("circuito", data_point["circuit"]) \
        .field("latitude", float(data_point["latitude"])) \
        .field("longitude", float(data_point["longitude"])) \
        .field("altitude_m", float(data_point["altitude_m"])) \
        .field("velocidade_kmh", float(data_point["speed_kmh"])) \
        .time(ts, WritePrecision.NS)

    return [p_motor, p_dinamica, p_gps]


def run_live_stream(rate_hz: int = SAMPLING_RATE_HZ, max_points: int = 0):
    """Executa o streaming contínuo em tempo real para o InfluxDB."""
    if not INFLUX_AVAILABLE:
        print("⚠️ Pacote 'influxdb-client' não encontrado. Instale com: pip install influxdb-client")
        return

    print(f"🚀 Conectando ao InfluxDB em: {INFLUXDB_URL}")
    print(f"   Organização: {INFLUXDB_ORG} | Bucket: {INFLUXDB_BUCKET}")
    print(f"   Frequência de amostragem: {rate_hz} Hz ({1000 / rate_hz:.0f} ms)")
    
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    simulator = TelemetrySimulator(sample_rate_hz=rate_hz)
    
    count = 0
    sleep_interval = 1.0 / rate_hz
    
    try:
        while True:
            data = simulator.step()
            points = create_influx_points(data)
            write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=points)
            
            count += 1
            if count % rate_hz == 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Pista: {data['sector']} | Vel: {data['speed_kmh']} km/h | RPM: {data['rpm']} | P.Óleo: {data['oil_pressure_bar']} bar | T.Óleo: {data['oil_temp_c']}°C")
                
            if max_points > 0 and count >= max_points:
                break
                
            time.sleep(sleep_interval)
    except KeyboardInterrupt:
        print("\n⏹️ Transmissão interrompida pelo usuário.")
    finally:
        client.close()
        print("Conexão fechada com sucesso.")


def run_backfill(points_count: int = 1500, rate_hz: int = SAMPLING_RATE_HZ):
    """Gera e envia dados históricos das últimas voltas para popular o dashboard imediatamente."""
    if not INFLUX_AVAILABLE:
        print("⚠️ Pacote 'influxdb-client' não encontrado. Instale com: pip install influxdb-client")
        return

    print(f"📥 Carregando histórico de {points_count} amostras no InfluxDB...")
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    simulator = TelemetrySimulator(sample_rate_hz=rate_hz)
    
    now = datetime.now(timezone.utc)
    dt = timedelta(seconds=1.0 / rate_hz)
    start_time = now - (dt * points_count)
    
    batch = []
    for i in range(points_count):
        pt_time = start_time + (dt * i)
        data = simulator.step()
        batch.extend(create_influx_points(data, point_time=pt_time))
        
        # Envia em blocos de 300 pontos
        if len(batch) >= 300:
            write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=batch)
            batch = []
            
    if batch:
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=batch)
        
    client.close()
    print(f"✅ Carga inicial de {points_count} pontos concluída! Abra o Grafana para visualizar os gráficos.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingestor de Telemetria Veicular IMT")
    parser.add_argument("--mode", choices=["stream", "backfill"], default="stream", help="Modo de operação: stream (tempo real) ou backfill (histórico)")
    parser.add_argument("--points", type=int, default=1500, help="Quantidade de pontos para o modo backfill")
    args = parser.parse_args()
    
    if args.mode == "backfill":
        run_backfill(points_count=args.points)
    else:
        run_live_stream()
