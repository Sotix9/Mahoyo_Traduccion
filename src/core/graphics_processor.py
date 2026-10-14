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
    def convertir_cbg_a_png(ruta_cbg: str, ruta_png: Optional[str] = None) -> bool:
        """Convierte una imagen .cbg individual a formato PNG estándar."""
        if not os.path.exists(ruta_cbg):
            print(f"[-] No existe el archivo CBG: {ruta_cbg}")
            return False

        if not ruta_png:
            base_dir = os.path.dirname(ruta_cbg)
            nombre_base = os.path.splitext(os.path.basename(ruta_cbg))[0]
            ruta_png = os.path.join(base_dir, f"{nombre_base}.png")

        try:
            os.makedirs(os.path.dirname(os.path.abspath(ruta_png)), exist_ok=True)
            with open(ruta_cbg, "rb") as f_in:
                cbg_obj = cbg.CompressedBG(f_in)
                cbg_obj.img_write(ruta_png, format="png")
            return True
        except Exception as e:
            print(f"[-] Error al convertir CBG a PNG ({ruta_cbg}): {e}")
            return False

    @classmethod
    def convertir_directorio_cbg_con_limite(
        cls, 
        carpeta_entrada: str, 
        carpeta_salida: Optional[str] = None, 
        carpeta_procesados: Optional[str] = None, 
        limite: Optional[int] = None
        ) -> int:
        """
        Escanea una carpeta en busca de archivos .cbg, procesa hasta alcanzar un límite opcional,
        convierte a .png y mueve los archivos procesados a una carpeta de destino para descartarlos
        en futuras extracciones. Maneja automáticamente si el límite supera el stock disponible.
        """
        if not carpeta_salida:
            carpeta_salida = os.path.join(carpeta_entrada, "cbg_png")
        
        if not carpeta_procesados:
            carpeta_procesados = os.path.join(carpeta_entrada, "cbg_extracted")

        if not os.path.exists(carpeta_entrada):
            print(f"[-] La carpeta de entrada no existe: {carpeta_entrada}")
            return 0

        os.makedirs(carpeta_salida, exist_ok=True)
        os.makedirs(carpeta_procesados, exist_ok=True)

        # Buscar archivos .cbg disponibles de forma ordenada
        archivos_cbg = sorted([f for f in os.listdir(carpeta_entrada) if f.lower().endswith('.cbg')])
        
        total_disponibles = len(archivos_cbg)
        if total_disponibles == 0:
            print(f"[*] No se encontraron archivos .cbg pendientes en: {carpeta_entrada}")
            return 0

        # Manejo lógico del límite solicitado frente al stock real
        if limite is not None and limite > 0:
            if limite < total_disponibles:
                print(f"[*] Se solicitaron {limite} archivos, pero hay {total_disponibles} disponibles. Procesando lote de {limite}...")
                archivos_cbg = archivos_cbg[:limite]
            else:
                print(f"[*] El límite solicitado ({limite}) excede o iguala los {total_disponibles} archivos disponibles. Procesando todos...")
        else:
            print(f"[*] Procesando los {total_disponibles} archivos disponibles encontrados...")

        exitosos = 0
        lote_a_procesar = len(archivos_cbg)

        print(f"[*] Iniciando procesamiento del lote...")
        for i, archivo in enumerate(archivos_cbg, 1):
            ruta_cbg = os.path.join(carpeta_entrada, archivo)
            nombre_png = os.path.splitext(archivo)[0] + ".png"
            ruta_png = os.path.join(carpeta_salida, nombre_png)

            # Barra de progreso visual simple en consola
            porcentaje = (i / lote_a_procesar) * 100
            print(f"\r[{i}/{lote_a_procesar}] ({porcentaje:.1f}%) Procesando: {archivo}", end="", flush=True)
            
            # Convertir imagen CBG a PNG utilizando tu método estático existente
            if cls.convertir_cbg_a_png(ruta_cbg, ruta_png):
                exitosos += 1
                # Mover el archivo original a la carpeta de procesados/descartados
                ruta_destino = os.path.join(carpeta_procesados, archivo)
                try:
                    shutil.move(ruta_cbg, ruta_destino)
                except Exception as e:
                    print(f"[-] Advertencia: No se pudo mover el archivo {archivo} a {carpeta_procesados}: {e}")

        print(f"[+] Lote finalizado. {exitosos}/{lote_a_procesar} archivos CBG convertidos y movidos a: {carpeta_procesados}")
        return exitosos

    @staticmethod
    def convertir_mzp_a_png(ruta_mzp: str, ruta_png: Optional[str] = None) -> bool:
        """Convierte un archivo de imagen comprimida .mzp a formato PNG estándar."""
        if not os.path.exists(ruta_mzp):
            print(f"[-] No existe el archivo MZP: {ruta_mzp}")
            return False

        if not ruta_png:
            base_dir = os.path.dirname(ruta_mzp)
            nombre_base = os.path.splitext(os.path.basename(ruta_mzp))[0]
            ruta_png = os.path.join(base_dir, f"{nombre_base}.png")

        try:
            os.makedirs(os.path.dirname(os.path.abspath(ruta_png)), exist_ok=True)
            with open(ruta_mzp, "rb") as f_in:
                mzp_img = MzpImage(f_in.read())
                mzp_img.img_write(ruta_png)
            return True
        except Exception as e:
            print(f"[-] Error al convertir MZP a PNG ({ruta_mzp}): {e}")
            return False


    @classmethod
    def convertir_directorio_mzp_con_limite(
        cls, 
        carpeta_entrada: str, 
        carpeta_salida: Optional[str] = None, 
        carpeta_procesados: Optional[str] = None, 
        limite: Optional[int] = None
    ) -> int:
        """
        Escanea una carpeta en busca de archivos .mzp, procesa hasta alcanzar un límite opcional,
        convierte a .png y mueve los archivos procesados a una carpeta de destino para descartarlos
        en futuras extracciones. Maneja automáticamente si el límite supera el stock disponible.
        """
        if not carpeta_salida:
            carpeta_salida = os.path.join(carpeta_entrada, "mzp_png")
        
        if not carpeta_procesados:
            carpeta_procesados = os.path.join(carpeta_entrada, "mzp_extracted")

        if not os.path.exists(carpeta_entrada):
            print(f"[-] La carpeta de entrada no existe: {carpeta_entrada}")
            return 0

        os.makedirs(carpeta_salida, exist_ok=True)
        os.makedirs(carpeta_procesados, exist_ok=True)

        # Buscar archivos .mzp disponibles
        archivos_mzp = sorted([f for f in os.listdir(carpeta_entrada) if f.lower().endswith('.mzp')])
        
        total_disponibles = len(archivos_mzp)
        if total_disponibles == 0:
            print(f"[*] No se encontraron archivos .mzp pendientes en: {carpeta_entrada}")
            return 0

        # Manejo lógico del límite solicitado frente al stock real
        if limite is not None and limite > 0:
            if limite < total_disponibles:
                print(f"[*] Archivos solicitados: {limite} | Disponibles: {total_disponibles}. Procesando lote de {limite}...")
                archivos_mzp = archivos_mzp[:limite]
            else:
                print(f"[*] Archivos solicitados: {limite} | Disponibles: {total_disponibles}. Procesando restantes/todos...")
        else:
            print(f"[*] Procesando los {total_disponibles} archivos disponibles encontrados...")

        exitosos = 0
        lote_a_procesar = len(archivos_mzp)

        print(f"[*] Iniciando procesamiento del lote...")
        for i, archivo in enumerate(archivos_mzp, 1):
            ruta_mzp = os.path.join(carpeta_entrada, archivo)
            nombre_png = os.path.splitext(archivo)[0] + ".png"
            ruta_png = os.path.join(carpeta_salida, nombre_png)
        
            # Barra de progreso visual simple en consola
            porcentaje = (i / lote_a_procesar) * 100
            print(f"\r[{i}/{lote_a_procesar}] ({porcentaje:.1f}%) Procesando: {archivo}", end="", flush=True)
            
            # Convertir imagen
            if cls.convertir_mzp_a_png(ruta_mzp, ruta_png):
                exitosos += 1
                # Mover el archivo original a la carpeta de procesados/descartados
                ruta_destino = os.path.join(carpeta_procesados, archivo)
                try:
                    shutil.move(ruta_mzp, ruta_destino)
                except Exception as e:
                    print(f"[-] Advertencia: No se pudo mover el archivo {archivo} a {carpeta_procesados}: {e}")

        print(f"[+] Lote finalizado. {exitosos}/{lote_a_procesar} archivos convertidos y movidos a: {carpeta_procesados}")
        return exitosos
