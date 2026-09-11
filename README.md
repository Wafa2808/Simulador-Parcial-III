# Parcial III - Simulación y Métodos Cuantitativos
## Trabajo Práctico: Simulación de Eventos Discretos y Simulación Continua

**Universidad José Antonio Páez**  
**Facultad de Ingeniería - Escuela de Ingeniería en Computación**  

---

## 📋 Descripción del Proyecto

Este proyecto implementa en **Python 3** bajo el paradigma de **Programación Orientada a Objetos (POO)** la solución completa a los dos problemas de simulación solicitados en el Parcial III:

1. **Simulación de Eventos Discretos (Fábrica de Laptops)**:
   - Modela la llegada aleatoria de órdenes de laptops mediante un proceso de **Poisson** ($\lambda = 10$ órdenes/hora).
   - Tiempo de ensamblaje en estación única según una distribución **Exponencial** ($\mu = 5$ minutos/laptop).
   - Gestión automática del inventario de procesadores de gama alta: stock inicial de 50 unidades, reabastecimiento automático al caer por debajo de 10 unidades, tiempo de entrega de 15 minutos y entregas en lotes de 50 unidades.
   - Recopila métricas clave: tiempo de espera promedio, tiempo de permanencia, tiempo de despacho de lote y paradas de línea por desabastecimiento.

2. **Simulación Continua (Clúster de Servidores - Centro de Datos)**:
   - Modela un clúster de alto rendimiento recibiendo tráfico de red con distribución **Normal** ($\mu = 3$ Gbps, $\sigma = 1$ Gbps, acotado entre 1 y 5 Gbps).
   - Resuelve la **ecuación diferencial de primer orden para balance térmico**:
     $$\frac{dT}{dt} = k_{gen} \cdot \text{Tráfico} - k_{dis} \cdot (T - T_{ambiente})$$
   - Evalúa el **estrangulamiento térmico (Thermal Throttling)** a temperaturas superiores a 75°C y mide la cantidad total de **Terabytes procesados**, la variabilidad térmica y la eficiencia global.

3. **Integración con API de Inteligencia Artificial**:
   - Envía las métricas compiladas a modelos de IA (Gemini, OpenAI o Ollama local).
   - Incluye un **motor de diagnóstico experto local (fallback)** para generar conclusiones y recomendaciones automatizadas de forma 100% autónoma y sin errores en cualquier entorno.

4. **Animación Gráfica Interactiva con Pygame (Pregunta Bonus - 2 Puntos)**:
   - Interfaz visual en tiempo real para ambos problemas.
   - Representación de cola de órdenes, estación de ensamblaje (colores por estado) e indicador de inventario.
   - Nodo de servidor con medidor térmico por gradiente de color (Azul $\to$ Verde $\to$ Amarillo $\to$ Rojo crítico) y gráfica de tráfico.
   - HUD dinámico y controles de teclado (`ESPACIO` para pausar/reanudar, `FLECHAS ARRIBA/ABAJO` para ajustar velocidad, `ESC` para salir).

---

## 📁 Estructura del Proyecto (`Simulacion/`)

```
Simulacion/
├── config.py                   # Constantes globales, parámetros predeterminados y rutas
├── main.py                     # Menú principal interactivo en consola
├── README.md                   # Documentación oficial del proyecto
│
├── models/                     # Clases y Lógica Orientada a Objetos
│   ├── __init__.py
│   ├── discrete_event.py       # Order, ProcessorInventory, AssemblyStation, DiscreteSimulationEngine
│   └── continuous.py          # TrafficGenerator, ThermalModel, ServerCluster, ContinuousSimulationEngine
│
├── services/                   # Servicios Auxiliares
│   ├── __init__.py
│   ├── ai_service.py           # Integrador de API de IA (Gemini/OpenAI/Ollama + Fallback Local)
│   ├── logger_service.py       # Consola y exportador de trazas y reportes a texto (.txt)
│   └── input_validator.py      # Validación de entrada con soporte para datos por defecto
│
├── visualization/              # Módulo de Animación Pygame (Bonus 2 Ptos)
│   ├── __init__.py
│   ├── pygame_animator.py      # Gestor del bucle Pygame y sincronización POO
│   ├── discrete_vis.py         # Visualizador del Problema 1
│   └── continuous_vis.py       # Visualizador del Problema 2
│
└── outputs/                    # Archivos de salida generados (.txt)
    ├── trace_discreta.txt
    ├── trace_continua.txt
    ├── reporte_ia_discreta.txt
    └── reporte_ia_continua.txt
```

---

## 🚀 Instrucciones de Ejecución

Para iniciar la aplicación, ejecuta el archivo `main.py` dentro de la carpeta `Simulacion`:

```bash
python Simulacion/main.py
```

### Uso del Menú Interactivo
- **Datos por Defecto (Pauta 9)**: En cualquier solicitud de consola, simplemente presiona **`[ENTER]`** para aceptar el valor predeterminado recomendado.
- **Validación de Entradas (Pauta 7)**: El sistema valida automáticamente rangos numéricos y opciones válidas.

---

## 🕹️ Controles de la Animación en Pygame (Bonus)

Al seleccionar la opción **3** del menú principal:
- **`ESPACIO`**: Pausar / Reanudar la animación en tiempo real.
- **`FLECHA ARRIBA`**: Incrementar la velocidad de simulación (1x $\to$ 2x $\to$ 5x $\to$ 10x $\to$ 20x).
- **`FLECHA ABAJO`**: Disminuir la velocidad de simulación.
- **`TECLA ESC`**: Cerrar la ventana gráfica y retornar al menú principal.

---

## 📄 Archivos de Salida Generados

Tras finalizar cada simulación, se generan automáticamente los siguientes archivos en la carpeta `outputs/`:
- `trace_discreta.txt`: Trazas ordenadas por tiempo simulado de la fábrica de laptops.
- `trace_continua.txt`: Registros de tráfico, temperatura y eficiencia del clúster de servidores.
- `reporte_ia_discreta.txt`: Reporte consolidado con métricas y conclusión automatizada de la IA para el Problema 1.
- `reporte_ia_continua.txt`: Reporte consolidado con métricas y conclusión automatizada de la IA para el Problema 2.
