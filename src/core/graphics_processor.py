import os
import sys
import shutil
from typing import Optional
from mahoyo_tools import cbg
from mahoyo_tools.mzp import MzpImage
from pathlib import Path

class GraphicsProcessor:
    """Clase especializada en el procesamiento, conversión y manejo de recursos gráficos (.cbg, .mzp)."""

    @staticmethod
    def _convertir_archivo_individual(ruta_archivo: str, extension: str, ruta_salida: Optional[str] = None) -> bool:
        """Método interno para convertir un único archivo gráfico (cbg o mzp) a PNG."""
        if not os.path.exists(ruta_archivo):
            print(f"[-] No existe el archivo: {ruta_archivo}")
            return False

        if not ruta_salida:
            base_dir = os.path.dirname(ruta_archivo)
            nombre_base = os.path.splitext(os.path.basename(ruta_archivo))[0]
            ruta_salida = os.path.join(base_dir, f"{nombre_base}.png")

        try:
            os.makedirs(os.path.dirname(os.path.abspath(ruta_salida)), exist_ok=True)
            with open(ruta_archivo, "rb") as f_in:
                if extension == '.cbg':
                    cbg_obj = cbg.CompressedBG(f_in)
                    cbg_obj.img_write(ruta_salida, format="png")
                elif extension == '.mzp':
                    mzp_img = MzpImage(f_in.read())
                    mzp_img.img_write(ruta_salida)
                else:
                    print(f"[-] Extensión no soportada para conversión individual: {extension}")
                    return False
            return True
        except Exception as e:
            print(f"[-] Error al convertir {extension.upper()} a PNG ({ruta_archivo}): {e}")
            return False

    @classmethod
    def procesar_recurso_grafico(
        cls, 
        entrada: str, 
        extension: str,  # '.cbg' o '.mzp'
        carpeta_salida: Optional[str] = None, 
        carpeta_procesados: Optional[str] = None, 
        limite: Optional[int] = None
    ) -> int:
        """
        Método centralizado inteligente: detecta automáticamente si la entrada es un archivo individual 
        o un directorio para procesarlo de forma masiva (con límite y movilización de originales).
        """
        extension = extension.lower()
        if not extension.startswith('.'):
            extension = f".{extension}"

        # CASO A: El usuario pasó la ruta de un archivo específico
        if os.path.isfile(entrada):
            if not entrada.lower().endswith(extension):
                print(f"[-] El archivo especificado no coincide con la extensión esperada ({extension}): {entrada}")
                return 0
            
            # Definir rutas por defecto si el usuario no las especificó
            tipo_nombre = extension.lstrip('.')
            dir_archivo = os.path.dirname(entrada)
            nombre_base = os.path.splitext(os.path.basename(entrada))[0]

            # Si carpeta_salida llegó pero es un directorio (o no se especificó), 
            # construimos la ruta correcta del archivo PNG dentro de esa carpeta.
            if not carpeta_salida:
                carpeta_salida = os.path.join(dir_archivo, f"{tipo_nombre}_png")
            
            # Asegurarnos de que ruta_salida sea el archivo final .png
            if os.path.isdir(carpeta_salida) or not carpeta_salida.lower().endswith('.png'):
                ruta_png_final = os.path.join(carpeta_salida, f"{nombre_base}.png")
            else:
                ruta_png_final = carpeta_salida
                carpeta_salida = os.path.dirname(carpeta_salida)

            if not carpeta_procesados:
                carpeta_procesados = os.path.join(dir_archivo, f"{tipo_nombre}_extracted")

            print(f"[*] Convirtiendo archivo {extension.upper()} individual: {entrada}")
            
            # Llamamos a la conversión pasando la ruta exacta del archivo .png de destino
            exito = cls._convertir_archivo_individual(entrada, extension, ruta_png_final)
            
            if exito:
                print(f"[+] ¡Conversión individual completada con éxito! Guardado en: {ruta_png_final}")
                
                # Mover el archivo original a la carpeta de procesados
                os.makedirs(carpeta_procesados, exist_ok=True)
                try:
                    ruta_destino = os.path.join(carpeta_procesados, os.path.basename(entrada))
                    shutil.move(entrada, ruta_destino)
                    print(f"[+] Archivo original movido a: {carpeta_procesados}")
                except Exception as e:
                    print(f"[-] Advertencia al mover el archivo original: {e}")
                return 1
            return 0

        # CASO B: El usuario pasó una carpeta (Procesamiento por lotes)
        if not os.path.exists(entrada):
            print(f"[-] La ruta de entrada no existe: {entrada}")
            return 0

        if not carpeta_salida:
            carpeta_salida = os.path.join(entrada, f"{extension.lstrip('.')}_png")
        
        if not carpeta_procesados:
            carpeta_procesados = os.path.join(entrada, f"{extension.lstrip('.')}_extracted")

        os.makedirs(carpeta_salida, exist_ok=True)
        os.makedirs(carpeta_procesados, exist_ok=True)

        # Buscar archivos correspondientes en la carpeta
        archivos = sorted([f for f in os.listdir(entrada) if f.lower().endswith(extension)])
        
        total_disponibles = len(archivos)
        if total_disponibles == 0:
            print(f"[*] No se encontraron archivos '{extension}' pendientes en: {entrada}")
            return 0

        # Manejo lógico del límite
        if limite is not None and limite > 0:
            if limite < total_disponibles:
                print(f"[*] Se solicitaron {limite} archivos, pero hay {total_disponibles} disponibles. Procesando lote de {limite}...")
                archivos = archivos[:limite]
            else:
                print(f"[*] El límite ({limite}) excede o iguala los {total_disponibles} archivos disponibles. Procesando todos...")
        else:
            print(f"[*] Procesando los {total_disponibles} archivos disponibles encontrados...")

        exitosos = 0
        lote_a_procesar = len(archivos)

        print(f"[*] Iniciando procesamiento del lote...")
        for i, archivo in enumerate(archivos, 1):
            ruta_archivo = os.path.join(entrada, archivo)
            nombre_png = os.path.splitext(archivo)[0] + ".png"
            ruta_png = os.path.join(carpeta_salida, nombre_png)

            # Barra de progreso visual simple en consola
            porcentaje = (i / lote_a_procesar) * 100
            print(f"\r[{i}/{lote_a_procesar}] ({porcentaje:.1f}%) Procesando: {archivo}", end="", flush=True)
            
            if cls._convertir_archivo_individual(ruta_archivo, extension, ruta_png):
                exitosos += 1
                # Mover el archivo original a la carpeta de procesados
                ruta_destino = os.path.join(carpeta_procesados, archivo)
                try:
                    shutil.move(ruta_archivo, ruta_destino)
                except Exception as e:
                    print(f"\n[-] Advertencia: No se pudo mover el archivo {archivo}: {e}")

        print(f"\n[+] Lote finalizado. {exitosos}/{lote_a_procesar} archivos convertidos y movidos a: {carpeta_procesados}")
        return exitosos
