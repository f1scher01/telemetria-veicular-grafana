"""
Simulador de cinemática e termodinâmica veicular sobre o traçado de Interlagos.

Todas as séries são SINTÉTICAS. O modelo existe para gerar sinais fisicamente
coerentes entre si, de modo que o pipeline de ingestão e visualização trabalhe com
dados que se comportam como telemetria real:

    posição      avanço por distância percorrida, s += v·dt, setor a setor
    longitudinal a velocidade persegue a velocidade-alvo do setor com limites de
                 aceleração (5 m/s²) e frenagem (12,5 m/s²); G_long = Δv / (dt·g)
    lateral      G_lat = v² / (R·g) nas curvas, com o raio médio do setor
    motor        rotação proporcional à velocidade na marcha do setor
    óleo e água  resposta de primeira ordem à carga, dT/dt = (T_eq − T) / τ
    lubrificação pressão crescente com a rotação, reduzida pela perda de viscosidade
                 do óleo quente e limitada pela válvula de alívio
"""

import math
import random
from datetime import datetime, timezone
from typing import Any, Dict, List

from .config import CIRCUIT_NAME, GRAVIDADE, INTERLAGOS_SECTORS, SAMPLING_RATE_HZ, VEHICLE_ID

ACELERACAO_MAX = 5.0        # m/s², tração
DESACELERACAO_MAX = 12.5    # m/s², frenagem
VELOCIDADE_TOPO_MARCHA = {1: 50, 2: 85, 3: 135, 4: 180, 5: 225, 6: 270}  # km/h a 11.800 rpm
TAU_OLEO_S, TAU_AGUA_S = 45.0, 30.0
PRESSAO_ALIVIO_BAR = 5.9


class TelemetrySimulator:
    def __init__(self, sample_rate_hz: int = SAMPLING_RATE_HZ, semente: int | None = 42):
        self.rng = random.Random(semente)
        self.sample_rate = sample_rate_hz
        self.dt = 1.0 / sample_rate_hz
        self.sectors = INTERLAGOS_SECTORS

        self.speed = 180.0          # km/h
        self.rpm = 9200.0
        self.gear = 6
        self.tps = 85.0             # %
        self.brake_bar = 0.0
        self.g_lat = 0.0
        self.g_long = 0.0

        self.oil_temp = 92.0        # °C
        self.coolant_temp = 86.0    # °C
        self.oil_pressure = 4.8     # bar

        self.current_sector_idx = 0
        self.distance_in_sector_m = 0.0
        self.lap_number = 1
        self.lap_time_seconds = 0.0
        self.last_lap_time_s = None

    def _ruido(self, amplitude: float) -> float:
        return self.rng.uniform(-amplitude, amplitude)

    def step(self) -> Dict[str, Any]:
        """Avança um passo de tempo e devolve o snapshot de telemetria."""
        self.lap_time_seconds += self.dt

        # Posição: avanço pela distância percorrida no passo
        self.distance_in_sector_m += (self.speed / 3.6) * self.dt
        while self.distance_in_sector_m >= self.sectors[self.current_sector_idx]["comprimento_m"]:
            self.distance_in_sector_m -= self.sectors[self.current_sector_idx]["comprimento_m"]
            self.current_sector_idx = (self.current_sector_idx + 1) % len(self.sectors)
            if self.current_sector_idx == 0:
                self.last_lap_time_s = round(self.lap_time_seconds, 2)
                self.lap_number += 1
                self.lap_time_seconds = 0.0

        setor = self.sectors[self.current_sector_idx]
        proximo = self.sectors[(self.current_sector_idx + 1) % len(self.sectors)]
        t = self.distance_in_sector_m / setor["comprimento_m"]

        lat = setor["lat"] + (proximo["lat"] - setor["lat"]) * t + self._ruido(0.00002)
        lon = setor["lon"] + (proximo["lon"] - setor["lon"]) * t + self._ruido(0.00002)
        altitude = 760.0 + 18.0 * math.sin(self.current_sector_idx + t)

        # Dinâmica longitudinal
        velocidade_anterior = self.speed
        # A velocidade-alvo é a do setor. Se o próximo setor é mais lento, a transição
        # acontece só no fim: últimos 40% de uma reta ou últimos 50% de uma curva.
        alvo = setor["speed_target"]
        if proximo["speed_target"] < setor["speed_target"]:
            zona = 0.5 if setor["raio_m"] else 0.4
            fracao = max(0.0, (t - (1.0 - zona)) / zona)
            alvo += (proximo["speed_target"] - setor["speed_target"]) * fracao
        diferenca = alvo - self.speed
        if diferenca > 2.0:
            self.tps = min(100.0, 60.0 + diferenca * 2.0)
            self.brake_bar = 0.0
            self.speed += min(ACELERACAO_MAX * 3.6 * self.dt * self.tps / 100.0, diferenca)
        elif diferenca < -0.5:
            # pressão de freio proporcional ao erro de velocidade: acompanha a zona de
            # frenagem de forma contínua, sem pulsar entre freio e acelerador
            self.tps = 0.0
            self.brake_bar = min(85.0, 8.0 * abs(diferenca))
            self.speed -= min(DESACELERACAO_MAX * 3.6 * self.dt * self.brake_bar / 85.0, abs(diferenca))
        else:
            self.tps = 45.0 + self._ruido(5.0)
            self.brake_bar = 0.0
        self.speed = max(55.0, min(265.0, self.speed))
        self.g_long = ((self.speed - velocidade_anterior) / 3.6) / self.dt / GRAVIDADE + self._ruido(0.03)

        # Dinâmica lateral: G = v² / (R·g)
        v = self.speed / 3.6
        if setor["raio_m"]:
            self.g_lat = setor["sentido"] * min(2.5, v * v / (setor["raio_m"] * GRAVIDADE)) + self._ruido(0.05)
        else:
            self.g_lat = self._ruido(0.08)

        # Motor
        self.gear = setor["gear"]
        self.rpm = (self.speed / VELOCIDADE_TOPO_MARCHA[self.gear]) * 11800.0 + self._ruido(60.0)
        self.rpm = max(3800.0, min(12400.0, self.rpm))
        carga = (self.rpm / 12000.0) * (self.tps / 100.0)

        # Térmica de primeira ordem
        oleo_equilibrio = 90.0 + 28.0 * carga
        agua_equilibrio = 85.0 + 9.0 * carga
        self.oil_temp += (oleo_equilibrio - self.oil_temp) / TAU_OLEO_S * self.dt
        self.coolant_temp += (agua_equilibrio - self.coolant_temp) / TAU_AGUA_S * self.dt

        # Lubrificação
        fator_viscosidade = 1.0 - (self.oil_temp - 90.0) * 0.0035
        pressao = (1.8 + (self.rpm / 12000.0) * 3.8) * fator_viscosidade + self._ruido(0.06)
        self.oil_pressure = max(1.2, min(PRESSAO_ALIVIO_BAR, pressao))

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "vehicle_id": VEHICLE_ID,
            "circuit": CIRCUIT_NAME,
            "sector": setor["name"],
            "lap": self.lap_number,
            "lap_time_s": round(self.lap_time_seconds, 2),
            "last_lap_time_s": self.last_lap_time_s,
            "speed_kmh": round(self.speed, 1),
            "rpm": int(self.rpm),
            "gear": self.gear,
            "tps_percent": round(self.tps, 1),
            "brake_bar": round(self.brake_bar, 1),
            "g_lat": round(self.g_lat, 2),
            "g_long": round(self.g_long, 2),
            "oil_pressure_bar": round(self.oil_pressure, 2),
            "oil_temp_c": round(self.oil_temp, 1),
            "coolant_temp_c": round(self.coolant_temp, 1),
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "altitude_m": round(altitude, 1),
        }

    def generate_lap_dataset(self, num_points: int = 1500) -> List[Dict[str, Any]]:
        """Gera uma sequência contínua de amostras simuladas."""
        return [self.step() for _ in range(num_points)]
