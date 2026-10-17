import os
import re
import inspect
from io import BytesIO
from typing import List, Any, Optional, Union, Dict
from mahoyo_tools import hfa

class HfaReader:
    """Clase especializada en la lectura y extracción de contenedores HFA."""

    @staticmethod
    def obtener_entradas(ruta_hfa: str) -> List[Any]:
        """Abre un contenedor HFA y devuelve la lista de entradas de forma segura."""
        if not os.path.exists(ruta_hfa):
            raise FileNotFoundError(f"No se encontró el archivo HFA: {ruta_hfa}")

        with hfa.HfaArchive(ruta_hfa) as archive:
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

    def reinyectar_archivo_hfa(ruta_hfa: str, nombre_entrada_ctd: str, ruta_nuevo_ctd: str):
        """Abre el contenedor HFA en modo lectura/escritura ('rw') e inyecta el script traducido."""
        with hfa.HfaArchive(ruta_hfa, mode='rw') as archive:
            if nombre_entrada_ctd in archive:
                # El método inject demahoyo_tools se encarga de empaquetarlo en el contenedor
                archive[nombre_entrada_ctd].inject(ruta_nuevo_ctd)
                print(f"[+] Script {nombre_entrada_ctd} reinyectado correctamente en {ruta_hfa}")
            else:
                print(f"[-] No se encontró la entrada {nombre_entrada_ctd} en el archivo HFA.")
                

    
####################################### DIAGNÓSTICO #######################################


    @classmethod
    def diagnosticar_objeto(cls, obj: Any, titulo: str = "INSPECCIÓN DE COMPONENTE") -> dict:
        """
        Realiza un análisis exhaustivo de atributos, métodos (con sus firmas reales) 
        y propiedades de cualquier objeto o clase del sistema.
        """
        print(f"\n==================================================")
        print(f" {titulo.upper()}")
        print(f"==================================================")
        
        tipo_objeto = type(obj)
        nombre_clase = tipo_objeto.__name__
        modulo = tipo_objeto.__module__
        print(f"[*] Clase: {nombre_clase} (Módulo: '{modulo}')")
        print(f"[*] Tipo: {tipo_objeto}")

        atributos_todos = [a for a in dir(obj) if not a.startswith('__')]
        propiedades = []
        metodos = {}

        for attr in atributos_todos:
            try:
                valor = getattr(obj, attr)
                if callable(valor):
                    try:
                        sig = inspect.signature(valor)
                        metodos[attr] = str(sig)
                    except (ValueError, TypeError):
                        metodos[attr] = "(...)"
                else:
                    propiedades.append((attr, type(valor).__name__, valor))
            except Exception as e:
                propiedades.append((attr, "ERROR", f"No accesible ({e})"))

        print(f"\n--- MÉTODOS Y FUNCIONES ({len(metodos)}) ---")
        if metodos:
            for nombre_m, firma in sorted(metodos.items()):
                print(f"  • {nombre_m}{firma}")
        else:
            print("  (No se encontraron métodos públicos)")

        print(f"\n--- PROPIEDADES Y VALORES ({len(propiedades)}) ---")
        if propiedades:
            for nombre_p, tipo_p, val_p in sorted(propiedades, key=lambda x: x[0]):
                repr_val = str(val_p)
                if len(repr_val) > 70:
                    repr_val = repr_val[:67] + "..."
                print(f"  • {nombre_p} ({tipo_p}): {repr_val}")
        else:
            print("  (No se encontraron propiedades públicas)")

        print("==================================================\n")
        return {"clase": nombre_clase, "metodos": metodos, "propiedades": [p[0] for p in propiedades]}

    @staticmethod
    def inspeccionar_stream_o_bytes(data_or_stream: Union[bytes, BytesIO, str], max_bytes: int = 32) -> bytes:
        """
        Analiza cabeceras (magic bytes) de cualquier archivo o stream de forma segura,
        sin alterar la posición original del puntero de lectura.
        """
        if isinstance(data_or_stream, str):
            with open(data_or_stream, "rb") as f:
                header = f.read(max_bytes)
        elif isinstance(data_or_stream, BytesIO):
            pos_original = data_or_stream.tell()
            data_or_stream.seek(0)
            header = data_or_stream.read(max_bytes)
            data_or_stream.seek(pos_original)
        else:
            header = bytes(data_or_stream[:max_bytes])

        print(f"--- ANÁLISIS DE CABECERA (MAGIC BYTES) ---")
        print(f"[*] Tamaño de muestra: {len(header)} bytes")
        print(f"[*] Hexadecimal: {header.hex(' ')}")
        print(f"[*] Representación ASCII: {header}")
        print("------------------------------------------\n")
        return header

'''
Bloque no implemmentado en 'cli.py' aún, pero su función es inspeccionar las funciones o atributos de una librería
para aplicar a un objeto específico. 

Por ejemplo, una solución a dicho problema en el intento de conversión de un CBG a PNG:
Resultado: "Atributos disponibles en cbg: ['Any', 'BitStreamReader', 'BitStreamWriter', 'BufferedWriter', 
            'ByteHuffmanTable', 'BytesIO', 'BytesRW', 'BytesReader', 'BytesWriter', 'CBG_MAGIC', 'CompressedBG', <- siendo este el que se necesitaba
            'Image', 'TYPE_CHECKING', 'cast', 'ceil', 'np', 'overload', 'read_variable', 'struct', 'write_variable']"

Parámetros del header de los archivos `.ctd`:

[*] Archivos .ctd a procesar: 4

Firma detectada: LenZuCompressor
Parámetro A (Hex): 31000000
Parámetro B (Hex): 30000000
Tamaño del bloque comprimido: 771770 bytes

Firma detectada: LenZuCompressor
Parámetro A (Hex): 31000000
Parámetro B (Hex): 30000000
Tamaño del bloque comprimido: 895856 bytes

Firma detectada: LenZuCompressor
Parámetro A (Hex): 31000000
Parámetro B (Hex): 30000000
Tamaño del bloque comprimido: 806301 bytes

Firma detectada: LenZuCompressor
Parámetro A (Hex): 31000000
Parámetro B (Hex): 30000000
Tamaño del bloque comprimido: 810340 bytes

'''
