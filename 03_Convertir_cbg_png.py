import os
from MahoyoService import MahoyoHelper

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

archivo_cbg = os.path.join(BASE_DIR, "extracted", "alphagradation020.cbg")
imagen_png = os.path.join(BASE_DIR, "extracted_cbg", "alphagradation020.png")

if __name__ == "__main__":
    if MahoyoHelper.cbg_a_png(archivo_cbg, imagen_png):
        print(f"[+] Imagen PNG convertida con éxito en: {imagen_png}")
