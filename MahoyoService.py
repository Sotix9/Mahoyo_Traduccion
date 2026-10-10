import os
import sys
import re
import inspect
from io import BytesIO
from typing import List, Any, Optional, Dict, Optional, Union

# Configurar path a /tools/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.join(BASE_DIR, "mahoyo_tools")
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

from mahoyo_tools import hfa, cbg

class MahoyoHelper:

    """Capa de servicio que centraliza la interacción con mahoyo_tools."""


    # -------------------------------------------------------------------------
    # OPERACIONES HFA (Contenedores)
    # -------------------------------------------------------------------------

    @classmethod
    def obtener_entradas_hfa(cls, ruta_hfa: str) -> List[Any]:
        """Abre un contenedor HFA y devuelve la lista de entradas de forma segura."""
        if not os.path.exists(ruta_hfa):
            raise FileNotFoundError(f"No se encontró el archivo HFA: {ruta_hfa}")

        archive = hfa.HfaArchive(ruta_hfa)
        if hasattr(archive, 'open'):
            archive.open()
        return list(archive)

    @classmethod
    def listar_y_reportar_hfa(cls, ruta_hfa: str, ruta_reporte_txt: str) -> None:
        """Genera un archivo TXT con el desglose por extensión e índice del HFA."""
        entradas = cls.obtener_entradas_hfa(ruta_hfa)
        extensiones = {}
        lista_nombres = []

        for entry in entradas:
            nombre = getattr(entry, 'filename', str(entry))
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

    @classmethod
    def obtener_nombre_limpio_entrada(cls, entrada_hfa: Any) -> str:
        """Extrae de forma segura el nombre del archivo dentro de un _HfaEntry."""
        # 1. Intentar atributos comunes
        for attr in ['path', 'filename', 'name', 'file_name']:
            val = getattr(entrada_hfa, attr, None)
            if val and isinstance(val, str):
                return os.path.basename(val)

        # 2. Si es una representación de objeto tipo 'HFA_entry: nombre.cbg, offset = ...'
        repr_str = str(entrada_hfa)
        
        # Buscar patrón de nombre con extensión
        match = re.search(r'[\w\.-]+\.[\w]+', repr_str)
        if match:
            return match.group(0)

        # Fallback de seguridad
        return "archivo_extraido.bin"

    @classmethod
    def extraer_recurso_hfa(cls, entrada_hfa: Any, ruta_destino: str) -> bool:
        """Extrae un recurso individual de un HFA a una ruta especificada."""
        try:
            # Obtener solo el nombre del archivo limpio (ej: 'alphagradation020.cbg')
            nombre_archivo = cls.obtener_nombre_limpio_entrada(entrada_hfa)

            # Si la ruta dada es un directorio o una carpeta base, construir la ruta completa
            if os.path.isdir(ruta_destino) or not os.path.splitext(ruta_destino)[1]:
                os.makedirs(ruta_destino, exist_ok=True)
                ruta_final = os.path.join(ruta_destino, nombre_archivo)
            else:
                os.makedirs(os.path.dirname(os.path.abspath(ruta_destino)), exist_ok=True)
                ruta_final = ruta_destino

            # Extraer usando el método de mahoyo_tools
            if hasattr(entrada_hfa, 'extract'):
                entrada_hfa.extract(ruta_final)
            elif hasattr(entrada_hfa, 'read'):
                data = entrada_hfa.read()
                with open(ruta_final, 'wb') as f_out:
                    f_out.write(data)
            else:
                raise AttributeError("La entrada no expone método 'extract' ni 'read'.")

            print(f"[+] Archivo extraído correctamente en: {ruta_final}")
            return True

        except Exception as e:
            print(f"[-] Error al extraer {entrada_hfa}: {e}")
            return False


    # -------------------------------------------------------------------------
    # OPERACIONES CBG (Imágenes)
    # -------------------------------------------------------------------------

    @classmethod
    def cbg_a_png(cls, ruta_cbg: str, ruta_png: str) -> bool:
        """Convierte una imagen .cbg a .png estándar."""
        if not os.path.exists(ruta_cbg):
            print(f"[-] No existe el archivo CBG: {ruta_cbg}")
            return False

        try:
            os.makedirs(os.path.dirname(os.path.abspath(ruta_png)), exist_ok=True)
            with open(ruta_cbg, "rb") as f_in:
                cbg_obj = cbg.CompressedBG(f_in)
                cbg_obj.img_write(ruta_png, format="png")
            return True
        except Exception as e:
            print(f"[-] Error al convertir CBG a PNG ({ruta_cbg}): {e}")
            return False


    # -------------------------------------------------------------------------
    # OPERACIONES CTD (Scripts y Diálogos)
    # -------------------------------------------------------------------------
    
    @classmethod
    def extraer_script_ctd(cls, entrada_hfa: Any, ruta_destino_txt: str) -> bool:
        """
        Extrae un archivo .ctd de un HFA (descomprimiendo LenZuCompressor) 
        y guarda su contenido listo para análisis o traducción.
        """
        try:
            os.makedirs(os.path.dirname(os.path.abspath(ruta_destino_txt)), exist_ok=True)
            
            # Usar extract si el objeto lo ofrece (mahoyo_tools descomprime internamente)
            if hasattr(entrada_hfa, 'extract'):
                entrada_hfa.extract(ruta_destino_txt)
            elif hasattr(entrada_hfa, 'read'):
                content = entrada_hfa.read()
                with open(ruta_destino_txt, 'wb') as f_out:
                    f_out.write(content)
            else:
                raise AttributeError("La entrada HFA no expone método 'extract' ni 'read'.")

            print(f"[+] Script CTD extraído y descomprimido en: {ruta_destino_txt}")
            return True
        except Exception as e:
            print(f"[-] Error al extraer script CTD {entrada_hfa}: {e}")
            return False

    @classmethod
    def ctd_a_texto_plano(cls, ruta_ctd: str, ruta_txt_salida: str, encoding: str = "utf-8") -> bool:
        """
        Escanea un archivo binario .ctd descomprimido y extrae todas las cadenas
        de texto legibles a un archivo .txt independiente.
        """
        if not os.path.exists(ruta_ctd):
            print(f"[-] No se encontró el archivo CTD: {ruta_ctd}")
            return False

        try:
            with open(ruta_ctd, "rb") as f:
                data = f.read()

            # Buscar cadenas de texto (secuencias de caracteres imprimibles)
            # Cubre caracteres ASCII, UTF-8 y rango de diálogos
            import re
            patron = re.compile(rb'[\x20-\x7E\xC0-\xFF][\x80-\xBF]{1,3}|[\x20-\x7E]{3,}')
            coincidencias = patron.findall(data)

            lineas_extraidas = []
            for raw_bytes in coincidencias:
                try:
                    texto = raw_bytes.decode(encoding).strip()
                    # Filtrar basura binaria o comandos muy cortos
                    if len(texto) > 1 and not texto.startswith("LenZu"):
                        lineas_extraidas.append(texto)
                except UnicodeDecodeError:
                    continue

            os.makedirs(os.path.dirname(os.path.abspath(ruta_txt_salida)), exist_ok=True)
            with open(ruta_txt_salida, "w", encoding="utf-8") as f_out:
                f_out.write(f"# DUMP DE TEXTO DESDE: {os.path.basename(ruta_ctd)}\n")
                f_out.write("=" * 60 + "\n\n")
                for i, linea in enumerate(lineas_extraidas, 1):
                    f_out.write(f"[{i:04d}] {linea}\n")

            print(f"[+] Dump de texto generado correctamente en: {ruta_txt_salida}")
            return True

        except Exception as e:
            print(f"[-] Error procesando {ruta_ctd}: {e}")
            return False


    # -------------------------------------------------------------------------
    # MÓDULO DE DIAGNÓSTICO E INSPECCIÓN DE CLASES Y OBJETOS
    # -------------------------------------------------------------------------
    @classmethod
    def diagnosticar(cls, obj: Any, titulo: str = "INSPECCIÓN DE COMPONENTE") -> Dict[str, Any]:
        """
        Realiza un análisis exhaustivo de atributos, métodos, firmas de funciones
        e información implícita de cualquier objeto o clase.
        """
        print(f"\n==================================================")
        print(f" {titulo.upper()}")
        print(f"==================================================")
        
        tipo_objeto = type(obj)
        nombre_clase = tipo_objeto.__name__
        modulo = tipo_objeto.__module__
        print(f"[*] Clase: {nombre_clase} (Módulo: '{modulo}')")
        print(f"[*] Tipo: {tipo_objeto}")

        # 1. Separar atributos públicos entre callables (métodos) y propiedades
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

        # 2. Imprimir Métodos con sus Firmas Reales
        print(f"\n--- MÉTODOS Y FUNCIONES ({len(metodos)}) ---")
        if metodos:
            for nombre_m, firma in sorted(metodos.items()):
                print(f"  • {nombre_m}{firma}")
        else:
            print("  (No se encontraron métodos públicos)")

        # 3. Imprimir Propiedades y Estado Actual
        print(f"\n--- PROPIEDADES Y VALORES ({len(propiedades)}) ---")
        if propiedades:
            for nombre_p, tipo_p, val_p in sorted(propiedades, key=lambda x: x[0]):
                # Truncar representaciones de texto muy largas
                repr_val = str(val_p)
                if len(repr_val) > 70:
                    repr_val = repr_val[:67] + "..."
                print(f"  • {nombre_p} ({tipo_p}): {repr_val}")
        else:
            print("  (No se encontraron propiedades públicas)")

        print("==================================================\n")

        return {
            "clase": nombre_clase,
            "metodos": metodos,
            "propiedades": [p[0] for p in propiedades]
        }

    @classmethod
    def inspeccionar_stream_o_bytes(cls, data_or_stream: Union[bytes, BytesIO], max_bytes: int = 32) -> bytes:
        """
        Analiza cabeceras (magic bytes) sin alterar la posición original del puntero de lectura.
        """
        if isinstance(data_or_stream, BytesIO):
            pos_original = data_or_stream.tell()
            data_or_stream.seek(0)
            header = data_or_stream.read(max_bytes)
            data_or_stream.seek(pos_original)  # Restaurar puntero
        else:
            header = bytes(data_or_stream[:max_bytes])

        print(f"--- ANÁLISIS DE CABECERA (MAGIC BYTES) ---")
        print(f"[*] Tamaño de muestra: {len(header)} bytes")
        print(f"[*] Hexadecimal: {header.hex(' ')}")
        print(f"[*] Representación ASCII: {header}")
        print("------------------------------------------\n")
        return header
