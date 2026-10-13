# Proyecto de Traducción: Witch on the Holy Night (Mahoyo)

Herramientas de automatización y procesamiento en Python para la extracción, gestión, descompresión y análisis de recursos (scripts, contenedores y gráficos) de la novela visual *Witch on the Holy Night* (Mahoutsukai no Yoru).

## 📂 Estructura Modular del Proyecto

El proyecto está organizado bajo una arquitectura modular estricta para separar las responsabilidades de la interfaz de usuario, los parsers de formato y los motores de procesamiento central:

```text
01_proyecto_traduccion/
│
├── cli.py                  # Punto de entrada principal por consola (CLI)
├── extracted/              # Salidas autogestionadas (bin_ctd/, json/, etc.)
├── mahoyo_tools/           # Módulo base integrado para lenzu y contenedores HFA
├── parsers/                # Parsers de scripts y extracción de texto
│   └── MahoyoScriptParserJSON.py
├── reports/                # Informes de diagnóstico e índices de archivos
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
│
└── ps-hunex_tools/         # Herramienta externa para contenedores mrgd00 (.mzp)
```

---

## 🛠️ Requisitos y Dependencias

### 1. Dependencias de Python
Instala las librerías necesarias con el siguiente comando:
```bash
pip install numpy Pillow cffi imagequant
```

### 2. Repositorios y Herramientas Integradas
* **mahoyo_tools:** Módulo de Python base para la interacción con descompresión LenZu y contenedores HFA.
  * [mahoyo_tools en GitHub](https://github.com/loicfrance/mahoyo_tools.git)
* **PS-HuneX_Tools:** Soporte para contenedores gráficos con firma `mrgd00` (`.mzp`) y descompresión MZX0.
  * [PS-HuneX_Tools en GitHub](https://github.com/Hintay/PS-HuneX_Tools.git)
* **MahoyoHDRepack:** Referencia externa en C# / .NET para exportación/importación de diálogos.
  * [MahoyoHDRepack en GitHub](https://github.com/nike4613/MahoyoHDRepack.git)

---

## 🚀 Uso de la Línea de Comandos (CLI)

La interfaz central se gestiona a través de `cli.py`. Para ver las opciones globales:
```bash
python cli.py --help
```

### 1. Descompresión de Scripts (`.ctd`)
Descomprime un archivo `.ctd` mediante `lenzu` y genera el binario limpio en `extracted/bin_ctd/`:
```bash
python cli.py decompress-ctd ruta/al/archivo.ctd
```

#### Extraer binario y generar JSON en un solo paso:
Si añades la bandera `--json`, se procesará el binario de forma encadenada usando `MahoyoScriptParserJSON`, generando un archivo estructurado listo para traducción en `extracted/json/`:
```bash
python cli.py decompress-ctd ruta/al/archivo.ctd --json
```

### 2. Parseo Independiente a JSON
Si ya cuentas con un binario descomprimido en `extracted/bin_ctd/` y deseas extraer sus textos a JSON sin volver a ejecutar LenZu:
```bash
python cli.py parse-json ruta/al/archivo_descomprimido.bin
```

### 3. Diagnóstico e Inspección
Realiza un análisis de metadatos o inspección de *magic bytes* para contenedores o streams binarios:
```bash
python cli.py diagnose ruta/al/archivo.hfa
```

---

## 🧩 Módulos Principales

* **`text_processor.py`:** Encapsula la descompresión con `lenzu_decompress` y coordina el flujo de extracción hacia la capa de parsing.
* **`MahoyoScriptParserJSON.py`:** Aplica filtros estrictos por expresiones regulares para desechar bytecode, comandos del motor y cadenas basura, generando una estructura JSON limpia con `id`, `original` y `traduccion`.
* **`hfa_reader.py`:** Maneja la lectura de archivos `.hfa`, generación de reportes por extensión, extracción organizada e inspección profunda de objetos y cabeceras binarias.
* **`graphics_processor.py`:** Gestor de procesamiento técnico de texturas e imágenes.