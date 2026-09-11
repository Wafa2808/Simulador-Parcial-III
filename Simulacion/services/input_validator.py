"""
Módulo de Validación de Entradas de Usuario
-------------------------------------------
Proporciona métodos auxiliares con validación estricta para solicitudes por consola,
garantizando el cumplimiento de la pauta 7 (validaciones) y pauta 9 (datos por defecto).
"""

from typing import Union


class InputValidator:
    """Clase estática para validar y solicitar datos por consola."""

    @staticmethod
    def get_float(prompt: str, default: float, min_val: float = 0.1, max_val: float = 1000.0) -> float:
        """
        Solicita un número flotante al usuario.
        Si presiona Enter sin escribir nada, retorna el valor por defecto.
        Valida que esté dentro del rango especificado [min_val, max_val].
        """
        while True:
            try:
                user_input = input(f"{prompt} [Por defecto: {default}]: ").strip()
                if not user_input:
                    print(f"-> Usando valor por defecto: {default}")
                    return default

                val = float(user_input)
                if val < min_val or val > max_val:
                    print(f"[ERROR DE VALIDACIÓN] El valor debe estar entre {min_val} y {max_val}. Intente nuevamente.")
                    continue
                return val
            except ValueError:
                print("[ERROR DE VALIDACIÓN] Entrada inválida. Debe ingresar un número válido (ej. 8 o 12.5).")

    @staticmethod
    def get_int(prompt: str, default: int, min_val: int = 1, max_val: int = 100) -> int:
        """
        Solicita un entero al usuario con soporte para valor por defecto y validación de rango.
        """
        while True:
            try:
                user_input = input(f"{prompt} [Por defecto: {default}]: ").strip()
                if not user_input:
                    print(f"-> Usando valor por defecto: {default}")
                    return default

                val = int(user_input)
                if val < min_val or val > max_val:
                    print(f"[ERROR DE VALIDACIÓN] El número debe estar entre {min_val} y {max_val}. Intente nuevamente.")
                    continue
                return val
            except ValueError:
                print("[ERROR DE VALIDACIÓN] Entrada inválida. Debe ingresar un número entero válido.")

    @staticmethod
    def get_option(prompt: str, valid_options: list, default: str = None) -> str:
        """
        Solicita la selección de una opción dentro de una lista permitida.
        """
        while True:
            default_str = f" [Por defecto: {default}]" if default else ""
            user_input = input(f"{prompt}{default_str}: ").strip()
            
            if not user_input and default is not None:
                print(f"-> Seleccionada opción por defecto: {default}")
                return default

            if user_input in valid_options:
                return user_input

            print(f"[ERROR DE VALIDACIÓN] Opción inválida '{user_input}'. Opciones válidas: {', '.join(valid_options)}")
