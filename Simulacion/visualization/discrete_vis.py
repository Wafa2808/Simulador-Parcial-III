"""
Módulo de Renders Gráficos para la Simulación de Eventos Discretos (Pygame)
-------------------------------------------------------------------------
Visualiza la cola de órdenes, el estado de la estación de ensamblaje por color
y el nivel del inventario de procesadores en tiempo real.
"""

import pygame
from typing import Dict, Any, List

# Colores RGB
COLOR_BG = (25, 30, 42)
COLOR_CARD = (38, 45, 62)
COLOR_TEXT = (240, 240, 245)
COLOR_TEXT_DIM = (160, 170, 190)
COLOR_PRIMARY = (52, 152, 219)      # Azul
COLOR_SUCCESS = (46, 204, 113)      # Verde (Libre/Stock OK)
COLOR_WARNING = (241, 196, 15)      # Amarillo (Ensamblando/Bajo stock)
COLOR_DANGER = (231, 76, 60)        # Rojo (Detenida/Sin stock)
COLOR_ACCENT = (155, 89, 182)       # Morado


class DiscreteVisualizer:
    """Clase encargada de dibujar los componentes de la fábrica de laptops."""

    def __init__(self, surface: pygame.Surface, font_title: pygame.font.Font, font_body: pygame.font.Font):
        self.surface: pygame.Surface = surface
        self.font_title: pygame.font.Font = font_title
        self.font_body: pygame.font.Font = font_body

    def render(self, engine, metrics: Dict[str, Any], is_paused: bool, speed_multiplier: float):
        """Dibuja todo el panel visual sincronizado directamente con la simulación POO."""
        self.surface.fill(COLOR_BG)

        # 1. Encabezado principal
        title_surf = self.font_title.render("SIMULACIÓN DE EVENTOS DISCRETOS - FÁBRICA DE LAPTOPS", True, COLOR_TEXT)
        self.surface.blit(title_surf, (30, 20))

        subtitle_str = f"Tiempo Simulado: {engine.current_time:.1f} min ({engine.current_time/60.0:.2f} hrs) | Estado: {'[PAUSADO]' if is_paused else '[EJECUTANDO]'} | Velocidad: {speed_multiplier}x"
        sub_surf = self.font_body.render(subtitle_str, True, COLOR_WARNING if is_paused else COLOR_SUCCESS)
        self.surface.blit(sub_surf, (30, 55))

        # 2. Tarjeta: Estación de Ensamblaje Principal
        self._render_assembly_station(engine)

        # 3. Tarjeta: Cola de Órdenes Entrantes
        self._render_order_queue(engine)

        # 4. Tarjeta: Nivel de Inventario de Procesadores
        self._render_inventory_gauge(engine)

        # 5. Tarjeta: Métricas y HUD en Tiempo Real
        self._render_hud_metrics(engine, metrics)

        # 6. Panel de Trazas Recientes
        self._render_trace_log(engine)

    def _render_assembly_station(self, engine):
        """Dibuja la estación de ensamblaje con cambio de color según el estado."""
        rect = pygame.Rect(40, 100, 320, 220)
        pygame.draw.rect(self.surface, COLOR_CARD, rect, border_radius=10)
        pygame.draw.rect(self.surface, COLOR_TEXT_DIM, rect, width=2, border_radius=10)

        # Título del módulo
        t_surf = self.font_title.render("Estación de Ensamblaje", True, COLOR_TEXT)
        self.surface.blit(t_surf, (rect.x + 20, rect.y + 15))

        # Determinar color según estado
        state = engine.assembly_station.state
        if state == "LIBRE":
            box_color = COLOR_SUCCESS
            status_text = "LIBRE (Esperando Orden)"
        elif state == "OCUPADA":
            box_color = COLOR_WARNING
            curr_order = engine.assembly_station.current_order
            order_id_str = f"#{curr_order.order_id}" if curr_order else "#?"
            status_text = f"ENSAMBLANDO ÓRDEN {order_id_str}"
        else:
            box_color = COLOR_DANGER
            status_text = "DETENIDA (FALTA STOCK)"

        # Caja indicadora de la línea
        station_box = pygame.Rect(rect.x + 20, rect.y + 60, 280, 90)
        pygame.draw.rect(self.surface, box_color, station_box, border_radius=8)

        # Texto dentro de la caja de la estación
        s_surf = self.font_title.render(status_text, True, (10, 10, 10))
        text_rect = s_surf.get_rect(center=station_box.center)
        self.surface.blit(s_surf, text_rect)

        # Total ensambladas
        count_str = f"Laptops completadas: {engine.assembly_station.total_assembled}"
        c_surf = self.font_body.render(count_str, True, COLOR_TEXT)
        self.surface.blit(c_surf, (rect.x + 20, rect.y + 170))

    def _render_order_queue(self, engine):
        """Dibuja la cola visual de órdenes esperando ser armadas."""
        rect = pygame.Rect(380, 100, 480, 220)
        pygame.draw.rect(self.surface, COLOR_CARD, rect, border_radius=10)
        pygame.draw.rect(self.surface, COLOR_TEXT_DIM, rect, width=2, border_radius=10)

        t_surf = self.font_title.render(f"Cola de Espera ({len(engine.order_queue)} órdenes)", True, COLOR_TEXT)
        self.surface.blit(t_surf, (rect.x + 20, rect.y + 15))

        # Dibujar hasta 10 cajas de órdenes en la cola
        max_boxes = 10
        visible_orders = engine.order_queue[:max_boxes]
        
        box_width = 38
        box_height = 50
        start_x = rect.x + 20
        start_y = rect.y + 70

        for i, order in enumerate(visible_orders):
            box_rect = pygame.Rect(start_x + i * (box_width + 8), start_y, box_width, box_height)
            pygame.draw.rect(self.surface, COLOR_PRIMARY, box_rect, border_radius=6)
            
            num_surf = self.font_body.render(f"#{order.order_id}", True, COLOR_TEXT)
            n_rect = num_surf.get_rect(center=box_rect.center)
            self.surface.blit(num_surf, n_rect)

        if len(engine.order_queue) > max_boxes:
            more_str = f"+{len(engine.order_queue) - max_boxes} órdenes más..."
            m_surf = self.font_body.render(more_str, True, COLOR_WARNING)
            self.surface.blit(m_surf, (rect.x + 20, start_y + 65))
        elif len(engine.order_queue) == 0:
            empty_surf = self.font_body.render("Cola vacía. Sin retrasos.", True, COLOR_TEXT_DIM)
            self.surface.blit(empty_surf, (rect.x + 20, start_y + 20))

        # Información estadística de la cola
        wait_info = f"Tiempo de espera promedio: {engine.get_metrics()['tiempo_espera_promedio_min']:.2f} min"
        w_surf = self.font_body.render(wait_info, True, COLOR_TEXT)
        self.surface.blit(w_surf, (rect.x + 20, rect.y + 170))

    def _render_inventory_gauge(self, engine):
        """Dibuja el medidor gráfico del stock de procesadores."""
        rect = pygame.Rect(40, 340, 320, 220)
        pygame.draw.rect(self.surface, COLOR_CARD, rect, border_radius=10)
        pygame.draw.rect(self.surface, COLOR_TEXT_DIM, rect, width=2, border_radius=10)

        t_surf = self.font_title.render("Inventario de Procesadores", True, COLOR_TEXT)
        self.surface.blit(t_surf, (rect.x + 20, rect.y + 15))

        stock = engine.inventory.stock
        max_stock = 50
        fill_pct = min(1.0, max(0.0, stock / max_stock))

        # Determinar color de la barra
        if stock < engine.inventory.threshold:
            bar_color = COLOR_DANGER
        elif stock <= 20:
            bar_color = COLOR_WARNING
        else:
            bar_color = COLOR_SUCCESS

        # Barra de progreso
        bar_bg = pygame.Rect(rect.x + 20, rect.y + 65, 280, 35)
        pygame.draw.rect(self.surface, (20, 25, 35), bar_bg, border_radius=6)
        
        fill_rect = pygame.Rect(bar_bg.x, bar_bg.y, int(bar_bg.width * fill_pct), bar_bg.height)
        pygame.draw.rect(self.surface, bar_color, fill_rect, border_radius=6)
        pygame.draw.rect(self.surface, COLOR_TEXT_DIM, bar_bg, width=2, border_radius=6)

        val_surf = self.font_body.render(f"Stock: {stock} / {max_stock} unidades", True, COLOR_TEXT)
        v_rect = val_surf.get_rect(center=bar_bg.center)
        self.surface.blit(val_surf, v_rect)

        # Estado del reabastecimiento
        if engine.inventory.is_reorder_in_transit:
            reorder_str = f" [!] PEDIDO EN CAMINO (+{engine.inventory.batch_size})"
            r_color = COLOR_WARNING
        else:
            reorder_str = f" Umbral crítico: {engine.inventory.threshold} unidades"
            r_color = COLOR_TEXT_DIM

        r_surf = self.font_body.render(reorder_str, True, r_color)
        self.surface.blit(r_surf, (rect.x + 20, rect.y + 120))

        stoppages_str = f"Paradas por stock: {engine.inventory.line_stoppage_count} veces"
        s_surf = self.font_body.render(stoppages_str, True, COLOR_DANGER if engine.inventory.line_stoppage_count > 0 else COLOR_TEXT)
        self.surface.blit(s_surf, (rect.x + 20, rect.y + 160))

    def _render_hud_metrics(self, engine, metrics: Dict[str, Any]):
        """Dibuja el panel principal de métricas en pantalla."""
        rect = pygame.Rect(380, 340, 480, 220)
        pygame.draw.rect(self.surface, COLOR_CARD, rect, border_radius=10)
        pygame.draw.rect(self.surface, COLOR_TEXT_DIM, rect, width=2, border_radius=10)

        t_surf = self.font_title.render("Métricas Clave en Tiempo Real", True, COLOR_TEXT)
        self.surface.blit(t_surf, (rect.x + 20, rect.y + 15))

        lines = [
            f"• Órdenes Totales Recibidas : {metrics.get('total_ordenes_recibidas', 0)}",
            f"• Órdenes Completadas     : {metrics.get('total_ordenes_completadas', 0)}",
            f"• Tiempo Espera Promedio   : {metrics.get('tiempo_espera_promedio_min', 0.0):.2f} min",
            f"• Tiempo Despacho Lote     : {metrics.get('tiempo_total_despacho_lote_min', 0.0):.2f} min",
            f"• Eficiencia Reabastecimiento: {metrics.get('eficiencia_reabastecimiento_pct', 100.0):.1f}%",
            f"• Duración Paradas Stock   : {metrics.get('duracion_total_paradas_min', 0.0):.2f} min"
        ]

        for idx, line in enumerate(lines):
            l_surf = self.font_body.render(line, True, COLOR_TEXT)
            self.surface.blit(l_surf, (rect.x + 20, rect.y + 55 + idx * 24))

    def _render_trace_log(self, engine):
        """Dibuja el visor de trazas en la parte inferior."""
        rect = pygame.Rect(40, 575, 820, 100)
        pygame.draw.rect(self.surface, (15, 20, 28), rect, border_radius=8)
        pygame.draw.rect(self.surface, COLOR_TEXT_DIM, rect, width=1, border_radius=8)

        t_surf = self.font_body.render("Últimos Registros de Trazas (Live Log):", True, COLOR_ACCENT)
        self.surface.blit(t_surf, (rect.x + 15, rect.y + 10))

        recent_traces = engine.traces[-3:] if engine.traces else ["Esperando inicio de eventos..."]
        for idx, tr in enumerate(recent_traces):
            tr_surf = self.font_body.render(tr, True, COLOR_TEXT_DIM)
            self.surface.blit(tr_surf, (rect.x + 15, rect.y + 32 + idx * 20))
