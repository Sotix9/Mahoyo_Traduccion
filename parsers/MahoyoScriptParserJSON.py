import json
import re
import os

class MahoyoScriptParserJSON:
    """Parser estructurado para extraer, desglosar y empaquetar textos de scripts de Mahoyo (.bin / .ctd)."""

    def __init__(self, ruta_binario: str):
        self.ruta_binario = ruta_binario

    def extraer_textos_filtrados(self, ruta_salida_json: str | None = None) -> str:
        """
        Extrae los textos del archivo binario y los exporta a un JSON estructurado.
        
        :param ruta_salida_json: Ruta opcional de destino para el archivo JSON.
                                 Si es None, se genera automáticamente en 'extracted/json/'.
        :return: La ruta final donde se guardó el archivo JSON.
        """
        if not os.path.exists(self.ruta_binario):
            raise FileNotFoundError(f"No se encuentra el archivo en: {self.ruta_binario}")

        # Definir ruta de salida por defecto si no se proporciona
        if ruta_salida_json is None:
            nombre_base = os.path.splitext(os.path.basename(self.ruta_binario))[0]
            # Limpiar sufijos repetitivos si el binario ya traía '_descomprimido'
            nombre_base = nombre_base.replace("_descomprimido", "")
            ruta_salida_json = os.path.join("extracted", "json", f"{nombre_base}.json")

        with open(self.ruta_binario, "rb") as f:
            contenido = f.read()

        textos_extraidos = []
        contador = 1
        vistos = set()

        # Expresión regular para capturar bloques de texto válidos
        patron_texto = re.compile(b'[\x20-\x7E\xC2-\xF4][\x20-\x7E\xC2-\xF4\x80-\xBF\x0A\x0D]{2,}')
        coincidencias = patron_texto.findall(contenido)

        for raw_bytes in coincidencias:
            try:
                # Limpiar bytes nulos pero preservar saltos de línea internos
                raw_bytes_limpios = raw_bytes.replace(b'\x00', b'').strip()
                if len(raw_bytes_limpios) < 3:
                    continue

                texto_bloque = raw_bytes_limpios.decode('utf-8', errors='ignore')

                # Dividir el bloque grande usando los saltos de línea para aislar frases
                lineas_individuales = re.split(r'[\r\n]+', texto_bloque)

                for linea in lineas_individuales:
                    linea_limpia = linea.strip()

                    es_valida = (
                        len(linea_limpia) >= 2 and
                        linea_limpia not in vistos and
                        any(c.isalpha() for c in linea_limpia) and  
                        not linea_limpia.startswith(('LenZu', 'mrgd', '_', 'script_')) 
                    )

                    if es_valida:
                        vistos.add(linea_limpia)
                        textos_extraidos.append({
                            "id": contador,
                            "original": linea_limpia,
                            "traduccion": ""
                        })
                        contador += 1

            except Exception:
                continue

        # Guardar la estructura JSON limpia
        os.makedirs(os.path.dirname(os.path.abspath(ruta_salida_json)), exist_ok=True)
        with open(ruta_salida_json, "w", encoding="utf-8") as f_json:
            json.dump(textos_extraidos, f_json, ensure_ascii=False, indent=4, separators=(',', ': '))
            
        print(f"[+] Parseo completado. Se obtuvieron {len(textos_extraidos)} líneas. JSON guardado en: {ruta_salida_json}")
        return ruta_salida_json
