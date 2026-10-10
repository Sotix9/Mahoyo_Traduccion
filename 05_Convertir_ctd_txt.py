import os
from MahoyoService import MahoyoHelper

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

carpeta_ctd = os.path.join(BASE_DIR, "extracted_ctd")
carpeta_txt = os.path.join(BASE_DIR, "extracted_txt")

if __name__ == "__main__":
    if os.path.exists(carpeta_ctd):
        archivos = [f for f in os.listdir(carpeta_ctd) if f.endswith(".ctd")]
        print(f"[*] Archivos .ctd a procesar: {len(archivos)}")

        for archivo in archivos:
            ruta_origen = os.path.join(carpeta_ctd, archivo)
            ruta_destino = os.path.join(carpeta_txt, f"{archivo}.txt")
            
            MahoyoHelper.ctd_a_texto_plano(ruta_origen, ruta_destino)
            
        print(f"\n[!] Texto extraído correctamente en: {carpeta_txt}")
    else:
        print(f"[-] No existe la carpeta {carpeta_ctd}")
