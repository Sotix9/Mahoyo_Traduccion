# Proyecto de Traducción: Witch on the Holy Night (Mahoyo)

Herramientas de automatización y procesamiento en Python para la extracción, gestión, descompresión y análisis de recursos (scripts, contenedores y gráficos) de la novela visual *Witch on the Holy Night* (Mahoutsukai no Yoru).

## 📂 Estructura Modular del Proyecto

El proyecto está organizado bajo una arquitectura modular estricta para separar las responsabilidades de la interfaz de usuario, los parsers de formato y los motores de procesamiento central:

```text
01_proyecto_traduccion/
│
├── cli.py                  # Punto de entrada principal por consola (CLI)
├── mahoyo_tools/           # Módulo base integrado para lenzu y contenedores HFA
├── parsers/                # Parsers de scripts y extracción de texto
│   └── MahoyoScriptParserJSON.py
├── WHN_Copy/               # Copia local / datos de juego de trabajo
│
├── src/                    # Lógica interna y núcleos de procesamiento
│   ├── core/
│   │   ├── graphics_processor.py  # Conversión gráfica (MZP, MZX0, CBG, tiles)
│   │   ├── hfa_reader.py          # Gestión, extracción y diagnóstico de archivos HFA
│   │   └── text_processor.py      # Orquestador de descompresión LenZu y parseo
│   │
│   └── legacy/             # Scripts históricos, pruebas y laboratorios de prueba
│       └── scripts_tests/
```

---

## Requisitos y Dependencias

### 1. Dependencias de Python
Instala las librerías necesarias con el siguiente comando:
```bash
pip install numpy Pillow cffi imagequant
```

### 2. Repositorios y Herramientas Integradas
* **mahoyo_tools:** Módulo de Python base para la interacción con descompresión LenZu y contenedores HFA.
  * [mahoyo_tools en GitHub](https://github.com/loicfrance/mahoyo_tools.git)
---

## Uso de la Línea de Comandos (CLI)

La interfaz central se gestiona a través de `cli.py`. Para ver las opciones globales:
```bash
python cli.py --help
python cli.py <comando> --help
```

### 1. Generar reportes de archivos (`.hfa`)
Genera una lista de todo el contenido de un `.hfa`, indicando cantidad total de archivos y resumen por extensión, guardándolo por defecto en `reports/reporte_hfa.txt/`:
```bash
python cli.py list -input ruta/al/archivo.hfa
```

### 2. Extraer archivo (`.hfa`)
Extrae el contenido de un `.hfa` tanto total o de forma selectiva indicando la extensión deseada, guardándolos por defecto en `extracted/(extension-archivo)/`:
```bash
python cli.py extract -input ruta/al/archivo.hfa
```

### 3. Conversión `.cbg` a `.png`
Convierte un único archivo `.cbg`, guardándolo por defecto en `extracted/png/`:
```bash
python cli.py cbg2png -input ruta/al/archivo.cbg
```

### 4. Conversión total `.cbg` a `.png`
Convierte todos los archivos `.cbg`, guardándolos por defecto en `extracted/png/`:
```bash
python cli.py allcbg2png -input ruta/carpeta/cbg/
```

### 5. Descompresión de Scripts (`.ctd`)
Descomprime un archivo `.ctd` mediante `lenzu` y genera el binario limpio en `extracted/bin_ctd/`:
```bash
python cli.py decompress-ctd ruta/al/archivo.ctd
```
Si añades la bandera `-json`, se procesará el binario de forma encadenada usando `MahoyoScriptParserJSON`, generando un archivo estructurado listo para traducción en `extracted/json/`:
```bash
python cli.py decompress-ctd ruta/al/archivo.ctd -json
```

---

## Módulos Principales

* **`text_processor.py`:** Encapsula la descompresión con `lenzu_decompress` y coordina el flujo de extracción hacia la capa de parsing.
* **`MahoyoScriptParserJSON.py`:** Aplica filtros estrictos por expresiones regulares para desechar bytecode, comandos del motor y cadenas basura, generando una estructura JSON limpia con `id`, `original` y `traduccion`.
* **`hfa_reader.py`:** Maneja la lectura de archivos `.hfa`, generación de reportes por extensión, extracción organizada e inspección profunda de objetos y cabeceras binarias.
* **`graphics_processor.py`:** Gestor de procesamiento técnico de texturas e imágenes.
