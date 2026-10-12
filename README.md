# Proyecto de Traducción: Witch on the Holy Night (Mahoyo)

Herramientas de automatización y procesamiento en Python para la extracción, gestión y análisis de recursos (scripts, contenedores y gráficos) de la novela visual "Witch on the Holy Night" (Mahoyo).

## Estructura Modular del Proyecto
El proyecto se encuentra organizado bajo una arquitectura modular clara para separar las responsabilidades de análisis, parsing y procesamiento gráfico:

- `cli.py` -> Punto de entrada principal por consola.
- `parsers/` -> Módulos encargados de procesar scripts (como el parsing binario de `.ctd` y exportación a texto/JSON).
- `src/core/` -> Núcleo del procesamiento técnico:
  - `graphics_processor.py` -> Manejo y conversión de recursos gráficos (integrando `PS-HuneX_Tools` para `.mzp`, tiles y `.cbg`).
  - `hfa_reader.py` -> Lector y gestor de contenedores `.hfa`.
- `src/utils/` -> Utilidades de soporte y scripts de laboratorio/diagnóstico (`scripts_prueba/`).
- `ps-hunex_tools/` -> Repositorio externo integrado para el soporte de archivos con firma `mrgd00` (`.mzp`).
- `extracted/` & `reports/` -> Directorios autogestionados para salidas de dumps, imágenes PNG e informes de diagnóstico.

## Requisitos y Dependencias Externas

1. **mahoyo_tools (Librería base):**
   Módulo base de Python necesario para la interacción inicial con los contenedores. Debe ubicarse en la raíz del proyecto.
   - Repositorio: [mahoyo_tools en GitHub](https://github.com/loicfrance/mahoyo_tools.git)

2. **PS-HuneX_Tools (Soporte gráfico HuneX):**
   Herramientas de la comunidad para la descompresión de contenedores `.mzp` y descompresión MZX0.
   - Repositorio: [PS-HuneX_Tools en GitHub](https://github.com/Hintay/PS-HuneX_Tools.git)

3. **MahoyoHDRepack:**
   - Herramienta de soporte en C# / .NET para el flujo limpio de exportación e importación de diálogos en formato CSV.
   - Repositorio: [MahoyoHDRepack en GitHub](https://github.com/nike4613/MahoyoHDRepack.git)

4. **Librerías de Python:**
   Instala las dependencias necesarias ejecutando:
   ```bash
   pip install numpy Pillow cffi imagequant
   ```

## Uso
Ejecuta el script principal de la interfaz por consola para gestionar las extracciones:
```bash
python cli.py