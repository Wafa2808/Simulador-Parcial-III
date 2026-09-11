"""
Módulo de Simulación de Eventos Discretos: Fábrica de Laptops
-------------------------------------------------------------
Este módulo implementa el paradigma de simulación de eventos discretos en POO
para evaluar la eficiencia de la estación de ensamblaje de laptops y la gestión
del inventario de procesadores.

Clases principales:
- Order: Representa una orden de producción.
- ProcessorInventory: Controla el stock, los umbrales de reabastecimiento y entregas.
- AssemblyStation: Controla el estado físico de la línea de producción.
- DiscreteEvent: Eventos discretos ordenados por tiempo.
- DiscreteSimulationEngine: Motor de ejecución de simulación por eventos discretos.
"""

import heapq
import random
from typing import List, Dict, Any, Optional

from config import (
    DEFAULT_DISCRETE_HOURS,
    ARRIVAL_RATE_LAMBDA,
    ASSEMBLY_MEAN_SERVICE_MINUTES,
    INITIAL_PROCESSOR_STOCK,
    INVENTORY_THRESHOLD,
    REORDER_BATCH_SIZE,
    REORDER_LEAD_TIME_MINUTES
)


class Order:
    """Representa una orden de fabricación de laptop dentro del sistema."""

    def __init__(self, order_id: int, arrival_time: float):
        self.order_id: int = order_id
        self.arrival_time: float = arrival_time           # Tiempo simulado de llegada (minutos)
        self.service_start_time: Optional[float] = None   # Tiempo de inicio de ensamblaje (minutos)
        self.completion_time: Optional[float] = None      # Tiempo de finalización (minutos)
        self.status: str = "QUEUED"                      # QUEUED, IN_ASSEMBLY, WAITING_INVENTORY, COMPLETED
        self.wait_time: float = 0.0                      # Tiempo gastado esperando en la cola (minutos)

    def start_assembly(self, current_time: float):
        """Marca el inicio del proceso de ensamblaje."""
        self.service_start_time = current_time
        self.wait_time = current_time - self.arrival_time
        self.status = "IN_ASSEMBLY"

    def complete_assembly(self, current_time: float):
        """Marca la finalización de la laptop."""
        self.completion_time = current_time
        self.status = "COMPLETED"

    def __repr__(self) -> str:
        return f"<Orden #{self.order_id} | Estado: {self.status} | Espera: {self.wait_time:.2f} min>"


class ProcessorInventory:
    """Gestiona el inventario de procesadores de gama alta y los pedidos al proveedor."""

    def __init__(self, initial_stock: int = INITIAL_PROCESSOR_STOCK,
                 threshold: int = INVENTORY_THRESHOLD,
                 batch_size: int = REORDER_BATCH_SIZE,
                 lead_time: float = REORDER_LEAD_TIME_MINUTES):
        self.stock: int = initial_stock
        self.threshold: int = threshold
        self.batch_size: int = batch_size
        self.lead_time: float = lead_time
        self.is_reorder_in_transit: bool = False
        self.total_reorders: int = 0
        self.successful_replenishments: int = 0
        self.line_stoppage_count: int = 0
        self.total_stoppage_duration: float = 0.0

    def has_stock(self) -> bool:
        """Verifica si hay al menos un procesador disponible."""
        return self.stock > 0

    def consume_processor(self) -> bool:
        """Consume 1 unidad de procesador si hay disponible."""
        if self.stock > 0:
            self.stock -= 1
            return True
        return False

    def should_reorder(self) -> bool:
        """Determina si se debe solicitar un pedido de reabastecimiento."""
        return self.stock < self.threshold and not self.is_reorder_in_transit

    def trigger_reorder(self):
        """Inicia el proceso de reabastecimiento automáticamente."""
        self.is_reorder_in_transit = True
        self.total_reorders += 1

    def receive_reorder(self):
        """Recibe el lote entregado por el proveedor y restablece el estado."""
        self.stock += self.batch_size
        self.is_reorder_in_transit = False
        self.successful_replenishments += 1


class AssemblyStation:
    """Representa la estación principal de ensamblaje de la fábrica."""

    STATE_FREE = "LIBRE"
    STATE_BUSY = "OCUPADA"
    STATE_STOPPED = "DETENIDA_SIN_STOCK"

    def __init__(self):
        self.state: str = self.STATE_FREE
        self.current_order: Optional[Order] = None
        self.total_assembled: int = 0
        self.total_busy_time: float = 0.0

    def assign_order(self, order: Order):
        """Asigna una orden a la estación."""
        self.current_order = order
        self.state = self.STATE_BUSY

    def set_stopped(self):
        """Pone la estación en estado de detención por falta de componentes."""
        self.state = self.STATE_STOPPED

    def release(self):
        """Libera la estación tras completar una orden."""
        self.current_order = None
        self.state = self.STATE_FREE


class DiscreteEvent:
    """Clase interna para ordenar los eventos discretos en una cola de prioridad."""

    EVENT_ORDER_ARRIVAL = 1
    EVENT_ASSEMBLY_COMPLETE = 2
    EVENT_REORDER_DELIVERY = 3

    def __init__(self, time: float, event_type: int, data: Any = None):
        self.time: float = time
        self.event_type: int = event_type
        self.data: Any = data

    def __lt__(self, other: 'DiscreteEvent') -> bool:
        return self.time < other.time


class DiscreteSimulationEngine:
    """Motor principal de la Simulación de Eventos Discretos."""

    def __init__(self, hours: float = DEFAULT_DISCRETE_HOURS):
        self.total_simulation_minutes: float = hours * 60.0
        self.current_time: float = 0.0
        self.event_queue: List[DiscreteEvent] = []
        
        # Componentes POO
        self.inventory: ProcessorInventory = ProcessorInventory()
        self.assembly_station: AssemblyStation = AssemblyStation()
        
        # Estructuras de datos
        self.order_queue: List[Order] = []
        self.completed_orders: List[Order] = []
        self.delayed_orders_count: int = 0
        self.order_counter: int = 0
        
        # Trazas de ejecución
        self.traces: List[str] = []
        
        # Medición de paradas de línea
        self.stoppage_start_time: Optional[float] = None

    def log_trace(self, message: str):
        """Agrega un registro con marca de tiempo simulada a las trazas."""
        hours = int(self.current_time // 60)
        minutes = int(self.current_time % 60)
        seconds = int((self.current_time * 60) % 60)
        timestamp = f"[{hours:02d}:{minutes:02d}:{seconds:02d}]"
        trace_entry = f"{timestamp} {message}"
        self.traces.append(trace_entry)

    def schedule_event(self, time: float, event_type: int, data: Any = None):
        """Planifica un nuevo evento discreto en la cola de prioridad."""
        event = DiscreteEvent(time, event_type, data)
        heapq.heappush(self.event_queue, event)

    def _generate_interarrival_time(self) -> float:
        """Genera el tiempo entre llegadas según distribución Exponencial (Poisson λ=10 por hora = 1 cada 6 min)."""
        # λ = 10 órdenes/hora => 1/6 órdenes/min. Media = 6 minutos.
        mean_interarrival = 60.0 / ARRIVAL_RATE_LAMBDA
        return random.expovariate(1.0 / mean_interarrival)

    def _generate_service_time(self) -> float:
        """Genera el tiempo de ensamblaje según distribución Exponencial (media = 5 min)."""
        return random.expovariate(1.0 / ASSEMBLY_MEAN_SERVICE_MINUTES)

    def run(self) -> Dict[str, Any]:
        """Ejecuta la simulación por eventos discretos durante el tiempo especificado."""
        self.log_trace(f"--- INICIO DE SIMULACIÓN DISCRETA ({self.total_simulation_minutes / 60:.2f} HORAS) ---")
        self.log_trace(f"Inventario Inicial: {self.inventory.stock} procesadores. Umbral: {self.inventory.threshold}.")

        # Programar la primera llegada de orden
        first_arrival = self._generate_interarrival_time()
        if first_arrival <= self.total_simulation_minutes:
            self.order_counter += 1
            first_order = Order(self.order_counter, first_arrival)
            self.schedule_event(first_arrival, DiscreteEvent.EVENT_ORDER_ARRIVAL, first_order)

        # Bucle principal de eventos discretos
        while self.event_queue:
            event = heapq.heappop(self.event_queue)
            
            if event.time > self.total_simulation_minutes:
                # Actualizar el tiempo al límite final de la simulación
                self.current_time = self.total_simulation_minutes
                break

            self.current_time = event.time

            if event.event_type == DiscreteEvent.EVENT_ORDER_ARRIVAL:
                self._handle_order_arrival(event.data)
            elif event.event_type == DiscreteEvent.EVENT_ASSEMBLY_COMPLETE:
                self._handle_assembly_complete(event.data)
            elif event.event_type == DiscreteEvent.EVENT_REORDER_DELIVERY:
                self._handle_reorder_delivery()

        # Si finalizó la simulación mientras la línea estaba detenida, registrar el tiempo transcurrido
        if self.stoppage_start_time is not None:
            self.inventory.total_stoppage_duration += (self.total_simulation_minutes - self.stoppage_start_time)
            self.stoppage_start_time = None

        self.log_trace(f"--- FIN DE SIMULACIÓN DISCRETA A LAS {self.total_simulation_minutes / 60:.2f} HORAS ---")
        return self.get_metrics()

    def _handle_order_arrival(self, order: Order):
        """Maneja el evento de llegada de una nueva orden."""
        self.log_trace(f"LLEGADA: Órden #{order.order_id} recibida. En cola: {len(self.order_queue) + 1}")
        self.order_queue.append(order)

        # Programar la siguiente llegada
        next_arrival_time = self.current_time + self._generate_interarrival_time()
        if next_arrival_time <= self.total_simulation_minutes:
            self.order_counter += 1
            next_order = Order(self.order_counter, next_arrival_time)
            self.schedule_event(next_arrival_time, DiscreteEvent.EVENT_ORDER_ARRIVAL, next_order)

        # Intentar procesar la cola
        self._try_start_next_assembly()

    def _try_start_next_assembly(self):
        """Intenta iniciar el ensamblaje de la siguiente orden en cola si la estación está libre."""
        if self.assembly_station.state == AssemblyStation.STATE_BUSY or not self.order_queue:
            return

        # Hay órdenes esperando y la estación no está ocupada armando
        if self.inventory.has_stock():
            # Si la línea estaba detenida por falta de stock, registrar reanudación
            if self.assembly_station.state == AssemblyStation.STATE_STOPPED:
                if self.stoppage_start_time is not None:
                    duration = self.current_time - self.stoppage_start_time
                    self.inventory.total_stoppage_duration += duration
                    self.stoppage_start_time = None
                self.log_trace("LÍNEA REANUDADA: Stock recibido, continuando ensamblaje.")

            # Consumir procesador e iniciar ensamblaje
            self.inventory.consume_processor()
            order = self.order_queue.pop(0)
            order.start_assembly(self.current_time)
            self.assembly_station.assign_order(order)

            service_duration = self._generate_service_time()
            completion_time = self.current_time + service_duration

            self.log_trace(
                f"ENSAMBLAJE INICIADO: Órden #{order.order_id} en proceso ({service_duration:.2f} min). "
                f"Procesadores restantes: {self.inventory.stock}"
            )
            self.schedule_event(completion_time, DiscreteEvent.EVENT_ASSEMBLY_COMPLETE, order)

            # Verificar si el stock cayó por debajo del umbral para pedir reabastecimiento
            self._check_inventory_threshold()
        else:
            # No hay stock disponible
            if self.assembly_station.state != AssemblyStation.STATE_STOPPED:
                self.assembly_station.set_stopped()
                self.inventory.line_stoppage_count += 1
                self.delayed_orders_count += 1
                self.stoppage_start_time = self.current_time
                self.log_trace(
                    f"ALERTA CRÍTICA: Línea detenida por FALTA DE STOCK (Órden #{self.order_queue[0].order_id} retrasada)."
                )

            # También verificar si se debe pedir reabastecimiento
            self._check_inventory_threshold()

    def _check_inventory_threshold(self):
        """Verifica si el inventario cayó por debajo del umbral y dispara la orden al proveedor."""
        if self.inventory.should_reorder():
            self.inventory.trigger_reorder()
            delivery_time = self.current_time + self.inventory.lead_time
            self.log_trace(
                f"REABASTECIMIENTO SOLICITADO: Stock ({self.inventory.stock}) < Umbral ({self.inventory.threshold}). "
                f"Lote de {self.inventory.batch_size} llegará a los {self.inventory.lead_time} min."
            )
            self.schedule_event(delivery_time, DiscreteEvent.EVENT_REORDER_DELIVERY)

    def _handle_assembly_complete(self, order: Order):
        """Maneja la finalización de ensamblaje de una orden."""
        order.complete_assembly(self.current_time)
        self.completed_orders.append(order)
        self.assembly_station.total_assembled += 1
        
        self.log_trace(f"ENSAMBLAJE COMPLETADO: Órden #{order.order_id} lista. Tiempo total en fábrica: {order.completion_time - order.arrival_time:.2f} min.")
        self.assembly_station.release()

        # Intentar iniciar la siguiente orden en cola
        self._try_start_next_assembly()

    def _handle_reorder_delivery(self):
        """Maneja la entrega del lote de procesadores por parte del proveedor."""
        self.inventory.receive_reorder()
        self.log_trace(
            f"REABASTECIMIENTO ENTREGADO: +{self.inventory.batch_size} procesadores recibidos del proveedor. "
            f"Nuevo Stock: {self.inventory.stock}"
        )
        # Intentar reanudar ensamblaje si había órdenes esperando por falta de stock
        self._try_start_next_assembly()

    def get_metrics(self) -> Dict[str, Any]:
        """Calcula y compila todas las métricas requeridas por el enunciado del parcial."""
        total_orders = len(self.completed_orders)
        
        if total_orders > 0:
            avg_wait_time = sum(o.wait_time for o in self.completed_orders) / total_orders
            avg_total_time = sum(o.completion_time - o.arrival_time for o in self.completed_orders) / total_orders
            dispatch_total_time = self.completed_orders[-1].completion_time
        else:
            avg_wait_time = 0.0
            avg_total_time = 0.0
            dispatch_total_time = 0.0

        replenishment_efficiency = (
            (self.inventory.successful_replenishments / self.inventory.total_reorders * 100.0)
            if self.inventory.total_reorders > 0 else 100.0
        )

        return {
            "duracion_simulada_horas": self.total_simulation_minutes / 60.0,
            "total_ordenes_recibidas": self.order_counter,
            "total_ordenes_completadas": total_orders,
            "ordenes_en_cola": len(self.order_queue),
            "tiempo_espera_promedio_min": round(avg_wait_time, 2),
            "tiempo_permanencia_promedio_min": round(avg_total_time, 2),
            "tiempo_total_despacho_lote_min": round(dispatch_total_time, 2),
            "paradas_linea_falta_stock": self.inventory.line_stoppage_count,
            "duracion_total_paradas_min": round(self.inventory.total_stoppage_duration, 2),
            "ordenes_retrasadas_falta_inventario": self.delayed_orders_count,
            "stock_final_procesadores": self.inventory.stock,
            "total_reabastecimientos_pedidos": self.inventory.total_reorders,
            "eficiencia_reabastecimiento_pct": round(replenishment_efficiency, 2),
            "trazas": self.traces
        }
