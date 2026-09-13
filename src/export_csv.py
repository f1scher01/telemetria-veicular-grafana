"""
Exportação de uma volta simulada completa para CSV e para o cockpit web.

A primeira volta serve de aquecimento (a simulação começa em regime arbitrário,
com 180 km/h e óleo a 92 °C). A segunda volta, já em regime, é gravada inteira:
    data/sample_lap_interlagos.csv   usada por generate_preview.py
    telemetry_data.js e web/telemetry_data.js   usados pelo cockpit index.html

Uso:
    python -m src.export_csv
"""

import csv
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from .simulator import TelemetrySimulator

VOLTA_GRAVADA = 2


def simular_volta(sample_rate_hz: int = 10):
    sim = TelemetrySimulator(sample_rate_hz=sample_rate_hz)
    volta = []
    while True:
        amostra = sim.step()
        if amostra["lap"] == VOLTA_GRAVADA:
            volta.append(amostra)
        elif amostra["lap"] > VOLTA_GRAVADA:
            return volta, amostra["last_lap_time_s"]


def export_sample_data(csv_path: str = "data/sample_lap_interlagos.csv"):
    volta, tempo_volta = simular_volta()
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=volta[0].keys())
        writer.writeheader()
        writer.writerows(volta)

    conteudo = "const TELEMETRY_DATA = " + json.dumps(volta, ensure_ascii=False) + ";\n"
    for destino in ("telemetry_data.js", os.path.join("web", "telemetry_data.js")):
        with open(destino, "w", encoding="utf-8") as f:
            f.write(conteudo)

    minutos, segundos = divmod(tempo_volta, 60)
    print(f"✅ Volta simulada {VOLTA_GRAVADA}: {len(volta)} amostras a 10 Hz, tempo {int(minutos)}:{segundos:06.3f}")
    print(f"   Velocidade máxima: {max(d['speed_kmh'] for d in volta)} km/h · pico de rotação: {max(d['rpm'] for d in volta)} rpm")
    print(f"   G lateral máximo: {max(abs(d['g_lat']) for d in volta):.2f} g · frenagem máxima: {min(d['g_long'] for d in volta):.2f} g")
    print(f"   Óleo: {min(d['oil_temp_c'] for d in volta):.1f} a {max(d['oil_temp_c'] for d in volta):.1f} °C, "
          f"{min(d['oil_pressure_bar'] for d in volta):.2f} a {max(d['oil_pressure_bar'] for d in volta):.2f} bar")
    print(f"   Arquivos: {csv_path}, telemetry_data.js, web/telemetry_data.js")


if __name__ == "__main__":
    export_sample_data()
