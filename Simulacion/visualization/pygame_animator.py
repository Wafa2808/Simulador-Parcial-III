"""
Módulo Integrador de Animación Interactiva Pygame (Pregunta Bonus - 2 Puntos)
-----------------------------------------------------------------------------
Gestiona la ventana gráfica de Pygame, los eventos de teclado (Pausar/Reanudar con ESPACIO,
ajuste de velocidad con FLECHAS), el reloj de renderizado a 60 FPS y la sincronización
directa con las clases POO de simulación.
"""

import sys
import pygame
from typing import Dict, Any

from models.discrete_event import DiscreteSimulationEngine
from models.continuous import ContinuousSimulationEngine
from visualization.discrete_vis import DiscreteVisualizer
from visualization.continuous_vis import ContinuousVisualizer
from services.ai_service import AIService
from services.logger_service import LoggerService
import config


class PygameAnimator:
    """Clase principal de la interfaz gráfica e interactiva en Pygame."""

    def __init__(self, mode: str = "discrete", hours: float = 8.0):
        """
        mode: 'discrete' para el Problema 1 o 'continuous' para el Problema 2.
        hours: Horas a simular.
        """
        self.mode: str = mode
        self.hours: float = hours
        self.is_paused: bool = False
        self.speed_multiplier: float = 1.0
        
        # Inicializar Pygame
        pygame.init()
        pygame.font.init()

        self.width: int = 900
        self.height: int = 700
        self.screen: pygame.Surface = pygame.display.set_mode((self.width, self.height))
        
        title_mode = "FÁBRICA DE LAPTOPS (EVENTOS DISCRETOS)" if mode == "discrete" else "CLÚSTER DE SERVIDORES (SIMULACIÓN CONTINUA)"
        pygame.display.set_caption(f"PARCIAL III SIMULACIÓN - VISUALIZACIÓN INTERACTIVA - {title_mode}")
        
        self.clock: pygame.time.Clock = pygame.time.Clock()

        # Fuentes
        self.font_title = pygame.font.SysFont("Arial", 18, bold=True)
        self.font_body = pygame.font.SysFont("Arial", 14)

        # Inicializar motores de simulación POO
        if self.mode == "discrete":
            self.engine = DiscreteSimulationEngine(hours=hours)
            self.visualizer = DiscreteVisualizer(self.screen, self.font_title, self.font_body)
            # Para la simulación discreta animada, pre-cargamos la simulación o la avanzamos paso a paso
            self._init_discrete_simulation()
        else:
            self.engine = ContinuousSimulationEngine(hours=hours, dt=1.0)
            self.visualizer = ContinuousVisualizer(self.screen, self.font_title, self.font_body)

    def _init_discrete_simulation(self):
        """Inicializa los eventos de la simulación por eventos discretos."""
        self.engine.log_trace(f"--- INICIO DE ANIMACIÓN DISCRETA ({self.hours:.2f} HORAS) ---")
        first_arrival = self.engine._generate_interarrival_time()
        if first_arrival <= self.engine.total_simulation_minutes:
            self.engine.order_counter += 1
            from models.discrete_event import Order, DiscreteEvent
            first_order = Order(self.engine.order_counter, first_arrival)
            self.engine.schedule_event(first_arrival, DiscreteEvent.EVENT_ORDER_ARRIVAL, first_order)

    def run(self):
        """Bucle principal de la animación Pygame."""
        running = True

        print(f"\n[PYGAME] Iniciando ventana gráfica de simulación '{self.mode}'...")
        print("[CONTROLES DE TECLADO]:")
        print("  • ESPACIO           : Pausar / Reanudar la animación")
        print("  • FLECHA ARRIBA     : Incrementar velocidad de simulación")
        print("  • FLECHA ABAJO      : Disminuir velocidad de simulación")
        print("  • TECLA ESC         : Salir de la animación y volver al menú principal\n")

        while running:
            # 1. Manejo de eventos de entrada por teclado y ventana
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self.is_paused = not self.is_paused
                        print(f"-> Estado de Animación: {'PAUSADO' if self.is_paused else 'REANUDADO'}")
                    elif event.key == pygame.K_UP:
                        speeds = [1.0, 2.0, 5.0, 10.0, 20.0, 50.0]
                        idx = speeds.index(self.speed_multiplier) if self.speed_multiplier in speeds else 0
                        self.speed_multiplier = speeds[min(len(speeds) - 1, idx + 1)]
                        print(f"-> Velocidad establecida en {self.speed_multiplier}x")
                    elif event.key == pygame.K_DOWN:
                        speeds = [1.0, 2.0, 5.0, 10.0, 20.0, 50.0]
                        idx = speeds.index(self.speed_multiplier) if self.speed_multiplier in speeds else 0
                        self.speed_multiplier = speeds[max(0, idx - 1)]
                        print(f"-> Velocidad establecida en {self.speed_multiplier}x")

            # 2. Avanzar la lógica POO de la simulación si no está pausada
            if not self.is_paused:
                self._update_simulation_step()

            # 3. Renderizar la interfaz gráfica sincronizada
            metrics = self.engine.get_metrics()
            self.visualizer.render(self.engine, metrics, self.is_paused, self.speed_multiplier)

            pygame.display.flip()
            self.clock.tick(60)  # Mantener a 60 FPS

        pygame.quit()
        print("\n[PYGAME] Ventana gráfica cerrada. Compilando métricas y ejecutando análisis de IA...")
        
        # Al cerrar Pygame, procesar con IA y guardar reporte
        metrics = self.engine.get_metrics()
        ai_service = AIService(provider="auto")
        
        if self.mode == "discrete":
            analysis = ai_service.generate_analysis("discrete", metrics)
            LoggerService.display_metrics_summary("Métricas Finales - Animación Discreta", metrics)
            LoggerService.save_traces(config.FILE_DISCRETE_TRACE, metrics.get("trazas", []))
            LoggerService.save_ai_report(config.FILE_DISCRETE_AI_REPORT, "Fábrica de Laptops (Discreta)", metrics, analysis)
        else:
            analysis = ai_service.generate_analysis("continuous", metrics)
            LoggerService.display_metrics_summary("Métricas Finales - Animación Continua", metrics)
            LoggerService.save_traces(config.FILE_CONTINUOUS_TRACE, metrics.get("trazas", []))
            LoggerService.save_ai_report(config.FILE_CONTINUOUS_AI_REPORT, "Clúster de Servidores (Continua)", metrics, analysis)

        print("\n--- ANÁLISIS DE LA INTELIGENCIA ARTIFICIAL ---")
        print(analysis)

    def _update_simulation_step(self):
        """Avanza los pasos de simulación según el multiplicador de velocidad."""
        if self.mode == "discrete":
            # Avanzar eventos discretos pendientes hasta cubrir el delta de tiempo simulado
            import heapq
            from models.discrete_event import DiscreteEvent

            steps = int(self.speed_multiplier)
            for _ in range(steps):
                if not self.engine.event_queue or self.engine.current_time >= self.engine.total_simulation_minutes:
                    break
                event = heapq.heappop(self.engine.event_queue)
                if event.time > self.engine.total_simulation_minutes:
                    self.engine.current_time = self.engine.total_simulation_minutes
                    break
                
                self.engine.current_time = event.time
                if event.event_type == DiscreteEvent.EVENT_ORDER_ARRIVAL:
                    self.engine._handle_order_arrival(event.data)
                elif event.event_type == DiscreteEvent.EVENT_ASSEMBLY_COMPLETE:
                    self.engine._handle_assembly_complete(event.data)
                elif event.event_type == DiscreteEvent.EVENT_REORDER_DELIVERY:
                    self.engine._handle_reorder_delivery()
        else:
            # Avanzar pasos de integración continua en segundos
            steps = int(self.speed_multiplier * 5)  # Avanzar 5 segundos por cuadro de render
            for _ in range(steps):
                if self.engine.current_time_seconds > self.engine.total_seconds:
                    break
                traffic = self.engine.traffic_gen.get_current_traffic()
                temp = self.engine.thermal_model.update_temperature(traffic, self.engine.dt)
                eff = self.engine.cluster.calculate_efficiency(temp)
                self.engine.cluster.process_data(traffic, eff, self.engine.dt)

                if self.engine.thermal_model.is_throttling:
                    self.engine.cluster.total_throttling_seconds += self.engine.dt
                    if not self.engine._was_throttling_previous:
                        self.engine.throttling_events_count += 1
                        self.engine.log_trace(f"ALERTA TÉRMICA: Estrangulamiento activado. Temp: {temp:.2f}°C")
                elif self.engine._was_throttling_previous:
                    self.engine.log_trace(f"ESTABILIZACIÓN TÉRMICA: Temp normalizada a {temp:.2f}°C.")

                self.engine._was_throttling_previous = self.engine.thermal_model.is_throttling

                self.engine.history_time.append(self.engine.current_time_seconds / 3600.0)
                self.engine.history_traffic.append(traffic)
                self.engine.history_temp.append(temp)
                self.engine.history_efficiency.append(eff)

                self.engine.current_time_seconds += self.engine.dt
