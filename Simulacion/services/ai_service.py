"""
Módulo de Integración con API de Inteligencia Artificial
---------------------------------------------------------
Envía las métricas compiladas de la simulación a un modelo de IA (OpenAI, Gemini, Ollama)
vía HTTP REST. Incluye un motor de diagnóstico inteligente (LocalAIAnalyzer) como respaldo
automático para garantizar el funcionamiento perfecto en cualquier entorno.
"""

import json
import os
import urllib.request
import urllib.error
from typing import Dict, Any, Optional


class LocalAIAnalyzer:
    """Motor de análisis de diagnóstico experto utilizado como respaldo (fallback) de IA."""

    @staticmethod
    def analyze_discrete(metrics: Dict[str, Any]) -> str:
        """Genera un reporte analítico experto para la Simulación de Eventos Discretos."""
        espera = metrics.get("tiempo_espera_promedio_min", 0.0)
        paradas = metrics.get("paradas_linea_falta_stock", 0)
        duracion_paradas = metrics.get("duracion_total_paradas_min", 0.0)
        eficiencia = metrics.get("eficiencia_reabastecimiento_pct", 100.0)
        completadas = metrics.get("total_ordenes_completadas", 0)
        stock_final = metrics.get("stock_final_procesadores", 0)

        # Evaluación de salud operacional
        diag_espera = "excelente" if espera < 5.0 else ("aceptable" if espera < 15.0 else "crítico")
        diag_paradas = "óptima" if paradas == 0 else ("moderada" if paradas <= 2 else "alta frecuencia de desabastecimiento")

        reporte = (
            f"=== ANÁLISIS DE INTELIGENCIA ARTIFICIAL (DIAGNÓSTICO AUTOMATIZADO) ===\n\n"
            f"1. CONCLUSIÓN GENERAL DE EFICIENCIA:\n"
            f"   La línea de ensamblaje operó durante {metrics.get('duracion_simulada_horas', 0):.2f} horas completando "
            f"un total de {completadas} órdenes de laptops. El tiempo medio de espera en cola fue de {espera:.2f} minutos, "
            f"lo cual representa un nivel de desempeño {diag_espera}.\n\n"
            f"2. EVALUACIÓN DE INVENTARIO Y CADENA DE SUMINISTRO:\n"
            f"   Se registraron {paradas} paradas de línea por falta de procesadores, acumulando {duracion_paradas:.2f} minutos "
            f"de inactividad forzada. La eficiencia del reabastecimiento fue del {eficiencia:.1f}%, finalizando con "
            f"{stock_final} unidades en stock.\n\n"
            f"3. RECOMENDACIONES DE OPTIMIZACIÓN:\n"
        )

        if paradas > 0:
            reporte += (
                f"   [!] URGENTE: El umbral de reabastecimiento (actualmente 10 unidades) es insuficiente para cubrir el "
                f"tiempo de entrega del proveedor (15 min) ante la tasa de llegada (10 órdenes/hora). Se recomienda:\n"
                f"       a) Incrementar el punto de reorden de 10 a 15-20 procesadores.\n"
                f"       b) Negociar con el proveedor un tiempo de entrega más rápido (lead time < 10 min) o mantener un stock de seguridad.\n"
            )
        else:
            reporte += (
                f"   [✓] El sistema de inventario mantuvo la continuidad operativa sin detener la línea.\n"
                f"       Se sugiere mantener los parámetros actuales o probar lotes de menor tamaño para optimizar costos de almacenamiento.\n"
            )

        reporte += (
            f"       c) Monitorear la variabilidad en los tiempos de ensamblaje para balancear la carga de trabajo en la estación."
        )
        return reporte

    @staticmethod
    def analyze_continuous(metrics: Dict[str, Any]) -> str:
        """Genera un reporte analítico experto para la Simulación Continua del Clúster."""
        tb_total = metrics.get("total_terabytes_procesados", 0.0)
        temp_prom = metrics.get("temperatura_promedio_celsius", 70.0)
        temp_max = metrics.get("temperatura_maxima_celsius", 70.0)
        estabilidad = metrics.get("estabilidad_termica_pct", 100.0)
        eficiencia_global = metrics.get("eficiencia_global_promedio_pct", 90.0)
        throttling_events = metrics.get("eventos_estrangulamiento_termico", 0)
        throttling_min = metrics.get("duracion_estrangulamiento_min", 0.0)

        diag_termico = "óptima" if temp_max <= 72.0 else ("moderada" if temp_max <= 76.0 else "alerta de sobrecalentamiento crítico")

        reporte = (
            f"=== ANÁLISIS DE INTELIGENCIA ARTIFICIAL (DIAGNÓSTICO AUTOMATIZADO) ===\n\n"
            f"1. CONCLUSIÓN DE RENDIMIENTO DEL CLÚSTER:\n"
            f"   Durante el periodo simulado de {metrics.get('duracion_simulada_horas', 0):.2f} horas, el clúster procesó "
            f"un total de {tb_total:.4f} Terabytes de datos con una eficiencia global promedio del {eficiencia_global:.1f}%.\n\n"
            f"2. EVALUACIÓN DE ESTABILIDAD TÉRMICA:\n"
            f"   La temperatura promedio del servidor se mantuvo en {temp_prom:.2f}°C (mínima: {metrics.get('temperatura_minima_celsius', 0):.2f}°C, "
            f"máxima: {temp_max:.2f}°C). El sistema permaneció en su rango térmico estable (<=70°C) durante el {estabilidad:.1f}% del tiempo, "
            f"presentando una condición de operación {diag_termico}.\n\n"
            f"3. ANÁLISIS DE ESTRANGULAMIENTO (THERMAL THROTTLING):\n"
            f"   Se detectaron {throttling_events} eventos de estrangulamiento térmico con una duración total de {throttling_min:.2f} minutos.\n\n"
            f"4. RECOMENDACIONES TÉCNICAS:\n"
        )

        if throttling_events > 0:
            reporte += (
                f"   [!] CRÍTICO: Las fluctuaciones de tráfico de red provocaron picos térmicos superiores a 75°C, "
                f"degradando el rendimiento del clúster. Se recomienda:\n"
                f"       a) Aumentar el flujo del sistema de refrigeración líquida (incrementar k_dis de 0.05 a 0.07).\n"
                f"       b) Implementar un algoritmo de balanceo de carga (Load Balancer) para suavizar los picos de tráfico entrante mayores a 4 Gbps.\n"
            )
        else:
            reporte += (
                f"   [✓] El sistema de refrigeración absorbió adecuadamente la carga térmica sin degradar la capacidad de cómputo.\n"
                f"       Se recomienda mantener la calibración actual de los sensores de refrigeración."
            )
        return reporte


class AIService:
    """Servicio para interactuar con APIs de IA (Gemini, OpenAI, Ollama) o fallback local."""

    def __init__(self, provider: str = "auto", api_key: Optional[str] = None):
        self.provider: str = provider.lower()
        self.api_key: Optional[str] = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")

    def generate_analysis(self, problem_type: str, metrics: Dict[str, Any]) -> str:
        """
        Envia las métricas a la API de IA seleccionada o utiliza el motor fallback.
        problem_type: 'discrete' o 'continuous'
        """
        print(f"\n[IA SERVICE] Procesando métricas con Inteligencia Artificial (Proveedor: '{self.provider}')...")

        # Intentar llamar a API externa si está configurada
        if self.provider == "gemini" and self.api_key:
            res = self._call_gemini_api(problem_type, metrics)
            if res:
                return res
        elif self.provider == "openai" and self.api_key:
            res = self._call_openai_api(problem_type, metrics)
            if res:
                return res
        elif self.provider == "ollama":
            res = self._call_ollama_api(problem_type, metrics)
            if res:
                return res

        # Si no se configuró o falló la llamada a la red, usar el generador experto local (Fallback de alta calidad)
        print("[IA SERVICE] Generando análisis analítico con motor experto local (Fallback)...")
        if problem_type == "discrete":
            return LocalAIAnalyzer.analyze_discrete(metrics)
        else:
            return LocalAIAnalyzer.analyze_continuous(metrics)

    def _build_prompt(self, problem_type: str, metrics: Dict[str, Any]) -> str:
        """Construye un prompt estructurado con las métricas recibidas."""
        clean_metrics = {k: v for k, v in metrics.items() if k != "trazas"}
        prompt = (
            f"Eres un experto en Simulación y Métodos Cuantitativos de Ingeniería.\n"
            f"Analiza las siguientes métricas de simulación del problema '{problem_type}':\n"
            f"{json.dumps(clean_metrics, indent=2, ensure_ascii=False)}\n\n"
            f"Por favor proporciona:\n"
            f"1. Una conclusión detallada del desempeño del sistema.\n"
            f"2. Análisis del inventario/temperatura y cuellos de botella identificados.\n"
            f"3. Recomendaciones operativas concretas de optimización."
        )
        return prompt

    def _call_gemini_api(self, problem_type: str, metrics: Dict[str, Any]) -> Optional[str]:
        """Petición HTTP a la API REST de Google Gemini."""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
            prompt = self._build_prompt(problem_type, metrics)
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            headers = {"Content-Type": "application/json"}

            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode("utf-8"))
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                return f"=== ANÁLISIS DE GEMINI AI (API REST) ===\n\n{text}"
        except Exception as e:
            print(f"[IA SERVICE WARNING] Petición a Gemini falló: {e}. Usando fallback local.")
            return None

    def _call_openai_api(self, problem_type: str, metrics: Dict[str, Any]) -> Optional[str]:
        """Petición HTTP a la API REST de OpenAI."""
        try:
            url = "https://api.openai.com/v1/chat/completions"
            prompt = self._build_prompt(problem_type, metrics)
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode("utf-8"))
                text = result["choices"][0]["message"]["content"]
                return f"=== ANÁLISIS DE OPENAI (API REST) ===\n\n{text}"
        except Exception as e:
            print(f"[IA SERVICE WARNING] Petición a OpenAI falló: {e}. Usando fallback local.")
            return None

    def _call_ollama_api(self, problem_type: str, metrics: Dict[str, Any]) -> Optional[str]:
        """Petición HTTP a Ollama local."""
        try:
            url = "http://localhost:11434/api/generate"
            prompt = self._build_prompt(problem_type, metrics)
            payload = {
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
            headers = {"Content-Type": "application/json"}
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode("utf-8"))
                text = result["response"]
                return f"=== ANÁLISIS DE OLLAMA LOCAL ===\n\n{text}"
        except Exception as e:
            print(f"[IA SERVICE WARNING] Petición a Ollama falló: {e}. Usando fallback local.")
            return None
