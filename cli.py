import sys
import os

# Añadir la carpeta 'src' al path de Python para importar los módulos internos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import argparse
from core.hfa_reader import HfaReader
from core.graphics_processor import GraphicsProcessor
from core.text_processor import LenzuDecompressor
from parsers.MahoyoScriptParserJSON import MahoyoScriptParserJSON

def main():
    parser = argparse.ArgumentParser(
        description="CLI oficial para el Proyecto de Traducción de Witch on the Holy Night (Mahoyo)."
    )
    subparsers = parser.add_subparsers(dest="command", help="Comando principal a ejecutar")

    # Comando 1: Listar
    parser_list = subparsers.add_parser("list", help="Lista y genera un reporte del contenido de un archivo HFA.")
    parser_list.add_argument("-i", "--input", required=True, help="Ruta al archivo .hfa de entrada.")
    parser_list.add_argument("-o", "--output", default="reports/reporte_hfa.txt", help="Ruta del archivo de reporte TXT de salida.")

    # Comando 2: Extraer (con organización automática por subcarpetas de extensión)
    parser_extract = subparsers.add_parser("extract", help="Extrae recursos de un archivo HFA organizándolos por extensión.")
    parser_extract.add_argument("-i", "--input", required=True, help="Ruta al archivo .hfa de entrada.")
    parser_extract.add_argument("-o", "--output", default="extracted", help="Carpeta base de destino.")
    parser_extract.add_argument("-ext", default=None, help="Filtrar por extensión específica (ej: .ctd, .cbg, .mzp, .ccti, .chs, .hw).")

    # Comando 3: Conversión CBG a PNG por lotes con límite y reubicación
    parser_allcbg2png = subparsers.add_parser("allcbg2png", help="Convierte archivos .cbg a .png de forma masiva con control de lotes y reubicación")
    parser_allcbg2png.add_argument("-i", "--input", required=True, help="Carpeta de entrada que contiene los archivos .cbg")
    parser_allcbg2png.add_argument("-o", "--output", required=False, help="Carpeta de salida opcional para los PNGs")
    parser_allcbg2png.add_argument("-a", "--archive", required=False, help="Carpeta opcional para mover los CBG procesados")
    parser_allcbg2png.add_argument("-lim", type=int, required=False, help="Cantidad máxima de archivos a procesar en este lote")

    # Comando 4: Conversión MZP a PNG por lotes con límite y reubicación
    parser_allmzp2png = subparsers.add_parser("allmzp2png", help="Convierte archivos .mzp a .png de forma masiva con control de lotes y reubicación")
    parser_allmzp2png.add_argument("-i", "--input", required=True, help="Carpeta de entrada que contiene los archivos .mzp")
    parser_allmzp2png.add_argument("-o", "--output", required=False, help="Carpeta de salida opcional para los PNGs")
    parser_allmzp2png.add_argument("-a", "--archive", required=False, help="Carpeta opcional para mover los MZP procesados")
    parser_allmzp2png.add_argument("-lim", type=int, required=False, help="Cantidad máxima de archivos a procesar en este lote")
    
    # Comando 5: Procesamiento LenZu (Descompresión / Compresión)
    parser_lenzu = subparsers.add_parser("lenzu", help="Ejecuta operaciones con el algoritmo LenZu (descomprimir o comprimir archivos .ctd/.bin).")
    # Grupo mutuamente exclusivo o banderas de acción
    grupo_accion = parser_lenzu.add_mutually_exclusive_required = True
    parser_lenzu.add_argument("-decompress", action="store_true", help="Descomprime un archivo .ctd usando LenZu.")
    parser_lenzu.add_argument("-compress", action="store_true", help="Comprime un archivo binario modificado de vuelta a formato LenZu.")
    # Argumentos de entrada y salida
    parser_lenzu.add_argument("-i", "--input", required=True, help="Ruta al archivo de entrada (.ctd para descomprimir o .bin para comprimir).")
    parser_lenzu.add_argument("-o", "--output", default=None, help="Carpeta o ruta de salida opcional.")
    # Bandera auxiliar específica para el flujo de descompresión con JSON
    parser_lenzu.add_argument("-json", action="store_true", help="[Solo descompresión] Generar automáticamente el JSON de traducción.")

    # Comando 6: Parseo independiente a JSON
    parser_jsonparse = subparsers.add_parser("jsonparse", help="Parsea un archivo .bin descompreso a un archivo JSON estructurado.")
    parser_jsonparse.add_argument("-i", "--input", required=True, help="Ruta al archivo .bin de entrada.")
    parser_jsonparse.add_argument("-o", "--output", default=None, help="Ruta o carpeta de salida opcional para el JSON (por defecto: extracted/json/)")

    # Comando 7: Reinyección de archivos modificados al HFA
    parser_inject = subparsers.add_parser("inject", help="Reinyecta un archivo modificado (ej: .ctd traducido) dentro de un contenedor HFA.")
    parser_inject.add_argument("-hfa", required=True, help="Ruta al archivo .hfa del juego donde se aplicará el cambio.")
    parser_inject.add_argument("-t", "--target", required=True, help="Nombre o ruta interna de la entrada dentro del HFA (ej: script_text_en.ctd).")
    parser_inject.add_argument("-f", "--file", required=True, help="Ruta al archivo binario/.ctd modificado listo para inyectar.")


    args = parser.parse_args()

    if args.command == "list":
        print(f"[*] Analizando HFA: {args.input}")
        HfaReader.generar_reporte(args.input, args.output)

    elif args.command == "extract":
        print(f"[*] Extrayendo recursos de: {args.input} (Filtro: {args.ext or 'Todos'})")
        HfaReader.extraer_recursos(args.input, carpeta_destino_base=args.output, filtrar_extension=args.ext)

    elif args.command == "allcbg2png":
        GraphicsProcessor.procesar_recurso_grafico(
            entrada=args.input,
            extension=".cbg",
            carpeta_salida=args.output,
            carpeta_procesados=args.archive,
            limite=args.lim
        )

    elif args.command == "allmzp2png":
        GraphicsProcessor.procesar_recurso_grafico(
            entrada=args.input,
            extension=".mzp",
            carpeta_salida=args.output,
            carpeta_procesados=args.archive,
            limite=args.lim
        )

    elif args.command == "lenzu":
        if args.decompress and args.compress:
            print("[-] Error: No puedes especificar --decompress y --compress al mismo tiempo.")
            return

        if args.compress and args.json:
            print("[-] Advertencia/Error: La bandera -json no es aplicable durante la compresión. El JSON se usa para traducir antes de compilar.")
            return

        if args.decompress:
            print(f"[*] Ejecutando descompresión LenZu en: {args.input}")
            LenzuDecompressor.descompresion_ctd_lenzu(
                ruta_ctd=args.input,
                carpeta_salida_bin=args.output or "extracted/bin_ctd",
                parsear_a_json=args.json,
                carpeta_salida_json="extracted/json"
            )
            
        elif args.compress:
            print(f"[*] Ejecutando compresión para reinyección en: {args.input}")
            # Lógica de compresión futura...

    elif args.command == "parse-json":
        try:
            print(f"[*] Iniciando parseo estructurado del binario: {args.input}")
            parser = MahoyoScriptParserJSON(args.input)
            ruta_resultado = parser.extraer_textos_filtrados(args.output)
            print(f"[+] ¡Proceso finalizado con éxito! JSON guardado en: {ruta_resultado}")
        except Exception as e:
            print(f"[-] Error al parsear el binario a JSON: {e}")

    elif args.command == "inject":
        print(f"[*] Preparando reinyección para la entrada '{args.target}' en: {args.hfa}")
        HfaReader.reinyectar_archivo_hfa(
            ruta_hfa=args.hfa,
            nombre_entrada_objetivo=args.target,
            ruta_nuevo_archivo=args.file
        )

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
