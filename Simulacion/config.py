"""
Módulo de Configuración Global de la Simulación
----------------------------------------------
Contiene los parámetros por defecto, constantes matemáticas y rutas
utilizados por los modelos de Simulación de Eventos Discretos y Continua.
"""

import os

# Ruta raíz del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

# Crear la carpeta de salidas si no existe
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# ---------------------------------------------------------
# Configuración: Problema 1 - Eventos Discretos (Laptops)
# ---------------------------------------------------------
DEFAULT_DISCRETE_HOURS = 8.0               # Duración por defecto de la simulación (horas)
ARRIVAL_RATE_LAMBDA = 10.0                 # Tasa promedio de llegada: 10 órdenes por hora (Poisson)
ASSEMBLY_MEAN_SERVICE_MINUTES = 5.0        # Tiempo promedio de ensamblaje: 5 minutos (Exponencial)

# Parámetros del Inventario
INITIAL_PROCESSOR_STOCK = 50              # Stock inicial de procesadores
INVENTORY_THRESHOLD = 10                  # Umbral crítico para reabastecimiento (unidades)
REORDER_BATCH_SIZE = 50                   # Tamaño del lote de entrega (unidades)
REORDER_LEAD_TIME_MINUTES = 15.0          # Tiempo de entrega del proveedor (minutos)

# ---------------------------------------------------------
# Configuración: Problema 2 - Simulación Continua (Clúster)
# ---------------------------------------------------------
DEFAULT_CONTINUOUS_HOURS = 8.0             # Duración por defecto de la simulación continua (horas)
TIME_STEP_SECONDS = 1.0                    # Paso de integración delta t (segundos)

# Parámetros de Tráfico de Red (Gbps)
TRAFFIC_MEAN_GBPS = 3.0                    # Media de tráfico entrante (Gbps)
TRAFFIC_STD_GBPS = 1.0                     # Desviación estándar de tráfico (Gbps)
TRAFFIC_MIN_GBPS = 1.0                     # Límite inferior de tráfico (Gbps)
TRAFFIC_MAX_GBPS = 5.0                     # Límite superior de tráfico (Gbps)

# Parámetros Térmicos del Servidor
BASELINE_TEMP_CELSIUS = 70.0               # Temperatura objetivo/base del servidor (°C)
AMBIENT_TEMP_CELSIUS = 25.0                # Temperatura ambiente del centro de datos (°C)
CRITICAL_THROTTLE_TEMP_CELSIUS = 75.0      # Temperatura a partir de la cual inicia estrangulamiento térmico (°C)
MAX_SAFE_TEMP_CELSIUS = 85.0               # Temperatura máxima de seguridad (°C)

# Constantes de Balance Térmico: dT/dt = k_gen * Tráfico - k_dis * (T - T_amb)
# Para mantener equilibrio en 70°C a 3 Gbps nominales:
# k_gen * 3.0 = k_dis * (70.0 - 25.0) => 3.0 * k_gen = 45.0 * k_dis => k_gen = 15 * k_dis
HEAT_DISSIPATION_RATE = 0.05               # Constante de disipación de calor del sistema de refrigeración
HEAT_GENERATION_RATE = 0.75                # Constante de generación de calor por Gbps de procesamiento

# Rendimiento y Eficiencia
BASE_EFFICIENCY = 0.90                     # Eficiencia nominal del 90% a T <= 70°C

# ---------------------------------------------------------
# Configuración de Archivos de Salida
# ---------------------------------------------------------
FILE_DISCRETE_TRACE = os.path.join(OUTPUTS_DIR, "trace_discreta.txt")
FILE_CONTINUOUS_TRACE = os.path.join(OUTPUTS_DIR, "trace_continua.txt")
FILE_DISCRETE_AI_REPORT = os.path.join(OUTPUTS_DIR, "reporte_ia_discreta.txt")
FILE_CONTINUOUS_AI_REPORT = os.path.join(OUTPUTS_DIR, "reporte_ia_continua.txt")
