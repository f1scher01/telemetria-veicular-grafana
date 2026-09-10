"""
Gerador de Imagens de Telemetria e Diagnóstico Veicular em Alta Resolução (300 DPI).
Produz gráficos técnicos de engenharia automotiva para documentação e README do repositório.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

def generate_telemetry_figures(csv_path: str = "data/sample_lap_interlagos.csv"):
    if not os.path.exists(csv_path):
        print(f"Erro: Arquivo {csv_path} não encontrado.")
        return
        
    df = pd.read_csv(csv_path)
    time = df['lap_time_s'].values
    speed = df['speed_kmh'].values
    rpm = df['rpm'].values
    tps = df['tps_percent'].values
    brake = df['brake_bar'].values
    gear = df['gear'].values
    g_lat = df['g_lat'].values
    g_long = df['g_long'].values
    oil_press = df['oil_pressure_bar'].values
    oil_temp = df['oil_temp_c'].values
    coolant_temp = df['coolant_temp_c'].values
    lat = df['latitude'].values
    lon = df['longitude'].values

    # Estilo Dark Mode Profissional
    plt.style.use('dark_background')
    bg_color = '#0b0f19'
    card_color = '#111827'
    grid_color = '#1f293d'
    text_color = '#f3f4f6'
    sub_color = '#9ca3af'
    
    # -------------------------------------------------------------
    # FIGURA 1: PAINEL INTEGRADO DE TELEMETRIA E AQUISIÇÃO (300 DPI)
    # -------------------------------------------------------------
    fig = plt.figure(figsize=(20, 11.5), facecolor=bg_color)
    gs = gridspec.GridSpec(4, 3, width_ratios=[1.25, 1.15, 0.95], height_ratios=[1, 1, 1, 1], 
                           wspace=0.32, hspace=0.44, left=0.06, right=0.96, top=0.88, bottom=0.06)

    fig.suptitle("SISTEMA DE TELEMETRIA VEICULAR — ANÁLISE DE VOLTA RÁPIDA (AUTÓDROMO DE INTERLAGOS)\n"
                 "Aquisição a 10 Hz | Carro 01 Fórmula Mauá | Tempo de Volta: 1m40s2 | Velocidade Máx: 236.4 km/h",
                 fontsize=14, fontweight='bold', color='#60a5fa', y=0.965)

    # Subplot 1: Velocidade & Marcha
    ax1 = fig.add_subplot(gs[0, 0], facecolor=card_color)
    ax1.plot(time, speed, color='#38bdf8', linewidth=1.8, label='Velocidade (km/h)')
    ax1.set_ylabel("Velocidade (km/h)", color='#38bdf8', fontsize=10, fontweight='bold')
    ax1.set_xlim(0, max(time))
    ax1.grid(True, linestyle='--', alpha=0.35, color=grid_color)
    ax1.tick_params(colors=sub_color, labelsize=9)
    # Linha secundária de marcha
    ax1_gear = ax1.twinx()
    ax1_gear.step(time, gear, color='#fbbf24', alpha=0.8, where='post', linewidth=1.2, label='Marcha')
    ax1_gear.set_ylabel("Marcha", color='#fbbf24', fontsize=9)
    ax1_gear.set_ylim(0.5, 6.5)
    ax1_gear.set_yticks([1, 2, 3, 4, 5, 6])
    ax1_gear.tick_params(colors='#fbbf24', labelsize=8)
    ax1.set_title("Dinâmica Longitudinal: Velocidade & Relação de Marchas", color=text_color, fontsize=11, fontweight='bold', pad=10)

    # Subplot 2: Rotação do Motor (RPM) & Redline
    ax2 = fig.add_subplot(gs[1, 0], facecolor=card_color)
    ax2.plot(time, rpm, color='#a855f7', linewidth=1.6, label='RPM Motor')
    ax2.axhline(8500, color='#ef4444', linestyle=':', linewidth=1.4, label='Shift Light (8500 RPM)')
    ax2.axhline(9200, color='#dc2626', linestyle='--', linewidth=1.4, label='Corte Redline (9200 RPM)')
    ax2.set_ylabel("RPM", color='#a855f7', fontsize=10, fontweight='bold')
    ax2.set_xlim(0, max(time))
    ax2.set_ylim(4000, 9800)
    ax2.grid(True, linestyle='--', alpha=0.35, color=grid_color)
    ax2.tick_params(colors=sub_color, labelsize=9)
    ax2.legend(loc='lower left', fontsize=8, facecolor=card_color, edgecolor=grid_color)
    ax2.set_title("Trem de Força: Rotação Instantânea e Zona de Shift", color=text_color, fontsize=11, fontweight='bold', pad=10)

    # Subplot 3: Pedais — TPS (%) e Pressão de Freio (bar)
    ax3 = fig.add_subplot(gs[2, 0], facecolor=card_color)
    ax3.plot(time, tps, color='#22c55e', linewidth=1.6, label='Acelerador (TPS %)')
    ax3.set_ylabel("TPS (%)", color='#22c55e', fontsize=10, fontweight='bold')
    ax3.set_xlim(0, max(time))
    ax3.set_ylim(-5, 105)
    ax3.grid(True, linestyle='--', alpha=0.35, color=grid_color)
    ax3.tick_params(colors=sub_color, labelsize=9)
    
    ax3_brake = ax3.twinx()
    ax3_brake.fill_between(time, 0, brake, color='#ef4444', alpha=0.45, label='Freio Hidráulico (bar)')
    ax3_brake.plot(time, brake, color='#ef4444', linewidth=1.2)
    ax3_brake.set_ylabel("Pressão Freio (bar)", color='#ef4444', fontsize=9)
    ax3_brake.set_ylim(0, 70)
    ax3_brake.tick_params(colors='#ef4444', labelsize=8)
    ax3.set_title("Ações do Piloto: Sobreposição de Acelerador e Frenagem", color=text_color, fontsize=11, fontweight='bold', pad=10)

    # Subplot 4: Acelerações Inerciais G-Lat & G-Long
    ax4 = fig.add_subplot(gs[3, 0], facecolor=card_color)
    ax4.plot(time, g_lat, color='#ec4899', linewidth=1.5, label='G Lateral (Curvas)')
    ax4.plot(time, g_long, color='#06b6d4', linewidth=1.5, label='G Longitudinal (Acel/Fren)')
    ax4.axhline(0, color=sub_color, linestyle='-', linewidth=0.8, alpha=0.5)
    ax4.set_xlabel("Tempo de Volta (s)", color=text_color, fontsize=10, fontweight='bold')
    ax4.set_ylabel("Aceleração (G)", color=text_color, fontsize=10, fontweight='bold')
    ax4.set_xlim(0, max(time))
    ax4.set_ylim(-2.2, 2.2)
    ax4.grid(True, linestyle='--', alpha=0.35, color=grid_color)
    ax4.tick_params(colors=sub_color, labelsize=9)
    ax4.legend(loc='upper right', fontsize=8, facecolor=card_color, edgecolor=grid_color)
    ax4.set_title("Dinâmica Veicular: Cargas Inerciais e Aceleração Triaxial", color=text_color, fontsize=11, fontweight='bold', pad=10)

    # Subplot 5: Mapa do Traçado GPS Interlagos (Colorido por Velocidade)
    ax5 = fig.add_subplot(gs[0:2, 1], facecolor=card_color)
    scatter = ax5.scatter(lon, lat, c=speed, cmap='plasma', s=18, edgecolor='none')
    cbar = fig.colorbar(scatter, ax=ax5, orientation='horizontal', pad=0.10, fraction=0.045)
    cbar.set_label("Velocidade Escalar no Traçado (km/h)", color=text_color, fontsize=9, fontweight='bold')
    cbar.ax.tick_params(colors=sub_color, labelsize=8)

    # Limites estritos para garantir margem de respiro perfeita
    ax5.set_xlim(-46.7055, -46.6940)
    ax5.set_ylim(-23.7085, -23.7000)
    
    # Anotações de setores icônicos de Interlagos com setas e caixas
    bbox_props = dict(boxstyle="round,pad=0.2", fc="#1e293b", ec="#3b82f6", lw=0.8, alpha=0.9)
    ax5.text(-46.6958, -23.7018, "Reta dos Boxes", color='#facc15', fontsize=8, fontweight='bold', bbox=bbox_props)
    ax5.text(-46.6975, -23.7048, "S do Senna", color='#f43f5e', fontsize=8, fontweight='bold', bbox=bbox_props)
    ax5.text(-46.7022, -23.7072, "Reta Oposta", color='#38bdf8', fontsize=8, fontweight='bold', bbox=bbox_props)
    ax5.text(-46.7048, -23.7032, "Ferradura", color='#fb923c', fontsize=8, fontweight='bold', bbox=bbox_props)
    ax5.text(-46.6998, -23.7012, "Juncao", color='#4ade80', fontsize=8, fontweight='bold', bbox=bbox_props)
    
    ax5.set_title("Georreferenciamento GPS: Traçado do Autódromo de Interlagos", color=text_color, fontsize=11, fontweight='bold', pad=10)
    ax5.set_xlabel("Longitude (WGS84)", color=sub_color, fontsize=8)
    ax5.set_ylabel("Latitude (WGS84)", color=sub_color, fontsize=8)
    ax5.grid(True, linestyle=':', alpha=0.3, color=grid_color)
    ax5.tick_params(colors=sub_color, labelsize=7)
    # Formatação de coordenadas limpas
    ax5.ticklabel_format(useOffset=False, style='plain')

    # Subplot 6: Diagrama G-G (Círculo de Atrito de Michelin / Miliken)
    ax6 = fig.add_subplot(gs[2:4, 1], facecolor=card_color)
    # Círculos de limite de aderência (1.0G, 1.5G, 2.0G)
    theta = np.linspace(0, 2*np.pi, 200)
    for radius, ls, alpha_val in [(1.0, ':', 0.4), (1.5, '--', 0.6), (2.0, '-', 0.8)]:
        ax6.plot(radius * np.cos(theta), radius * np.sin(theta), linestyle=ls, color='#64748b', alpha=alpha_val, linewidth=1.1)
        ax6.text(radius * 0.707, radius * 0.707, f"{radius:.1f}G", color='#94a3b8', fontsize=7)
    
    scatter_gg = ax6.scatter(g_lat, g_long, c=speed, cmap='viridis', s=12, alpha=0.75, edgecolors='none')
    ax6.axvline(0, color=sub_color, linestyle='-', linewidth=0.8, alpha=0.4)
    ax6.axhline(0, color=sub_color, linestyle='-', linewidth=0.8, alpha=0.4)
    ax6.set_xlim(-2.3, 2.3)
    ax6.set_ylim(-2.3, 2.3)
    ax6.set_xlabel("Aceleração Lateral (G) — Curvas", color=text_color, fontsize=9, fontweight='bold')
    ax6.set_ylabel("Aceleração Longitudinal (G) — Frenagem / Aceleração", color=text_color, fontsize=9, fontweight='bold')
    ax6.set_title("Diagrama G-G (Círculo de Atrito & Envelope Operacional)", color=text_color, fontsize=11, fontweight='bold', pad=8)
    ax6.grid(True, linestyle='--', alpha=0.25, color=grid_color)
    ax6.tick_params(colors=sub_color, labelsize=8)
    cbar_gg = fig.colorbar(scatter_gg, ax=ax6, orientation='horizontal', pad=0.10, fraction=0.045)
    cbar_gg.set_label("Velocidade (km/h)", color=text_color, fontsize=8)
    cbar_gg.ax.tick_params(colors=sub_color, labelsize=7)

    # Subplot 7: Saúde do Trem de Força — Pressão de Óleo vs RPM
    ax7 = fig.add_subplot(gs[0:2, 2], facecolor=card_color)
    ax7.scatter(rpm, oil_press, c='#3b82f6', s=10, alpha=0.6, label='Pontos de Operação')
    ax7.axhline(2.5, color='#ef4444', linestyle='--', linewidth=1.5, label='Alarme Mínimo (2.5 bar)')
    ax7.set_xlabel("RPM do Motor", color=text_color, fontsize=9, fontweight='bold')
    ax7.set_ylabel("Pressão de Óleo (bar)", color='#3b82f6', fontsize=9, fontweight='bold')
    ax7.set_title("Curva de Lubrificação: Pressão vs Rotação", color=text_color, fontsize=11, fontweight='bold', pad=10)
    ax7.set_ylim(1.5, 5.5)
    ax7.grid(True, linestyle='--', alpha=0.35, color=grid_color)
    ax7.tick_params(colors=sub_color, labelsize=8)
    ax7.legend(loc='lower right', fontsize=8, facecolor=card_color, edgecolor=grid_color)

    # Subplot 8: Termodinâmica — Óleo e Arrefecimento ao Longo da Sessão
    ax8 = fig.add_subplot(gs[2:4, 2], facecolor=card_color)
    ax8.plot(time, oil_temp, color='#f97316', linewidth=1.8, label='Temp. Óleo (°C)')
    ax8.plot(time, coolant_temp, color='#06b6d4', linewidth=1.8, label='Temp. Radiador (°C)')
    ax8.axhline(105.0, color='#ef4444', linestyle=':', linewidth=1.3, label='Alerta Óleo (>105°C)')
    ax8.axhline(95.0, color='#eab308', linestyle=':', linewidth=1.3, label='Alerta Radiador (>95°C)')
    ax8.set_xlabel("Tempo de Volta (s)", color=text_color, fontsize=9, fontweight='bold')
    ax8.set_ylabel("Temperatura (°C)", color=text_color, fontsize=9, fontweight='bold')
    ax8.set_title("Gestão Térmica: Balanço Fluido-Radiador", color=text_color, fontsize=11, fontweight='bold', pad=10)
    ax8.set_xlim(0, max(time))
    ax8.set_ylim(70, 115)
    ax8.grid(True, linestyle='--', alpha=0.35, color=grid_color)
    ax8.tick_params(colors=sub_color, labelsize=8)
    ax8.legend(loc='lower right', fontsize=8, facecolor=card_color, edgecolor=grid_color)

    output_fig1 = "telemetria_dashboard_preview.png"
    plt.savefig(output_fig1, dpi=300, bbox_inches='tight', facecolor=bg_color)
    plt.close()
    print(f"Sucesso: Dashboard de Telemetria gerado em alta resolução: {output_fig1}")


if __name__ == "__main__":
    generate_telemetry_figures()

