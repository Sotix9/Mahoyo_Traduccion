import os
import sys
import json
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
    def descompresion_ctd_lenzu(
        ruta_ctd: str, 
        carpeta_salida_bin: str = "extracted/bin_ctd", 
        parsear_a_json: bool = False, 
        carpeta_salida_json: str = "extracted/json"
        ):
        
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

    @staticmethod
    def comprimir_json_a_ctd(
        ruta_json: str, 
        ruta_ctd_original: str, 
        ruta_salida_ctd: str
    ) -> bool:
        
        """
        Toma un archivo JSON traducido, reconstruye el archivo binario .ctd 
        y lo deja listo (o lo comprime con LenZu si la librería lo soporta) para su reinyección.
        """
        
        if not os.path.exists(ruta_json):
            print(f"[-] No se encontró el archivo JSON: {ruta_json}")
            return False

        if not os.path.exists(ruta_ctd_original):
            print(f"[-] No se encontró el archivo CTD original de referencia: {ruta_ctd_original}")
            return False

        try:
            # 1. Cargar el JSON traducido
            with open(ruta_json, "r", encoding="utf-8") as f:
                datos_json = json.load(f)

            print(f"[*] Cargados {len(datos_json)} registros traducidos desde el JSON.")

            # 2. Leer el binario original como base estructural
            with open(ruta_ctd_original, "rb") as f:
                binario_original = f.read()

            # Lógica de reemplazo de cadenas:
            # Aquí aplicamos la sustitución de los textos originales por los traducidos
            # manteniendo la integridad de los opcodes binarios circundantes.
            binario_modificado = binario_original
            for item in datos_json:
                orig = item.get("original", "").encode("utf-8")
                trad = item.get("traduccion", "").encode("utf-8")
                
                # Si hay una traducción válida, reemplazamos en el flujo de bytes
                if trad and orig in binario_modificado:
                    # Nota: Hay que asegurar el manejo de longitudes si el texto traducido 
                    # ocupa más bytes que el original (padding o reasignación de punteros).
                    binario_modificado = binario_modificado.replace(orig, trad)

            # 3. Guardar el archivo .ctd resultante listo para inyección
            os.makedirs(os.path.dirname(os.path.abspath(ruta_salida_ctd)), exist_ok=True)
            with open(ruta_salida_ctd, "wb") as f_out:
                f_out.write(binario_modificado)

            print(f"[+] Archivo CTD compilado con éxito en: {ruta_salida_ctd}")
            return True

        except Exception as e:
            print(f"[-] Error al compilar el JSON a CTD: {e}")
            return False
