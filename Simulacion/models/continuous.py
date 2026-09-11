"""
Módulo de Simulación Continua: Clúster de Servidores del Centro de Datos
-------------------------------------------------------------------------
Este módulo implementa una simulación en tiempo continuo utilizando
integración numérica (método de Euler) para modelar el comportamiento térmico
y el rendimiento de un clúster de servidores de alto rendimiento.

Clases principales:
- TrafficGenerator: Genera tasa variable de tráfico entrante (distribución normal).
- ThermalModel: Resuelve la ecuación diferencial de balance térmico y estrangulamiento.
- ServerCluster: Mide el rendimiento de datos procesados (Terabytes) y eficiencia.
- ContinuousSimulationEngine: Ejecuta el bucle de integración continua y registra trazas.
"""

import math
import random
from typing import List, Dict, Any

from config import (
    DEFAULT_CONTINUOUS_HOURS,
    TIME_STEP_SECONDS,
    TRAFFIC_MEAN_GBPS,
    TRAFFIC_STD_GBPS,
    TRAFFIC_MIN_GBPS,
    TRAFFIC_MAX_GBPS,
    BASELINE_TEMP_CELSIUS,
    AMBIENT_TEMP_CELSIUS,
    CRITICAL_THROTTLE_TEMP_CELSIUS,
    HEAT_GENERATION_RATE,
    HEAT_DISSIPATION_RATE,
    BASE_EFFICIENCY
)


class TrafficGenerator:
    """Genera el flujo continuo de tráfico de red (Gbps) según distribución normal."""

    def __init__(self, mean: float = TRAFFIC_MEAN_GBPS,
                 std: float = TRAFFIC_STD_GBPS,
                 min_gbps: float = TRAFFIC_MIN_GBPS,
                 max_gbps: float = TRAFFIC_MAX_GBPS):
        self.mean: float = mean
        self.std: float = std
        self.min_gbps: float = min_gbps
        self.max_gbps: float = max_gbps

    def get_current_traffic(self) -> float:
        """Genera un valor de tráfico en Gbps acotado entre [min_gbps, max_gbps]."""
        traffic = random.gauss(self.mean, self.std)
        # Acotar la distribución al rango permitido por la especificación [1 Gbps, 5 Gbps]
        return max(self.min_gbps, min(self.max_gbps, traffic))


class ThermalModel:
    """
    Modela el balance térmico del servidor mediante la ecuación diferencial de primer orden:
    dT/dt = k_gen * Tráfico - k_dis * (T - T_ambiente)
    """

    def __init__(self, initial_temp: float = BASELINE_TEMP_CELSIUS,
                 ambient_temp: float = AMBIENT_TEMP_CELSIUS,
                 k_gen: float = HEAT_GENERATION_RATE,
                 k_dis: float = HEAT_DISSIPATION_RATE,
                 throttle_threshold: float = CRITICAL_THROTTLE_TEMP_CELSIUS):
        self.current_temp: float = initial_temp
        self.ambient_temp: float = ambient_temp
        self.k_gen: float = k_gen
        self.k_dis: float = k_dis
        self.throttle_threshold: float = throttle_threshold
        self.is_throttling: bool = False

    def update_temperature(self, traffic_gbps: float, dt_seconds: float) -> float:
        """
        Aplica el paso de integración numérica de Euler para calcular la nueva temperatura.
        dt_seconds se convierte a minutos/fracción de tiempo adecuada para la tasa de transferencia.
        """
        dt_minutes = dt_seconds / 60.0  # Escalar la constante de tiempo a minutos
        
        heat_generated = self.k_gen * traffic_gbps
        heat_dissipated = self.k_dis * (self.current_temp - self.ambient_temp)
        
        dT_dt = heat_generated - heat_dissipated
        self.current_temp += dT_dt * dt_minutes

        # Evaluar si el sistema activa estrangulamiento térmico (thermal throttling)
        self.is_throttling = self.current_temp > self.throttle_threshold
        return self.current_temp


class ServerCluster:
    """Mide la cantidad de datos procesados (Terabytes) y la eficiencia operacional."""

    def __init__(self, base_efficiency: float = BASE_EFFICIENCY):
        self.base_efficiency: float = base_efficiency
        self.total_gigabits_processed: float = 0.0
        self.total_throttling_seconds: float = 0.0
        self.current_efficiency: float = base_efficiency

    def calculate_efficiency(self, temperature: float) -> float:
        """
        Calcula la eficiencia actual del clúster.
        - Si T <= 70°C: Eficiencia estable del 90% (0.90).
        - Si T > 70°C: Penalización progresiva debido al calor y thermal throttling.
        """
        if temperature <= BASELINE_TEMP_CELSIUS:
            self.current_efficiency = self.base_efficiency
        else:
            # Caída de eficiencia del 5% por cada grado por encima de 70°C (mínimo 20% de eficiencia)
            overheating = temperature - BASELINE_TEMP_CELSIUS
            penalty = overheating * 0.05
            self.current_efficiency = max(0.20, self.base_efficiency - penalty)
        return self.current_efficiency

    def process_data(self, traffic_gbps: float, efficiency: float, dt_seconds: float) -> float:
        """Procesa datos durante dt_seconds y acumula los Gigabits procesados."""
        effective_throughput = traffic_gbps * efficiency
        gigabits = effective_throughput * dt_seconds
        self.total_gigabits_processed += gigabits
        return gigabits

    @property
    def total_terabytes_processed(self) -> float:
        """Convierte los Gigabits totales procesados a Terabytes (1 TB = 8,000 Gb)."""
        return self.total_gigabits_processed / 8000.0


class ContinuousSimulationEngine:
    """Motor principal de la Simulación Continua del Clúster de Servidores."""

    def __init__(self, hours: float = DEFAULT_CONTINUOUS_HOURS, dt: float = TIME_STEP_SECONDS):
        self.total_seconds: float = hours * 3600.0
        self.dt: float = dt
        self.current_time_seconds: float = 0.0
        
        # Componentes POO
        self.traffic_gen: TrafficGenerator = TrafficGenerator()
        self.thermal_model: ThermalModel = ThermalModel()
        self.cluster: ServerCluster = ServerCluster()

        # Almacenamiento de series temporales para estadísticas y gráficos
        self.history_traffic: List[float] = []
        self.history_temp: List[float] = []
        self.history_efficiency: List[float] = []
        self.history_time: List[float] = []

        # Trazas de simulación
        self.traces: List[str] = []
        self.throttling_events_count: int = 0
        self._was_throttling_previous: bool = False

    def log_trace(self, message: str):
        """Registra un mensaje con marca de tiempoHH:MM:SS."""
        hours = int(self.current_time_seconds // 3600)
        minutes = int((self.current_time_seconds % 3600) // 60)
        seconds = int(self.current_time_seconds % 60)
        timestamp = f"[{hours:02d}:{minutes:02d}:{seconds:02d}]"
        self.traces.append(f"{timestamp} {message}")

    def run(self) -> Dict[str, Any]:
        """Ejecuta la simulación continua por pasos de integración de Euler."""
        hours_total = self.total_seconds / 3600.0
        self.log_trace(f"--- INICIO DE SIMULACIÓN CONTINUA ({hours_total:.2f} HORAS) ---")
        self.log_trace(f"Temperatura Inicial del Servidor: {self.thermal_model.current_temp:.2f}°C. Meta: 70.0°C.")

        # Intervalo para registrar trazas en pantalla/archivo (ej. cada 15 minutos simulados)
        trace_interval_seconds = 900.0
        last_trace_time = -trace_interval_seconds

        while self.current_time_seconds <= self.total_seconds:
            # 1. Obtener tasa de entrada de tráfico variable (Gbps)
            traffic = self.traffic_gen.get_current_traffic()

            # 2. Actualizar temperatura con ecuación diferencial
            temp = self.thermal_model.update_temperature(traffic, self.dt)

            # 3. Calcular eficiencia y procesar datos
            efficiency = self.cluster.calculate_efficiency(temp)
            self.cluster.process_data(traffic, efficiency, self.dt)

            # Contar eventos de estrangulamiento térmico
            if self.thermal_model.is_throttling:
                self.cluster.total_throttling_seconds += self.dt
                if not self._was_throttling_previous:
                    self.throttling_events_count += 1
                    self.log_trace(
                        f"ALERTA TÉRMICA: Activado Estrangulamiento (Thermal Throttling). "
                        f"Temp: {temp:.2f}°C > Umbral ({CRITICAL_THROTTLE_TEMP_CELSIUS}°C)."
                    )
            elif self._was_throttling_previous:
                self.log_trace(
                    f"ESTABILIZACIÓN TÉRMICA: Temperatura descendió a {temp:.2f}°C. "
                    f"Estrangulamiento desactivado."
                )

            self._was_throttling_previous = self.thermal_model.is_throttling

            # Guardar en historial
            self.history_time.append(self.current_time_seconds / 3600.0)
            self.history_traffic.append(traffic)
            self.history_temp.append(temp)
            self.history_efficiency.append(efficiency)

            # Registrar traza periódica
            if self.current_time_seconds - last_trace_time >= trace_interval_seconds:
                self.log_trace(
                    f"ESTADO: Tráfico: {traffic:.2f} Gbps | Temp: {temp:.2f}°C | "
                    f"Eficiencia: {efficiency*100:.1f}% | Procesado: {self.cluster.total_terabytes_processed:.4f} TB"
                )
                last_trace_time = self.current_time_seconds

            self.current_time_seconds += self.dt

        self.log_trace(f"--- FIN DE SIMULACIÓN CONTINUA A LAS {hours_total:.2f} HORAS ---")
        return self.get_metrics()

    def get_metrics(self) -> Dict[str, Any]:
        """Compila las métricas globales requeridas por el problema 2."""
        if not self.history_temp:
            return {}

        avg_temp = sum(self.history_temp) / len(self.history_temp)
        min_temp = min(self.history_temp)
        max_temp = max(self.history_temp)
        
        # Desviación estándar de temperatura (variabilidad)
        variance = sum((t - avg_temp) ** 2 for t in self.history_temp) / len(self.history_temp)
        std_temp = math.sqrt(variance)

        avg_traffic = sum(self.history_traffic) / len(self.history_traffic)
        avg_efficiency = sum(self.history_efficiency) / len(self.history_efficiency) * 100.0

        # Porcentaje de tiempo operando en temperatura estable (<= 70°C)
        stable_counts = sum(1 for t in self.history_temp if t <= BASELINE_TEMP_CELSIUS)
        stability_percentage = (stable_counts / len(self.history_temp)) * 100.0

        return {
            "duracion_simulada_horas": self.total_seconds / 3600.0,
            "total_terabytes_procesados": round(self.cluster.total_terabytes_processed, 4),
            "trafico_promedio_gbps": round(avg_traffic, 2),
            "temperatura_promedio_celsius": round(avg_temp, 2),
            "temperatura_minima_celsius": round(min_temp, 2),
            "temperatura_maxima_celsius": round(max_temp, 2),
            "variabilidad_temperatura_std": round(std_temp, 2),
            "estabilidad_termica_pct": round(stability_percentage, 2),
            "eficiencia_global_promedio_pct": round(avg_efficiency, 2),
            "eventos_estrangulamiento_termico": self.throttling_events_count,
            "duracion_estrangulamiento_min": round(self.cluster.total_throttling_seconds / 60.0, 2),
            "trazas": self.traces
        }
