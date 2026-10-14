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

def main():
    parser = argparse.ArgumentParser(
        description="CLI oficial para el Proyecto de Traducción de Witch on the Holy Night (Mahoyo)."
    )
    subparsers = parser.add_subparsers(dest="command", help="Comando principal a ejecutar")

    # Comando 1: Listar
    parser_list = subparsers.add_parser("list", help="Lista y genera un reporte del contenido de un archivo HFA.")
    parser_list.add_argument("-hfa", required=True, help="Ruta al archivo .hfa de entrada.")
    parser_list.add_argument("-output", default="reports/reporte_hfa.txt", help="Ruta del archivo de reporte TXT de salida.")

    # Comando 2: Extraer (con organización automática por subcarpetas de extensión)
    parser_extract = subparsers.add_parser("extract", help="Extrae recursos de un archivo HFA organizándolos por extensión.")
    parser_extract.add_argument("-hfa", required=True, help="Ruta al archivo .hfa de entrada.")
    parser_extract.add_argument("-output", default="extracted", help="Carpeta base de destino.")
    parser_extract.add_argument("-ext", default=None, help="Filtrar por extensión específica (ej: .ctd, .cbg, .mzp, .ccti, .chs, .hw).")

    # Comando 3: Conversión CBG a PNG por lotes con límite y reubicación
    parser_allcbg2png = subparsers.add_parser("allcbg2png", help="Convierte archivos .cbg a .png de forma masiva con control de lotes y reubicación")
    parser_allcbg2png.add_argument("-input", required=True, help="Carpeta de entrada que contiene los archivos .cbg")
    parser_allcbg2png.add_argument("-output", required=False, help="Carpeta de salida opcional para los PNGs")
    parser_allcbg2png.add_argument("-processed", required=False, help="Carpeta opcional para mover los CBG procesados")
    parser_allcbg2png.add_argument("-limit", type=int, required=False, help="Cantidad máxima de archivos a procesar en este lote")

    # Comando 4: Conversión MZP a PNG por lotes con límite y reubicación
    parser_allmzp2png = subparsers.add_parser("allmzp2png", help="Convierte archivos .mzp a .png de forma masiva y los reubica")
    parser_allmzp2png.add_argument("-input", required=True, help="Carpeta de entrada que contiene los archivos .mzp")
    parser_allmzp2png.add_argument("-output", required=False, help="Carpeta de salida opcional para los PNGs")
    parser_allmzp2png.add_argument("-processed", required=False, help="Carpeta opcional para mover los MZP procesados")
    parser_allmzp2png.add_argument("-limit", type=int, required=False, help="Cantidad máxima de archivos a procesar en este lote")
    
    # Comando 5: Descompresión CTD
    parser_ctd = subparsers.add_parser("decompress-ctd", help="Descomprime un archivo .ctd usando LenZu")
    parser_ctd.add_argument("-input", help="Ruta al archivo .ctd de entrada")
    parser_ctd.add_argument("-bin_dir", default="extracted/bin_ctd", help="Carpeta de salida para el binario")
    parser_ctd.add_argument("-json", action="store_true", help="Generar automáticamente el JSON de traducción")
    parser_ctd.add_argument("-json_dir", default="extracted/json", help="Carpeta de salida para el JSON")

    args = parser.parse_args()

    if args.command == "list":
        print(f"[*] Analizando HFA: {args.hfa}")
        HfaReader.generar_reporte(args.hfa, args.output)

    elif args.command == "extract":
        print(f"[*] Extrayendo recursos de: {args.hfa} (Filtro: {args.ext or 'Todos'})")
        HfaReader.extraer_recursos(args.hfa, carpeta_destino_base=args.output, filtrar_extension=args.ext)

    elif args.command == "allcbg2png":
        GraphicsProcessor.convertir_directorio_cbg_con_limite(
            carpeta_entrada=args.input,
            carpeta_salida=args.output,
            carpeta_procesados=args.processed,
            limite=args.limit
        )

    elif args.command == "allmzp2png":
        GraphicsProcessor.convertir_directorio_mzp_con_limite(
            carpeta_entrada=args.input,
            carpeta_salida=args.output,
            carpeta_procesados=args.processed,
            limite=args.limit
        )

    elif args.command == "decompress-ctd":
        LenzuDecompressor.descompresion_ctd_lenzu(
            ruta_ctd=args.input,
            carpeta_salida_bin=args.bin_dir,
            parsear_a_json=args.json,
            carpeta_salida_json=args.json_dir
        )

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
