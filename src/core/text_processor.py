import os
import sys
from io import BytesIO

# Asegurar que mahoyo_tools esté accesible
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAHOYO_TOOLS_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../mahoyo_tools"))
if MAHOYO_TOOLS_DIR not in sys.path:
    sys.path.insert(0, MAHOYO_TOOLS_DIR)

from mahoyo_tools.lenzu import lenzu_decompress
from parsers.MahoyoScriptParserJSON import MahoyoScriptParserJSON

class LenzuDecompressor:

    @staticmethod
    def descompresion_ctd_lenzu(ruta_ctd: str, carpeta_salida_bin: str = "extracted/bin_ctd", parsear_a_json: bool = False, carpeta_salida_json: str = "extracted/json"):
        """
        Toma un archivo .ctd comprimido con LenZu, lo descomprime 
        utilizando lenzu.py y guarda el binario limpio resultante.
        """

        if not os.path.exists(ruta_ctd):
            print(f"[-] No se encontró el archivo CTD: {ruta_ctd}")
            return None

        try:
            with open(ruta_ctd, "rb") as f:
                contenido_bytes = f.read()

            print(f"[*] Procesando CTD: {os.path.basename(ruta_ctd)} ({len(contenido_bytes)} bytes)")
            
            reader = BytesIO(contenido_bytes)
            compressed_size = len(contenido_bytes)

            print("[*] Ejecutando descompresión LenZu...")
            buffer_descomprimido = lenzu_decompress(reader, compressed_size, dest=None)
            
            nombre_base = os.path.splitext(os.path.basename(ruta_ctd))[0]
            ruta_salida_bin = os.path.join(carpeta_salida_bin, f"{nombre_base}_descomprimido.bin")
            
            os.makedirs(os.path.dirname(os.path.abspath(ruta_salida_bin)), exist_ok=True)
            with open(ruta_salida_bin, "wb") as f_out:
                f_out.write(buffer_descomprimido.getvalue())

            print(f"[+] ¡Descompresión exitosa! Binario guardado en: {ruta_salida_bin}")

            # Si se solicita explícitamente, encadenamos el parseo a JSON automáticamente
            if parsear_a_json:
                print("[*] Opción de parseo automático activada...")
                os.makedirs(carpeta_salida_json, exist_ok=True)
                ruta_salida_json = os.path.join(carpeta_salida_json, f"{nombre_base}.json")
                
                # Instanciamos la clase pasando la ruta del binario recién generado
                parser = MahoyoScriptParserJSON(ruta_salida_bin)
                parser.extraer_textos_filtrados(ruta_salida_json)

            return ruta_salida_bin

        except Exception as e:
            print(f"[-] Error al descomprimir el archivo CTD: {e}")
            return None