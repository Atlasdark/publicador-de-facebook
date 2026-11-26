"""Construye data/grupos.csv a partir de una lista de enlaces pegada a mano.

Uso:
    1. Abre data/lista_grupos.txt (se crea sola la primera vez).
    2. Pega un grupo por linea:   https://www.facebook.com/groups/123456/
                              o:   Nombre del grupo | https://www.facebook.com/groups/123456/
    3. Ejecuta:  python agregar_grupos.py

Es seguro ejecutarlo varias veces: los grupos que ya estan en grupos.csv
conservan su fecha de ultima_publicacion; solo se agregan los nuevos.
"""
import csv
import os
import re

DIRECTORIO_BASE = os.path.dirname(os.path.abspath(__file__))
CARPETA_DATA = os.path.join(DIRECTORIO_BASE, "data")
RUTA_LISTA = os.path.join(CARPETA_DATA, "lista_grupos.txt")
RUTA_CSV = os.path.join(CARPETA_DATA, "grupos.csv")
CAMPOS = ["nombre", "url", "tipo", "ultima_publicacion"]
FECHA_INICIAL = "2000-01-01 00:00:00"

PLANTILLA = (
    "# Un grupo por linea. Formatos validos:\n"
    "#   https://www.facebook.com/groups/123456789/\n"
    "#   Nombre del grupo | https://www.facebook.com/groups/123456789/\n"
    "# Las lineas que empiezan con # se ignoran.\n"
)


def normalizar_url(url):
    """Quita parametros y deja la URL como https://www.facebook.com/groups/<id>/"""
    url = url.strip().split("?")[0].split("#")[0]
    m = re.search(r"facebook\.com/groups/([^/\s]+)", url)
    if not m:
        return None
    return f"https://www.facebook.com/groups/{m.group(1)}/"


def leer_lista():
    entradas = []
    with open(RUTA_LISTA, encoding="utf-8") as f:
        for n, linea in enumerate(f, start=1):
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            if "|" in linea:
                nombre, url_cruda = [x.strip() for x in linea.split("|", 1)]
            else:
                nombre, url_cruda = "", linea
            url = normalizar_url(url_cruda)
            if not url:
                print(f"[!] Linea {n} ignorada (no parece un grupo de Facebook): {linea}")
                continue
            if not nombre:
                nombre = "grupo-" + url.rstrip("/").split("/")[-1]
            entradas.append((nombre, url))
    return entradas


def leer_csv_actual():
    if not os.path.exists(RUTA_CSV):
        return {}
    with open(RUTA_CSV, encoding="utf-8", newline="") as f:
        return {fila["url"]: fila for fila in csv.DictReader(f)}


def main():
    os.makedirs(CARPETA_DATA, exist_ok=True)
    if not os.path.exists(RUTA_LISTA):
        with open(RUTA_LISTA, "w", encoding="utf-8") as f:
            f.write(PLANTILLA)
        print(f"[OK] Cree {RUTA_LISTA}. Pega tus grupos ahi y vuelve a ejecutar.")
        return

    existentes = leer_csv_actual()
    nuevos = 0
    for nombre, url in leer_lista():
        if url in existentes:
            continue
        existentes[url] = {
            "nombre": nombre,
            "url": url,
            "tipo": "normal",
            "ultima_publicacion": FECHA_INICIAL,
        }
        nuevos += 1

    with open(RUTA_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        w.writerows(existentes.values())

    print(f"[OK] {nuevos} grupo(s) nuevo(s). Total en CSV: {len(existentes)}")


if __name__ == "__main__":
    main()
