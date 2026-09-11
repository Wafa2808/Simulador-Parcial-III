"""
================================================================================
UNIVERSIDAD JOSÉ ANTONIO PÁEZ - FACULTAD DE INGENIERÍA - ESCUELA DE COMPUTACIÓN
PARCIAL III. SIMULACIÓN Y MÉTODOS CUANTITATIVOS ( TRABAJO PRÁCTICO )
================================================================================
Programa Principal de Consola (Main Loop)
-----------------------------------------
Integra los modelos POO de Simulación de Eventos Discretos y Simulación Continua,
servicio de Inteligencia Artificial, almacenamiento de trazas y archivos de texto,
validación de entradas y la interfaz animada interactiva en Pygame (Bonus).
"""

import sys
import os

# Asegurar que los módulos del proyecto sean importables independientemente del CWD
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import config
from models.discrete_event import DiscreteSimulationEngine
from models.continuous import ContinuousSimulationEngine
from services.input_validator import InputValidator
from services.logger_service import LoggerService
from services.ai_service import AIService


def show_header():
    """Muestra el encabezado académico oficial en pantalla."""
    print("=" * 80)
    print("      UNIVERSIDAD JOSÉ ANTONIO PÁEZ - FACULTAD DE INGENIERÍA")
    print("            ESCUELA DE INGENIERÍA EN COMPUTACIÓN")
    print("         PARCIAL III. SIMULACIÓN Y MÉTODOS CUANTITATIVOS")
    print("=" * 80)


def run_discrete_simulation(ai_provider: str, api_key: str):
    """Ejecuta el Problema 1: Simulación de Eventos Discretos (Fábrica de Laptops)."""
    print("\n" + "-" * 70)
    print("  PROBLEMA 1: SIMULACIÓN DE EVENTOS DISCRETOS (FÁBRICA DE LAPTOPS)")
    print("-" * 70)
    print("Parámetros del Sistema:")
    print(f" • Tasa de llegada (Poisson)        : {config.ARRIVAL_RATE_LAMBDA} órdenes/hora")
    print(f" • Ensamblaje (Exponencial)         : Media {config.ASSEMBLY_MEAN_SERVICE_MINUTES} minutos/laptop")
    print(f" • Stock inicial procesadores        : {config.INITIAL_PROCESSOR_STOCK} unidades")
    print(f" • Umbral crítico reabastecimiento  : {config.INVENTORY_THRESHOLD} unidades")
    print(f" • Lote entrega / Tiempo proveedor  : {config.REORDER_BATCH_SIZE} unids / {config.REORDER_LEAD_TIME_MINUTES} min")
    print("-" * 70)

    # Solicitar horas con datos por defecto y validación
    hours = InputValidator.get_float(
        prompt="Ingrese la duración de la simulación en HORAS",
        default=config.DEFAULT_DISCRETE_HOURS,
        min_val=0.5,
        max_val=168.0
    )

    print(f"\n[SISTEMA] Iniciando motor de simulación de eventos discretos durante {hours} horas...")
    engine = DiscreteSimulationEngine(hours=hours)
    metrics = engine.run()

    # 1. Mostrar resumen de métricas por pantalla
    LoggerService.display_metrics_summary("Métricas de la Simulación de Eventos Discretos", metrics)

    # 2. Guardar archivo de trazas
    LoggerService.save_traces(config.FILE_DISCRETE_TRACE, metrics.get("trazas", []))

    # 3. Enviar a la API de Inteligencia Artificial para análisis y conclusiones
    ai_service = AIService(provider=ai_provider, api_key=api_key)
    ai_report = ai_service.generate_analysis("discrete", metrics)

    # 4. Mostrar conclusión por pantalla
    print("\n" + "=" * 70)
    print("  CONCLUSIÓN Y RECOMENDACIÓN DE LA INTELIGENCIA ARTIFICIAL")
    print("=" * 70)
    print(ai_report)
    print("=" * 70 + "\n")

    # 5. Guardar reporte consolidado en archivo de texto
    LoggerService.save_ai_report(config.FILE_DISCRETE_AI_REPORT, "Fábrica de Laptops (Eventos Discretos)", metrics, ai_report)
    input("\nPresione ENTER para regresar al menú principal...")


def run_continuous_simulation(ai_provider: str, api_key: str):
    """Ejecuta el Problema 2: Simulación Continua (Clúster de Servidores)."""
    print("\n" + "-" * 70)
    print("  PROBLEMA 2: SIMULACIÓN CONTINUA (CLÚSTER DE SERVIDORES Y CENTRO DE DATOS)")
    print("-" * 70)
    print("Parámetros del Sistema:")
    print(f" • Tráfico entrante (Normal)         : Media {config.TRAFFIC_MEAN_GBPS} Gbps, Std {config.TRAFFIC_STD_GBPS} Gbps (Rango [1, 5] Gbps)")
    print(f" • Temperatura objetivo / Ambiente   : {config.BASELINE_TEMP_CELSIUS}°C / {config.AMBIENT_TEMP_CELSIUS}°C")
    print(f" • Umbral estrangulamiento térmico   : {config.CRITICAL_THROTTLE_TEMP_CELSIUS}°C")
    print(f" • Eficiencia nominal                : {config.BASE_EFFICIENCY * 100:.0f}% a T <= 70°C")
    print("-" * 70)

    # Solicitar horas con datos por defecto y validación
    hours = InputValidator.get_float(
        prompt="Ingrese la duración de la simulación en HORAS",
        default=config.DEFAULT_CONTINUOUS_HOURS,
        min_val=0.5,
        max_val=168.0
    )

    print(f"\n[SISTEMA] Ejecutando simulación continua por integración de Euler ({hours} horas)...")
    engine = ContinuousSimulationEngine(hours=hours, dt=config.TIME_STEP_SECONDS)
    metrics = engine.run()

    # 1. Mostrar resumen de métricas
    LoggerService.display_metrics_summary("Métricas de la Simulación Continua del Clúster", metrics)

    # 2. Guardar trazas
    LoggerService.save_traces(config.FILE_CONTINUOUS_TRACE, metrics.get("trazas", []))

    # 3. Enviar métricas a la API de IA
    ai_service = AIService(provider=ai_provider, api_key=api_key)
    ai_report = ai_service.generate_analysis("continuous", metrics)

    # 4. Mostrar conclusión por pantalla
    print("\n" + "=" * 70)
    print("  CONCLUSIÓN Y RECOMENDACIÓN DE LA INTELIGENCIA ARTIFICIAL")
    print("=" * 70)
    print(ai_report)
    print("=" * 70 + "\n")

    # 5. Guardar reporte de IA en archivo de texto
    LoggerService.save_ai_report(config.FILE_CONTINUOUS_AI_REPORT, "Clúster de Servidores (Continua)", metrics, ai_report)
    input("\nPresione ENTER para regresar al menú principal...")


def run_pygame_visualization():
    """Ejecuta la animación interactiva Pygame (Pregunta Bonus)."""
    print("\n" + "-" * 70)
    print("  BONUS (2 PTOS): ANIMACIÓN DE LA SIMULACIÓN EN PYGAME")
    print("-" * 70)
    print(" Seleccione la simulación que desea visualizar:")
    print(" 1. Problema 1: Visualizar Cola de Órdenes, Estación de Ensamblaje e Inventario")
    print(" 2. Problema 2: Visualizar Nodo Servidor, Barra Térmica y Tráfico de Red")
    print(" 3. Volver al Menú Principal")

    choice = InputValidator.get_option("Seleccione una opción (1-3)", ["1", "2", "3"], default="1")
    if choice == "3":
        return

    hours = InputValidator.get_float("Ingrese horas simuladas para la animación", default=4.0, min_val=0.5, max_val=24.0)

    try:
        from visualization.pygame_animator import PygameAnimator
        mode = "discrete" if choice == "1" else "continuous"
        animator = PygameAnimator(mode=mode, hours=hours)
        animator.run()
    except Exception as e:
        print(f"\n[ERROR EN PYGAME] No se pudo lanzar la ventana de Pygame: {e}")
        print("Asegúrese de contar con un entorno gráfico habilitado.")

    input("\nPresione ENTER para regresar al menú principal...")


def configure_ai_service(current_provider: str, current_key: str):
    """Permite seleccionar el proveedor de IA y configurar la API Key."""
    print("\n" + "-" * 70)
    print("  CONFIGURACIÓN DE SERVICIO DE INTELIGENCIA ARTIFICIAL")
    print("-" * 70)
    print(f"Proveedor actual: {current_provider.upper()}")
    print("Seleccione el proveedor deseado:")
    print(" 1. Fallback / Motor Experto Local (Respuesta inmediata sin API key)")
    print(" 2. Google Gemini API REST (Requiere GEMINI_API_KEY)")
    print(" 3. OpenAI GPT API REST (Requiere OPENAI_API_KEY)")
    print(" 4. Ollama Local LLM (Servidor http://localhost:11434)")

    choice = InputValidator.get_option("Seleccione una opción (1-4)", ["1", "2", "3", "4"], default="1")

    providers = {"1": "auto", "2": "gemini", "3": "openai", "4": "ollama"}
    new_provider = providers[choice]

    new_key = current_key
    if new_provider in ["gemini", "openai"]:
        input_key = input(f"Ingrese su API Key para {new_provider.upper()} (dejar vacío para mantener la actual): ").strip()
        if input_key:
            new_key = input_key

    print(f"\n[EXITO] Proveedor configurado como: '{new_provider.upper()}'")
    return new_provider, new_key


def main():
    """Bucle principal de la aplicación."""
    ai_provider = "auto"
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY") or ""

    while True:
        os.system("cls" if os.name == "nt" else "clear")
        show_header()
        print("                        MENÚ PRINCIPAL DE OPCIONES")
        print("=" * 80)
        print(" 1. Simulación de Eventos Discretos (Fábrica de Laptops)")
        print(" 2. Simulación Continua (Clúster de Servidores y Balance Térmico)")
        print(" 3. Visualización Interactiva Animada en Pygame (Bonus 2 Puntos)")
        print(" 4. Configuración de API de Inteligencia Artificial")
        print(" 5. Salir del Programa")
        print("=" * 80)

        choice = InputValidator.get_option("Seleccione una opción [1-5]", ["1", "2", "3", "4", "5"], default="1")

        if choice == "1":
            run_discrete_simulation(ai_provider, api_key)
        elif choice == "2":
            run_continuous_simulation(ai_provider, api_key)
        elif choice == "3":
            run_pygame_visualization()
        elif choice == "4":
            ai_provider, api_key = configure_ai_service(ai_provider, api_key)
            input("\nPresione ENTER para continuar...")
        elif choice == "5":
            print("\n¡Gracias por utilizar el sistema de simulación! Cerrando programa...")
            break


if __name__ == "__main__":
    main()
