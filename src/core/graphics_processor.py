import os
from typing import Optional
from mahoyo_tools import cbg

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
    def convertir_directorio_cbg(cls, carpeta_entrada: str, carpeta_salida: Optional[str] = None) -> int:
        """
        Escanea una carpeta en busca de archivos .cbg y los convierte todos a .png en un solo intento.
        """
        if not carpeta_salida:
            carpeta_salida = os.path.join(carpeta_entrada, "extracted_png")

        if not os.path.exists(carpeta_entrada):
            print(f"[-] La carpeta de entrada no existe: {carpeta_entrada}")
            return 0

        os.makedirs(carpeta_salida, exist_ok=True)
        archivos_cbg = [f for f in os.listdir(carpeta_entrada) if f.lower().endswith('.cbg')]
        
        if not archivos_cbg:
            print(f"[*] No se encontraron archivos .cbg en: {carpeta_entrada}")
            return 0

        print(f"[*] Se encontraron {len(archivos_cbg)} archivos .cbg. Iniciando conversión masiva...")
        exitosos = 0

        for archivo in archivos_cbg:
            ruta_cbg = os.path.join(carpeta_entrada, archivo)
            nombre_png = os.path.splitext(archivo)[0] + ".png"
            ruta_png = os.path.join(carpeta_salida, nombre_png)

            if cls.convertir_cbg_a_png(ruta_cbg, ruta_png):
                exitosos += 1

        print(f"[+] Conversión masiva finalizada. {exitosos}/{len(archivos_cbg)} imágenes convertidas en: {carpeta_salida}")
        return exitosos
