# Proyecto Académico de traducción

Herramientas de automatización y procesamiento en Python para la extracción, gestión y futura reinyección de diálogos de la VN "Witch on the Holy Night" (Mahoyo).

## Estructura del Proyecto
Al ejecutar los scripts por primera vez, el sistema autogestionará y creará localmente las siguientes carpetas de trabajo:
- `reports/` -> Reportes y listados del contenido de los contenedores `.hfa`.
- `extracted/` -> Recursos generales extraídos.
- `extracted_cbg/` -> Imágenes convertidas o procesadas.
- `extracted_ctd/` -> Scripts de diálogos originales.
- `extracted_txt/` -> Dumps de texto y archivos intermedios de trabajo.

## Requisitos y Dependencias Externas
1. **mahoyo_tools (Librería base de Python):**
   Es obligatoria para que la capa de servicio funcione. Debes clonarla o instalarla dentro de tu entorno de trabajo:
   - Repositorio oficial: [mahoyo_tools en GitHub](https://github.com/loicfrance/mahoyo_tools.git)
   - Ubicarla en la carpeta `tools/` de este proyecto tal como se especifica en la configuración de rutas de los scripts.
     
2. **MahoyoHDRepack:**
   Herramienta de soporte para el desempaquetado y empaquetado avanzado de scripts. Descárgala desde su repositorio oficial: [MahoyoHDRepack en GitHub](https://github.com/nike4613/MahoyoHDRepack).

## Uso
1. Clona este repositorio o descárgalo en ZIP.
2. Asegúrate de tener Python instalado y ejecuta los scripts principales para inicializar el entorno de trabajo local.
