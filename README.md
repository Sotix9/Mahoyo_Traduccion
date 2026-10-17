# Proyecto de Traducción: Witch on the Holy Night (Mahoyo)

Herramientas de automatización y procesamiento en Python para la extracción, gestión, descompresión y análisis de recursos (scripts, contenedores y gráficos) de la novela visual *Witch on the Holy Night* (Mahoutsukai no Yoru).

## 📂 Estructura Modular del Proyecto

El proyecto está organizado bajo una arquitectura modular estricta para separar las responsabilidades de la interfaz de usuario, los parsers de formato y los motores de procesamiento central:

```text
01_proyecto_traduccion/
│
├── cli.py                         # Punto de entrada principal por consola (CLI)
├── mahoyo_tools/                  # Módulo base integrado para lenzu y contenedores HFA
├── parsers/                       # Parsers de scripts y extracción de texto
│   └── MahoyoScriptParserJSON.py
├── WHN_Copy/                      # Copia local / datos de juego de trabajo
│
├── src/                           # Lógica interna y núcleos de procesamiento
│   ├── core/
│   │   ├── graphics_processor.py  # Conversión gráfica (MZP, MZX0, CBG, tiles)
│   │   ├── hfa_reader.py          # Gestión, extracción y diagnóstico de archivos HFA
│   │   └── text_processor.py      # Orquestador de descompresión LenZu y parseo
│   │
│   └── legacy/                    # Scripts históricos, pruebas y laboratorios de prueba
│       └── scripts_tests/         (no incluido)
```

---

## Requisitos y Dependencias

### 1. Dependencias de Python
Instala las librerías necesarias con el siguiente comando:
```bash
pip install numpy Pillow cffi imagequant
```

### 2. Repositorios y Herramientas Integradas
* **mahoyo_tools:** Módulo de Python base con scripts dedicados de descompresión (`hfa.py, lenzu.py, mzp.py, cbg.py`) para archivos `.hfa`, `.cbg`, `.mzp` y `.ctd`.
  * [mahoyo_tools en GitHub](https://github.com/loicfrance/mahoyo_tools.git)
---

## Línea de Comandos (CLI)

La interfaz central se gestiona a través de `cli.py`. Para ver las opciones globales y detalles de sintaxis:
```bash
python cli.py --help
python cli.py <comando> --help
```

### 1. Comando: list
Genera una lista/reporte de todo el contenido de un `.hfa`, indicando cantidad total de archivos y resumen por extensión, guardándolo por defecto en `reports/reporte_hfa.txt`:
```bash
python cli.py list -i ruta/al/archivo.hfa
```

### 2. Comando: extract
Extrae el contenido de un `.hfa` tanto total o de forma selectiva indicando la extensión deseada, guardándolos por defecto en `extracted/(extension-archivo)/`:
```bash
python cli.py extract -i ruta/al/archivo.hfa
```

### 3. Comando: allcbg2png
Convierte todos o una cantidad especificada de archivos `.cbg`, guardándolos por defecto en `extracted/cbg/cbg_png/`.
Los archivos procesados se moverán por defecto a `extracted/cbg/extracted_cbg/`, para que en la próxima extracción no se vuelvan a tomar en cuenta.
```bash
python cli.py allcbg2png -i [ruta/carpeta/cbg | ruta/al/archivo.cbg] -lim cantidad-a-procesar
```

### 4. Comando: allmzp2png
Convierte todos o una cantidad especificada de archivos `.mzp`, guardándolos por defecto en `extracted/mzp/mzp_png/`.
Los archivos procesados se moverán por defecto a `extracted/mzp/extracted_mzp/`, para que en la próxima extracción no se vuelvan a tomar en cuenta.
```bash
python cli.py allmzp2png -i [ruta/carpeta/mzp | ruta/al/archivo.mzp] -lim cantidad-a-procesar
```

### 5. Comando: lenzu
Descomprime o comprime un archivo `.ctd` mediante `lenzu` con las banderas: `-decompress` o `-compress`, generando el binario limpio en `extracted/bin_ctd/`
Si añades la bandera `-json`, se procesará el binario de forma encadenada usando `MahoyoScriptParserJSON`, generando un archivo estructurado listo para traducción en `extracted/json/`. Esta opción solo funciona al descomprimir el archivo:
```bash
python cli.py lenzu [-decompress | -compress] -i ruta/al/archivo.ctd -json
```


### 6. Comando: jsonparse
Convierte un archivo `.bin` extraído de un `.ctd` a JSON, guardándolo por defecto en `extracted/json/`. Desobliga la utilización de la bandera `-json` del comando `lenzu`:
```bash
python cli.py jsonparse -i ruta/al/archivo.bin
```

### 7. Comando: inject
Reinyección del archivo `.bin` o `.ctd` modificado y comprimido dentro del archivo `.hfa` de origen:
```bash
python cli.py inject -hfa ruta/al/archivo.hfa -t nombre-archivo-a-modificar -f ruta/al/archivo_modificado[.bin | .ctd]
```


---

## Módulos Principales

* **`text_processor.py`:** Encapsula la descompresión con `lenzu_decompress` y coordina el flujo de extracción hacia la capa de parsing.
* **`MahoyoScriptParserJSON.py`:** Aplica filtros estrictos por expresiones regulares para desechar bytecode, comandos del motor y cadenas basura, generando una estructura JSON limpia con `id`, `original` y `traduccion`.
* **`hfa_reader.py`:** Maneja la lectura de archivos `.hfa`, generación de reportes por extensión, extracción organizada e inspección profunda de objetos y cabeceras binarias.
* **`graphics_processor.py`:** Gestor de procesamiento técnico de texturas e imágenes.
