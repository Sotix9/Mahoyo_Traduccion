import json
import re
import os

class MahoyoScriptParserJSON:

    def __init__(self, ruta_binario: str):
        self.ruta_binario = ruta_binario

    def extraer_textos_filtrados(self, ruta_salida_json: str):
        if not os.path.exists(self.ruta_binario):
            raise FileNotFoundError(f"No se encuentra el archivo en: {self.ruta_binario}")

        with open(self.ruta_binario, "rb") as f:
            contenido = f.read()

        # Expresión regular para capturar cadenas de texto legítimas en UTF-8
        # Buscamos secuencias que tengan al menos una longitud prudente y caracteres imprimibles estándar
        patron = re.compile(b'[\x20-\x7E\xC2-\xF4][\x20-\x7E\xC2-\xF4\x80-\xBF]{3,}')
        coincidencias = patron.findall(contenido)

        textos_extraidos = []
        contador = 1
        vistos = set() # Para evitar duplicados si los hubiera

        for raw_str in coincidencias:
            try:
                texto = raw_str.decode('utf-8', errors='ignore').strip()
                
                # Criterios estrictos de filtrado para desechar bytecode y comandos internos
                es_basura_o_comando = (
                    len(texto) < 4 or
                    texto in vistos or
                    texto.startswith("LenZu") or
                    texto.startswith("mrgd") or
                    any(cmd in texto for cmd in ["_ZM", "_ZY", "_SCH", "_JUMP", "_WKST", "script_text"]) or
                    not any(c.isalpha() for c in texto) # Debe contener al menos una letra real
                )

                if not es_basura_o_comando:
                    vistos.add(texto)
                    textos_extraidos.append({
                        "id": contador,
                        "original": texto,
                        "traduccion": ""
                    })
                    contador += 1

            except Exception:
                continue

        with open(ruta_salida_json, "w", encoding="utf-8") as f_json:
            json.dump(textos_extraidos, f_json, ensure_ascii=False, indent=4)
            
        print(f"¡Parseo refinado completado! Se obtuvieron {len(textos_extraidos)} líneas limpias listas para traducción.")