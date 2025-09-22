import json
import bibtexparser


def bib_to_obj(bib_path: str) -> list[dict]:
    """
    Convierte un archivo .bib en una lista de diccionarios.

    Args:
        bib_path (str): Ruta al archivo .bib

    Returns:
        list[dict]: Lista de referencias
    """
    with open(bib_path, encoding="utf-8") as bibfile:
        bib_database = bibtexparser.load(bibfile)

    # `entries` es una lista de diccionarios con las referencias
    return bib_database.entries

def bib_to_json(bib_path: str, json_path: str = None) -> str:
    """
    Convierte un archivo .bib en un string JSON.
    Si se pasa `json_path`, también lo guarda en disco.

    Args:
        bib_path (str): Ruta al archivo .bib
        json_path (str, optional): Ruta para guardar el JSON. Si es None, no se guarda.

    Returns:
        str: Contenido en formato JSON
    """
    with open(bib_path, encoding="utf-8") as bibfile:
        bib_database = bibtexparser.load(bibfile)

    # `entries` es una lista de diccionarios con las referencias
    json_str = json.dumps(bib_database.entries, indent=2, ensure_ascii=False)

    if json_path:
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(json_str)

    return json_str