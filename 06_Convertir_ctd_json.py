import json
import re
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def is_clean_text(text):
    """
    Determina si una línea es texto legible descartando basura binaria.
    """
    # Eliminar espacios laterales
    cleaned = text.strip()
    
    # Descartar cadenas muy cortas o sin letras
    if len(cleaned) < 3 or not re.search(r'[a-zA-Z]', cleaned):
        return False
        
    # Descartar patrones típicos de datos binarios / opcodes (símbolos raros seguidos)
    # Si más del 30% de los caracteres son símbolos no alfanuméricos ni puntuación básica, es basura
    garbage_chars = len(re.findall(r'[^a-zA-Z0-9\s\.,\'"\!\?\-\–\—]', cleaned))
    if garbage_chars / len(cleaned) > 0.30:
        return False

    return True

def clean_and_extract_to_json(input_file, output_json):
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        raw_lines = f.readlines()

    clean_dialogues = []
    current_phrase = []
    
    for line in raw_lines:
        line_str = line.strip()
        
        if is_clean_text(line_str):
            # Limpiar caracteres raros sobrantes dentro de la línea
            sanitized = re.sub(r'[^a-zA-Z0-9\s\.,\'"\!\?\-\–\—]', '', line_str).strip()
            if sanitized:
                current_phrase.append(sanitized)
        else:
            # Si encontramos basura binaria, consolidamos lo que habíamos juntado hasta ahora
            if current_phrase:
                full_text = " ".join(current_phrase)
                # Guardamos solo si la frase consolidada tiene al menos 2 palabras
                if len(full_text.split()) >= 2:
                    clean_dialogues.append(full_text)
                current_phrase = []

    # Caso de borde al finalizar el archivo
    if current_phrase:
        full_text = " ".join(current_phrase)
        if len(full_text.split()) >= 2:
            clean_dialogues.append(full_text)

    # Formatear a lista de objetos para el traductor
    output_data = []
    for idx, text in enumerate(clean_dialogues, 1):
        output_data.append({
            "id": idx,
            "english": text,
            "spanish": ""
        })

    # Exportar a JSON
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    print(f" Proceso completado: Se extrajeron {len(output_data)} frases limpias en '{output_json}'.")

if __name__ == "__main__":

    INPUT_FILE = os.path.join(BASE_DIR, "extracted_scripts_txt", "script_text_en.ctd.txt")
    OUTPUT_FILE = "dialogues_es.json"

    clean_and_extract_to_json(INPUT_FILE, OUTPUT_FILE)