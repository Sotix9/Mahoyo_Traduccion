import os
from MahoyoService import MahoyoHelper

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
archivo_hfa = os.path.join(BASE_DIR, "WHN_Copy", "data00000.hfa")

if __name__ == "__main__":
    # 1. Diagnóstico sobre la lista de entradas HFA
    entradas = MahoyoHelper.obtener_entradas_hfa(archivo_hfa)
    
    if entradas:
        primer_recurso = entradas[0]
        
        # Diagnóstico automático completo sobre la entrada (_HfaEntry)
        MahoyoHelper.diagnosticar(primer_recurso, "DIAGNÓSTICO: ENTRADA HFA")

        # 2. Si leemos el contenido del archivo en bytes, inspeccionar cabecera
        if hasattr(primer_recurso, 'read'):
            raw_bytes = primer_recurso.read()
            MahoyoHelper.inspeccionar_stream_o_bytes(raw_bytes)