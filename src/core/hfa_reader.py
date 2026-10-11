import os
import re
from typing import List, Any, Optional
from mahoyo_tools import hfa

class HfaReader:
    """Clase especializada en la lectura y extracción de contenedores HFA."""

    @staticmethod
    def obtener_entradas(ruta_hfa: str) -> List[Any]:
        """Abre un contenedor HFA y devuelve la lista de entradas de forma segura."""
        if not os.path.exists(ruta_hfa):
            raise FileNotFoundError(f"No se encontró el archivo HFA: {ruta_hfa}")

        archive = hfa.HfaArchive(ruta_hfa)
        if hasattr(archive, 'open'):
            archive.open()
        return list(archive)

    @classmethod
    def generar_reporte(cls, ruta_hfa: str, ruta_reporte_txt: str) -> None:
        """Genera un archivo TXT con el desglose por extensión e índice del HFA."""
        entradas = cls.obtener_entradas(ruta_hfa)
        extensiones = {}
        lista_nombres = []

        for entry in entradas:
            nombre = cls.obtener_nombre_limpio(entry)
            lista_nombres.append(nombre)
            ext = os.path.splitext(nombre)[1].lower()
            extensiones[ext] = extensiones.get(ext, 0) + 1

        os.makedirs(os.path.dirname(os.path.abspath(ruta_reporte_txt)), exist_ok=True)
        with open(ruta_reporte_txt, "w", encoding="utf-8") as f:
            f.write(f"ÍNDICE DE CONTENIDO: {os.path.basename(ruta_hfa)}\n")
            f.write(f"Total de archivos: {len(lista_nombres)}\n")
            f.write("=" * 50 + "\n\n")
            f.write("RESUMEN POR EXTENSIÓN:\n")
            for ext, count in sorted(extensiones.items(), key=lambda x: x[1], reverse=True):
                f.write(f"  {ext if ext else '[Sin extensión]'}: {count} archivos\n")
            f.write("\n" + "=" * 50 + "\n\n")
            f.write("LISTA COMPLETA DE ARCHIVOS:\n")
            for nombre in lista_nombres:
                f.write(f"{nombre}\n")

        print(f"[+] Índice generado exitosamente en: {ruta_reporte_txt}")

    @staticmethod
    def obtener_nombre_limpio(entrada_hfa: Any) -> str:
        """Extrae de forma segura el nombre del archivo dentro de una entrada HFA."""
        for attr in ['path', 'filename', 'name', 'file_name']:
            val = getattr(entrada_hfa, attr, None)
            if val and isinstance(val, str):
                return os.path.basename(val)

        repr_str = str(entrada_hfa)
        match = re.search(r'[\w\.-]+\.[\w]+', repr_str)
        if match:
            return match.group(0)

        return "archivo_extraido.bin"

    @classmethod
    def extraer_recursos(cls, ruta_hfa: str, carpeta_destino_base: str = "extracted", filtrar_extension: Optional[str] = None) -> int:
        """
        Extrae recursos de un HFA organizándolos automáticamente en subcarpetas según su extensión.
        """
        entradas = cls.obtener_entradas(ruta_hfa)
        contador = 0

        for entry in entradas:
            nombre_archivo = cls.obtener_nombre_limpio(entry)
            ext = os.path.splitext(nombre_archivo)[1].lower()

            # Si se especificó un filtro y no coincide, saltar
            if filtrar_extension and ext != filtrar_extension.lower():
                continue

            # Determinar subcarpeta dinámica según la extensión (ej: .ctd -> extracted/ctd/)
            nombre_carpeta_ext = ext.replace(".", "") if ext else "sin_extension"
            carpeta_destino_final = os.path.join(carpeta_destino_base, nombre_carpeta_ext)
            os.makedirs(carpeta_destino_final, exist_ok=True)

            ruta_final = os.path.join(carpeta_destino_final, nombre_archivo)

            try:
                if hasattr(entry, 'extract'):
                    entry.extract(ruta_final)
                elif hasattr(entry, 'read'):
                    data = entry.read()
                    with open(ruta_final, 'wb') as f_out:
                        f_out.write(data)
                else:
                    print(f"[-] Advertencia: La entrada {nombre_archivo} no expone métodos de extracción.")
                    continue
                
                contador += 1
            except Exception as e:
                print(f"[-] Error al extraer {nombre_archivo}: {e}")

        print(f"[+] Se extrajeron {contador} archivos correctamente en carpetas organizadas bajo: {carpeta_destino_base}")
        return contador