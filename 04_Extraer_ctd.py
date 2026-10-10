import os
from MahoyoService import MahoyoHelper

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Rutas del contenedor y de la carpeta de destino
archivo_hfa = os.path.join(BASE_DIR, "WHN_Copy", "NOMBRE_ARCHIVO_HFA.hfa")
carpeta_salida_scripts = os.path.join(BASE_DIR, "extracted_ctd")

if __name__ == "__main__":
    print(f"[*] Inspeccionando contenedor: {archivo_hfa}")
    
    # 1. Obtener todas las entradas del HFA usando la capa de servicio
    entradas = MahoyoHelper.obtener_entradas_hfa(archivo_hfa)
    
    # 2. Filtrar únicamente las entradas con extensión .ctd
    scripts_ctd = [
        e for e in entradas 
        if MahoyoHelper.obtener_nombre_limpio_entrada(e).lower().endswith(".ctd")
    ]
    
    print(f"[+] Archivos .ctd detectados: {len(scripts_ctd)}")
    
    # 3. Procesar y extraer cada script .ctd (descomprimiendo LenZuCompressor)
    if scripts_ctd:
        for entrada in scripts_ctd:
            nombre_limpio = MahoyoHelper.obtener_nombre_limpio_entrada(entrada)
            ruta_destino = os.path.join(carpeta_salida_scripts, nombre_limpio)
            
            MahoyoHelper.extraer_script_ctd(entrada, ruta_destino)
            
        print(f"\n[!] Proceso finalizado. Todos los scripts .ctd están listos en: {carpeta_salida_scripts}")
    else:
        print("[-] No se encontraron archivos .ctd en este contenedor HFA.")
