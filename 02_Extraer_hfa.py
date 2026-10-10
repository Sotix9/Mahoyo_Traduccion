import os
from MahoyoService import MahoyoHelper

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
archivo_hfa = os.path.join(BASE_DIR, "WHN_Copy", "NOMBRE_ARCHIVO_HFA.hfa")
carpeta_salida = os.path.join(BASE_DIR, "extracted")

if __name__ == "__main__":

    entradas = MahoyoHelper.obtener_entradas_hfa(archivo_hfa)
    
    if entradas:
        primer_recurso = entradas[0]
        # Pasamos la carpeta de salida directamente, el Helper resolverá el nombre limpio
        MahoyoHelper.extraer_recurso_hfa(primer_recurso, carpeta_salida)
