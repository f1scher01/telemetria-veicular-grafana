"""
Simulador de Cinemática e Termodinâmica Veicular em Pista de Competição.
Modela o comportamento de trem de força, sensores mecânicos e GPS no Autódromo de Interlagos.
"""

import math
import random
from typing import Dict, Generator, List, Any
from datetime import datetime, timezone

from .config import INTERLAGOS_SECTORS, SAMPLING_RATE_HZ, VEHICLE_ID, CIRCUIT_NAME


class TelemetrySimulator:
    def __init__(self, sample_rate_hz: int = SAMPLING_RATE_HZ):
        self.sample_rate = sample_rate_hz
        self.dt = 1.0 / sample_rate_hz
        
        # Estados dinâmicos do veículo
        self.speed = 180.0          # km/h
        self.rpm = 9200.0           # RPM
        self.gear = 5
        self.tps = 85.0             # % acelerador
        self.brake_bar = 0.0        # Pressão de freio (bar)
        self.g_lat = 0.0            # G lateral
        self.g_long = 0.2           # G longitudinal
        
        # Estados termodinâmicos
        self.oil_temp = 92.0        # °C
        self.coolant_temp = 86.0    # °C
        self.oil_pressure = 4.8     # bar
        
        # Posição na pista
        self.sectors = INTERLAGOS_SECTORS
        self.current_sector_idx = 0
        self.progress_in_sector = 0.0
        self.lap_number = 1
        self.lap_time_seconds = 0.0
        self.total_time = 0.0

    def step(self) -> Dict[str, Any]:
        """Avança a simulação em um passo de tempo (dt) e retorna o snapshot de telemetria."""
        self.total_time += self.dt
        self.lap_time_seconds += self.dt
        
        # Setor atual e próximo setor
        current_sec = self.sectors[self.current_sector_idx]
        next_sec = self.sectors[(self.current_sector_idx + 1) % len(self.sectors)]
        
        # Progresso no setor
        step_increment = (self.speed / 120.0) * (self.dt / 4.0)
        self.progress_in_sector += step_increment
        
        if self.progress_in_sector >= 1.0:
            self.progress_in_sector = 0.0
            self.current_sector_idx = (self.current_sector_idx + 1) % len(self.sectors)
            # Conclusão de volta
            if self.current_sector_idx == 0:
                self.lap_number += 1
                self.lap_time_seconds = 0.0
            current_sec = self.sectors[self.current_sector_idx]
            next_sec = self.sectors[(self.current_sector_idx + 1) % len(self.sectors)]
            
        t = self.progress_in_sector
        
        # Interpolação suave de coordenadas GPS
        lat = current_sec["lat"] + (next_sec["lat"] - current_sec["lat"]) * t + random.uniform(-0.00002, 0.00002)
        lon = current_sec["lon"] + (next_sec["lon"] - current_sec["lon"]) * t + random.uniform(-0.00002, 0.00002)
        altitude = 760.0 + 18.0 * math.sin(self.current_sector_idx + t)
        
        # Dinâmica de velocidade e comandos
        target_speed = current_sec["speed_target"] + (next_sec["speed_target"] - current_sec["speed_target"]) * t
        speed_diff = target_speed - self.speed
        
        if speed_diff > 5.0:
            # Aceleração
            self.tps = min(100.0, 70.0 + speed_diff * 1.5)
            self.brake_bar = 0.0
            self.speed += min(18.0 * self.dt, speed_diff * 0.4)
            self.g_long = min(0.95, (self.tps / 100.0) * 0.85 + random.uniform(-0.05, 0.05))
        elif speed_diff < -5.0:
            # Frenagem forte
            self.tps = 0.0
            braking_intensity = min(85.0, abs(speed_diff) * 2.0)
            self.brake_bar = braking_intensity
            self.speed -= min(45.0 * self.dt, abs(speed_diff) * 0.6)
            self.g_long = max(-2.1, -1.8 * (braking_intensity / 80.0) + random.uniform(-0.05, 0.05))
        else:
            # Manutenção de velocidade na curva
            self.tps = 45.0 + random.uniform(-5, 5)
            self.brake_bar = 0.0
            self.speed += random.uniform(-1.0, 1.0) * self.dt
            self.g_long = random.uniform(-0.1, 0.1)
            
        self.speed = max(55.0, min(265.0, self.speed))
        
        # Marcha e RPM
        gear_ratios = {1: 50, 2: 85, 3: 135, 4: 180, 5: 225, 6: 270}
        self.gear = current_sec.get("gear", 4)
        max_speed_gear = gear_ratios[self.gear]
        self.rpm = (self.speed / max_speed_gear) * 11800.0 + random.uniform(-60, 60)
        self.rpm = max(3800.0, min(12400.0, self.rpm))
        
        # Força G lateral em curvas
        is_turn = "Curva" in current_sec["name"] or "S do" in current_sec["name"] or "Bico" in current_sec["name"]
        if is_turn:
            turn_direction = -1 if "Lago" in current_sec["name"] or "Senna 1" in current_sec["name"] else 1
            self.g_lat = (self.speed / 130.0) * 1.55 * turn_direction + random.uniform(-0.08, 0.08)
        else:
            self.g_lat = random.uniform(-0.12, 0.12)
            
        # Termodinâmica: Temperatura do Óleo
        # Sobe com TPS alto e RPM alto, arrefece suavemente com o ar na reta
        heat_input = (self.rpm / 12000.0) * (self.tps / 100.0) * 0.12
        cooling_oil = (self.speed / 250.0) * 0.05 + 0.02
        self.oil_temp += (heat_input - cooling_oil) * self.dt
        self.oil_temp = max(88.0, min(118.5, self.oil_temp))
        
        # Termodinâmica: Temperatura do Arrefecimento (Água)
        # Termostato estabiliza entre 85°C e 94°C
        cooling_water = (self.coolant_temp - 87.0) * 0.08
        self.coolant_temp += (heat_input * 0.9 - cooling_water) * self.dt
        self.coolant_temp = max(82.0, min(97.0, self.coolant_temp))
        
        # Pressão do Óleo (bar):
        # Aumenta proporcionalmente ao RPM, mas sofre pequena atenuação conforme o óleo esquenta (perda de viscosidade)
        viscosity_factor = 1.0 - (self.oil_temp - 90.0) * 0.0035
        base_pressure = 1.8 + (self.rpm / 12000.0) * 3.8
        self.oil_pressure = (base_pressure * viscosity_factor) + random.uniform(-0.06, 0.06)
        self.oil_pressure = max(1.2, min(5.9, self.oil_pressure))
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "vehicle_id": VEHICLE_ID,
            "circuit": CIRCUIT_NAME,
            "sector": current_sec["name"],
            "lap": self.lap_number,
            "lap_time_s": round(self.lap_time_seconds, 2),
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
            "altitude_m": round(altitude, 1)
        }

    def generate_lap_dataset(self, num_points: int = 1500) -> List[Dict[str, Any]]:
        """Gera um conjunto contínuo de dados simulados de uma volta completa."""
        data = []
        for _ in range(num_points):
            data.append(self.step())
        return data
