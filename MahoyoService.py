import os
import sys
import re
import inspect
from io import BytesIO
from typing import List, Any, Optional, Dict, Optional, Union

# Configurar path a /tools/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.join(BASE_DIR, "mahoyo_tools")
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

from mahoyo_tools import hfa, cbg

class MahoyoHelper:

    """Capa de servicio que centraliza la interacción con mahoyo_tools."""

    # -------------------------------------------------------------------------
    # MÓDULO DE DIAGNÓSTICO E INSPECCIÓN DE CLASES Y OBJETOS
    # -------------------------------------------------------------------------
    @classmethod
    def diagnosticar(cls, obj: Any, titulo: str = "INSPECCIÓN DE COMPONENTE") -> Dict[str, Any]:
        """
        Realiza un análisis exhaustivo de atributos, métodos, firmas de funciones
        e información implícita de cualquier objeto o clase.
        """
        print(f"\n==================================================")
        print(f" {titulo.upper()}")
        print(f"==================================================")
        
        tipo_objeto = type(obj)
        nombre_clase = tipo_objeto.__name__
        modulo = tipo_objeto.__module__
        print(f"[*] Clase: {nombre_clase} (Módulo: '{modulo}')")
        print(f"[*] Tipo: {tipo_objeto}")

        # 1. Separar atributos públicos entre callables (métodos) y propiedades
        atributos_todos = [a for a in dir(obj) if not a.startswith('__')]
        propiedades = []
        metodos = {}

        for attr in atributos_todos:
            try:
                valor = getattr(obj, attr)
                if callable(valor):
                    try:
                        sig = inspect.signature(valor)
                        metodos[attr] = str(sig)
                    except (ValueError, TypeError):
                        metodos[attr] = "(...)"
                else:
                    propiedades.append((attr, type(valor).__name__, valor))
            except Exception as e:
                propiedades.append((attr, "ERROR", f"No accesible ({e})"))

        # 2. Imprimir Métodos con sus Firmas Reales
        print(f"\n--- MÉTODOS Y FUNCIONES ({len(metodos)}) ---")
        if metodos:
            for nombre_m, firma in sorted(metodos.items()):
                print(f"  • {nombre_m}{firma}")
        else:
            print("  (No se encontraron métodos públicos)")

        # 3. Imprimir Propiedades y Estado Actual
        print(f"\n--- PROPIEDADES Y VALORES ({len(propiedades)}) ---")
        if propiedades:
            for nombre_p, tipo_p, val_p in sorted(propiedades, key=lambda x: x[0]):
                # Truncar representaciones de texto muy largas
                repr_val = str(val_p)
                if len(repr_val) > 70:
                    repr_val = repr_val[:67] + "..."
                print(f"  • {nombre_p} ({tipo_p}): {repr_val}")
        else:
            print("  (No se encontraron propiedades públicas)")

        print("==================================================\n")

        return {
            "clase": nombre_clase,
            "metodos": metodos,
            "propiedades": [p[0] for p in propiedades]
        }

    @classmethod
    def inspeccionar_stream_o_bytes(cls, data_or_stream: Union[bytes, BytesIO], max_bytes: int = 32) -> bytes:
        """
        Analiza cabeceras (magic bytes) sin alterar la posición original del puntero de lectura.
        """
        if isinstance(data_or_stream, BytesIO):
            pos_original = data_or_stream.tell()
            data_or_stream.seek(0)
            header = data_or_stream.read(max_bytes)
            data_or_stream.seek(pos_original)  # Restaurar puntero
        else:
            header = bytes(data_or_stream[:max_bytes])

        print(f"--- ANÁLISIS DE CABECERA (MAGIC BYTES) ---")
        print(f"[*] Tamaño de muestra: {len(header)} bytes")
        print(f"[*] Hexadecimal: {header.hex(' ')}")
        print(f"[*] Representación ASCII: {header}")
        print("------------------------------------------\n")
        return header
