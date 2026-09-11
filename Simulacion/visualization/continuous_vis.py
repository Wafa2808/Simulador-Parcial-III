"""
Módulo de Renders Gráficos para la Simulación Continua (Pygame)
----------------------------------------------------------------
Visualiza el nodo del servidor, las fluctuaciones de temperatura mediante
una barra térmica de colores (azul -> verde -> amarillo -> rojo crítico)
y la gráfica de tráfico de red en tiempo real.
"""

import math
import pygame
from typing import Dict, Any

# Colores RGB
COLOR_BG = (25, 30, 42)
COLOR_CARD = (38, 45, 62)
COLOR_TEXT = (240, 240, 245)
COLOR_TEXT_DIM = (160, 170, 190)
COLOR_PRIMARY = (52, 152, 219)      # Azul
COLOR_SUCCESS = (46, 204, 113)      # Verde
COLOR_WARNING = (241, 196, 15)      # Amarillo
COLOR_DANGER = (231, 76, 60)        # Rojo
COLOR_ACCENT = (155, 89, 182)       # Morado


class ContinuousVisualizer:
    """Clase encargada de dibujar los componentes del clúster de servidores."""

    def __init__(self, surface: pygame.Surface, font_title: pygame.font.Font, font_body: pygame.font.Font):
        self.surface: pygame.Surface = surface
        self.font_title: pygame.font.Font = font_title
        self.font_body: pygame.font.Font = font_body

    def render(self, engine, metrics: Dict[str, Any], is_paused: bool, speed_multiplier: float):
        """Dibuja todo el panel visual sincronizado con el modelo térmico continuo POO."""
        self.surface.fill(COLOR_BG)

        # 1. Encabezado principal
        title_surf = self.font_title.render("SIMULACIÓN CONTINUA - CLÚSTER DE SERVIDORES Y BALANCES TÉRMICOS", True, COLOR_TEXT)
        self.surface.blit(title_surf, (30, 20))

        hours = engine.current_time_seconds / 3600.0
        subtitle_str = f"Tiempo Simulado: {hours:.2f} hrs ({engine.current_time_seconds:.0f} s) | Estado: {'[PAUSADO]' if is_paused else '[EJECUTANDO]'} | Velocidad: {speed_multiplier}x"
        sub_surf = self.font_body.render(subtitle_str, True, COLOR_WARNING if is_paused else COLOR_SUCCESS)
        self.surface.blit(sub_surf, (30, 55))

        # 2. Tarjeta: Nodo del Servidor y Estado Térmico
        self._render_server_node(engine)

        # 3. Tarjeta: Medidor / Barra Térmica
        self._render_thermal_gauge(engine)

        # 4. Tarjeta: Tráfico de Red y Rendimiento (Throughput)
        self._render_traffic_panel(engine)

        # 5. Tarjeta: HUD de Métricas Globales
        self._render_hud_metrics(engine, metrics)

        # 6. Panel de Trazas Recientes
        self._render_trace_log(engine)

    def _get_thermal_color(self, temp: float) -> tuple:
        """Devuelve el color correspondiente al gradiente térmico de la temperatura."""
        if temp <= 65.0:
            return COLOR_PRIMARY       # Azul (Frío/Normal)
        elif temp <= 70.0:
            return COLOR_SUCCESS       # Verde (Óptimo)
        elif temp <= 75.0:
            return COLOR_WARNING       # Amarillo/Naranja (Elevado)
        else:
            return COLOR_DANGER        # Rojo (Peligro/Thermal Throttling)

    def _render_server_node(self, engine):
        """Dibuja la representación gráfica del nodo del servidor con resplandor térmico."""
        rect = pygame.Rect(40, 100, 320, 220)
        pygame.draw.rect(self.surface, COLOR_CARD, rect, border_radius=10)
        pygame.draw.rect(self.surface, COLOR_TEXT_DIM, rect, width=2, border_radius=10)

        t_surf = self.font_title.render("Nodo del Servidor", True, COLOR_TEXT)
        self.surface.blit(t_surf, (rect.x + 20, rect.y + 15))

        temp = engine.thermal_model.current_temp
        thermal_color = self._get_thermal_color(temp)

        # Dibujar gráfico del servidor
        server_box = pygame.Rect(rect.x + 40, rect.y + 60, 240, 100)
        pygame.draw.rect(self.surface, (20, 25, 35), server_box, border_radius=8)
        pygame.draw.rect(self.surface, thermal_color, server_box, width=4, border_radius=8)

        # LEDs del servidor
        for i in range(3):
            led_color = thermal_color if i == 0 else (50, 60, 80)
            pygame.draw.circle(self.surface, led_color, (server_box.x + 25 + i * 20, server_box.y + 25), 6)

        # Texto del servidor
        status_str = "ESTRANGLAMIENTO TÉRMICO" if engine.thermal_model.is_throttling else "OPERACIÓN NORMAL"
        st_surf = self.font_body.render(status_str, True, thermal_color)
        self.surface.blit(st_surf, (server_box.x + 20, server_box.y + 55))

        temp_str = f"Temperatura: {temp:.2f} °C"
        tp_surf = self.font_title.render(temp_str, True, COLOR_TEXT)
        self.surface.blit(tp_surf, (rect.x + 20, rect.y + 175))

    def _render_thermal_gauge(self, engine):
        """Dibuja la barra de gradiente térmico de temperatura."""
        rect = pygame.Rect(380, 100, 480, 220)
        pygame.draw.rect(self.surface, COLOR_CARD, rect, border_radius=10)
        pygame.draw.rect(self.surface, COLOR_TEXT_DIM, rect, width=2, border_radius=10)

        t_surf = self.font_title.render("Barra Térmica y Balance de Calor", True, COLOR_TEXT)
        self.surface.blit(t_surf, (rect.x + 20, rect.y + 15))

        temp = engine.thermal_model.current_temp
        min_scale, max_scale = 50.0, 85.0
        fill_pct = min(1.0, max(0.0, (temp - min_scale) / (max_scale - min_scale)))

        thermal_color = self._get_thermal_color(temp)

        # Barra de temperatura
        bar_bg = pygame.Rect(rect.x + 20, rect.y + 60, 440, 40)
        pygame.draw.rect(self.surface, (20, 25, 35), bar_bg, border_radius=8)
        
        fill_rect = pygame.Rect(bar_bg.x, bar_bg.y, int(bar_bg.width * fill_pct), bar_bg.height)
        pygame.draw.rect(self.surface, thermal_color, fill_rect, border_radius=8)
        pygame.draw.rect(self.surface, COLOR_TEXT_DIM, bar_bg, width=2, border_radius=8)

        # Marcador de meta 70°C
        target_pct = (70.0 - min_scale) / (max_scale - min_scale)
        target_x = bar_bg.x + int(bar_bg.width * target_pct)
        pygame.draw.line(self.surface, COLOR_TEXT, (target_x, bar_bg.y - 5), (target_x, bar_bg.bottom + 5), 3)

        lbl_target = self.font_body.render("Meta: 70°C", True, COLOR_TEXT)
        self.surface.blit(lbl_target, (target_x - 30, bar_bg.bottom + 8))

        # Línea de peligro 75°C
        danger_pct = (75.0 - min_scale) / (max_scale - min_scale)
        danger_x = bar_bg.x + int(bar_bg.width * danger_pct)
        pygame.draw.line(self.surface, COLOR_DANGER, (danger_x, bar_bg.y - 5), (danger_x, bar_bg.bottom + 5), 3)

        lbl_danger = self.font_body.render("Crítico: 75°C", True, COLOR_DANGER)
        self.surface.blit(lbl_danger, (danger_x - 35, bar_bg.y - 25))

        # Información adicional
        throttling_str = f"Eventos Throttling: {engine.throttling_events_count} | Duración: {engine.cluster.total_throttling_seconds/60.0:.2f} min"
        th_surf = self.font_body.render(throttling_str, True, COLOR_DANGER if engine.throttling_events_count > 0 else COLOR_TEXT)
        self.surface.blit(th_surf, (rect.x + 20, rect.y + 170))

    def _render_traffic_panel(self, engine):
        """Dibuja la gráfica en vivo de tráfico de red e indicador de rendimiento."""
        rect = pygame.Rect(40, 340, 320, 220)
        pygame.draw.rect(self.surface, COLOR_CARD, rect, border_radius=10)
        pygame.draw.rect(self.surface, COLOR_TEXT_DIM, rect, width=2, border_radius=10)

        t_surf = self.font_title.render("Tráfico Entrante (Gbps)", True, COLOR_TEXT)
        self.surface.blit(t_surf, (rect.x + 20, rect.y + 15))

        current_traffic = engine.history_traffic[-1] if engine.history_traffic else 3.0
        eff = engine.history_efficiency[-1] * 100.0 if engine.history_efficiency else 90.0

        tr_str = f"Tráfico Actual: {current_traffic:.2f} Gbps"
        tr_surf = self.font_title.render(tr_str, True, COLOR_PRIMARY)
        self.surface.blit(tr_surf, (rect.x + 20, rect.y + 55))

        eff_str = f"Eficiencia del Clúster: {eff:.1f}%"
        ef_surf = self.font_body.render(eff_str, True, COLOR_SUCCESS if eff >= 85 else COLOR_WARNING)
        self.surface.blit(ef_surf, (rect.x + 20, rect.y + 90))

        # Mini gráfica de historial de tráfico
        graph_box = pygame.Rect(rect.x + 20, rect.y + 120, 280, 80)
        pygame.draw.rect(self.surface, (15, 20, 28), graph_box, border_radius=6)
        
        recent_traffic = engine.history_traffic[-50:]
        if len(recent_traffic) > 1:
            points = []
            for i, val in enumerate(recent_traffic):
                px = graph_box.x + int(i * (graph_box.width / 50))
                # Normalizar val entre 1.0 y 5.0
                norm = (val - 1.0) / 4.0
                py = graph_box.bottom - int(norm * (graph_box.height - 10)) - 5
                points.append((px, py))
            pygame.draw.lines(self.surface, COLOR_PRIMARY, False, points, 2)

    def _render_hud_metrics(self, engine, metrics: Dict[str, Any]):
        """Dibuja el panel principal de métricas en tiempo real."""
        rect = pygame.Rect(380, 340, 480, 220)
        pygame.draw.rect(self.surface, COLOR_CARD, rect, border_radius=10)
        pygame.draw.rect(self.surface, COLOR_TEXT_DIM, rect, width=2, border_radius=10)

        t_surf = self.font_title.render("Métricas Globales de Cómputo", True, COLOR_TEXT)
        self.surface.blit(t_surf, (rect.x + 20, rect.y + 15))

        lines = [
            f"• Terabytes Procesados     : {metrics.get('total_terabytes_procesados', 0.0):.4f} TB",
            f"• Tráfico Promedio         : {metrics.get('trafico_promedio_gbps', 0.0):.2f} Gbps",
            f"• Temperatura Promedio     : {metrics.get('temperatura_promedio_celsius', 0.0):.2f} °C",
            f"• Temp Mínima / Máxima     : {metrics.get('temperatura_minima_celsius', 0.0):.1f}°C / {metrics.get('temperatura_maxima_celsius', 0.0):.1f}°C",
            f"• Variabilidad (Std Dev)   : ±{metrics.get('variabilidad_temperatura_std', 0.0):.2f} °C",
            f"• Estabilidad Térmica      : {metrics.get('estabilidad_termica_pct', 100.0):.1f}% del tiempo"
        ]

        for idx, line in enumerate(lines):
            l_surf = self.font_body.render(line, True, COLOR_TEXT)
            self.surface.blit(l_surf, (rect.x + 20, rect.y + 55 + idx * 24))

    def _render_trace_log(self, engine):
        """Dibuja el visor de trazas en la parte inferior."""
        rect = pygame.Rect(40, 575, 820, 100)
        pygame.draw.rect(self.surface, (15, 20, 28), rect, border_radius=8)
        pygame.draw.rect(self.surface, COLOR_TEXT_DIM, rect, width=1, border_radius=8)

        t_surf = self.font_body.render("Últimos Registros Térmicos (Live Log):", True, COLOR_ACCENT)
        self.surface.blit(t_surf, (rect.x + 15, rect.y + 10))

        recent_traces = engine.traces[-3:] if engine.traces else ["Esperando datos de la simulación continua..."]
        for idx, tr in enumerate(recent_traces):
            tr_surf = self.font_body.render(tr, True, COLOR_TEXT_DIM)
            self.surface.blit(tr_surf, (rect.x + 15, rect.y + 32 + idx * 20))
