"""
Script de Exportação de Dados de Telemetria para CSV.
Gera arquivos de sessão de volta rápida no Autódromo de Interlagos para testes estáticos e validações.
"""

import os
import sys
import csv
from datetime import datetime, timezone

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from .simulator import TelemetrySimulator


def export_sample_data(output_path: str = "data/sample_lap_interlagos.csv", points: int = 1600):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    sim = TelemetrySimulator(sample_rate_hz=10)
    
    print(f"🏎️ Simulando volta rápida no Autódromo de Interlagos ({points} amostras a 10 Hz)...")
    dataset = sim.generate_lap_dataset(points)
    
    if not dataset:
        print("Erro: Nenhum dado foi gerado.")
        return
        
    keys = dataset[0].keys()
    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(dataset)
        
    print(f"✅ Arquivo de telemetria gerado com sucesso em: {output_path}")
    print(f"   Voltas completadas: {dataset[-1]['lap']}")
    print(f"   Velocidade máxima: {max(d['speed_kmh'] for d in dataset)} km/h")
    print(f"   Pico de RPM: {max(d['rpm'] for d in dataset)} RPM")
    print(f"   Faixa de Pressão de Óleo: {min(d['oil_pressure_bar'] for d in dataset):.2f} a {max(d['oil_pressure_bar'] for d in dataset):.2f} bar")
    print(f"   Faixa de Temperatura de Óleo: {min(d['oil_temp_c'] for d in dataset):.1f}°C a {max(d['oil_temp_c'] for d in dataset):.1f}°C")


if __name__ == "__main__":
    export_sample_data()
