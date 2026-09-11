"""
Módulo de Registro de Trazas y Generación de Archivos de Salida
---------------------------------------------------------------
Se encarga de formatear las métricas por consola y guardar las trazas
y reportes generados por la IA en archivos de texto dentro de la carpeta outputs/.
"""

import os
from typing import Dict, Any, List


class LoggerService:
    """Servicio POO para el manejo de archivos de trazas y reportes de simulación."""

    @staticmethod
    def display_metrics_summary(title: str, metrics: Dict[str, Any]):
        """Muestra un resumen formateado de las métricas en consola."""
        print("\n" + "=" * 70)
        print(f"  {title.upper()}")
        print("=" * 70)
        for key, value in metrics.items():
            if key == "trazas":
                continue
            formatted_key = key.replace("_", " ").title()
            print(f"  • {formatted_key:<45}: {value}")
        print("=" * 70 + "\n")

    @staticmethod
    def save_traces(filepath: str, traces: List[str]):
        """Guarda la lista de trazas de ejecución en un archivo de texto."""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"=== ARCHIVO DE TRAZAS DE SIMULACIÓN ===\n")
                f.write(f"Total de registros: {len(traces)}\n\n")
                for trace in traces:
                    f.write(trace + "\n")
            print(f"[EXITO] Archivo de trazas guardado exitosamente en: {filepath}")
        except Exception as e:
            print(f"[ERROR] No se pudo guardar el archivo de trazas '{filepath}': {e}")

    @staticmethod
    def save_ai_report(filepath: str, problem_title: str, metrics: Dict[str, Any], ai_analysis: str):
        """Guarda el reporte consolidado con las métricas y la conclusión de la IA en un archivo de texto."""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("========================================================================\n")
                f.write(f"  REPORTE OFICIAL DE SIMULACIÓN E INTELIGENCIA ARTIFICIAL\n")
                f.write(f"  Problema: {problem_title}\n")
                f.write("========================================================================\n\n")

                f.write("--- 1. MÉTRICAS CLAVE RECOPILADAS ---\n")
                for key, value in metrics.items():
                    if key == "trazas":
                        continue
                    formatted_key = key.replace("_", " ").title()
                    f.write(f"  • {formatted_key:<45}: {value}\n")
                
                f.write("\n--- 2. CONCLUSIÓN Y RECOMENDACIÓN AUTOMATIZADA (IA) ---\n\n")
                f.write(ai_analysis.strip() + "\n\n")
                f.write("========================================================================\n")

            print(f"[EXITO] Reporte de IA guardado exitosamente en: {filepath}")
        except Exception as e:
            print(f"[ERROR] No se pudo guardar el reporte de IA '{filepath}': {e}")
