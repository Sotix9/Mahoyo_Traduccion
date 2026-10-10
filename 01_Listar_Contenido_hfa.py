import os
from MahoyoService import MahoyoHelper

def inicializar_entorno():
    """Crea automáticamente la estructura de carpetas local si no existe."""
    directorios = ["WHN_Copy", "tools", "MahoyoHDRepack", "reports", "extracted", "extracted_cbg", "extracted_ctd", "extracted_txt", "translated"]
    for directorio in directorios:
        os.makedirs(directorio, exist_ok=True)
    print("[+] Entorno de carpetas verificado y preparado.")

if __name__ == "__main__":
    # 1. Crear carpetas automáticamente
    inicializar_entorno()

    # 2. Definir ruta del archivo HFA local y ejecutar la lógica de servicio
    ruta_hfa_local = "data00000.hfa"  # Archivo de ejemplo compartido
    reporte_txt = os.path.join("reports", "reporte_hfa.txt")

    if os.path.exists(ruta_hfa_local):
        MahoyoHelper.listar_y_reportar_hfa(ruta_hfa_local, reporte_txt)
    else:
        print(f"[-] Coloca el archivo {ruta_hfa_local} en la raíz para comenzar la prueba.")