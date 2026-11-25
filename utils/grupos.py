"""Logica compartida de grupos: cuales toca publicar, registro y reparto entre ayudantes."""
import csv
import os
from datetime import datetime, timedelta

DIRECTORIO_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETA_DATA = os.path.join(DIRECTORIO_BASE, "data")
RUTA_CSV = os.path.join(CARPETA_DATA, "grupos.csv")
RUTA_SPINTAX = os.path.join(CARPETA_DATA, "spintax.txt")
RUTA_HISTORIAL = os.path.join(CARPETA_DATA, "historial.csv")
RUTA_AYUDANTE = os.path.join(CARPETA_DATA, "ayudante.txt")
CARPETA_MEDIA = os.path.join(DIRECTORIO_BASE, "media")
RUTA_IMAGEN = os.path.join(CARPETA_MEDIA, "promo.jpg")  # imagen por defecto

CAMPOS = ["nombre", "url", "tipo", "ultima_publicacion"]
HORAS_ENTRE_PUBLICACIONES = 48   # un mismo grupo no se repite antes de este tiempo
MAX_POR_DIA = 3                  # maximo recomendado de grupos por persona al dia


def leer_ayudante():
    """Devuelve (n, m) si data/ayudante.txt dice por ejemplo '2/4'; si no existe, None."""
    try:
        with open(RUTA_AYUDANTE, encoding="utf-8-sig") as f:
            n, m = f.read().strip().split("/")
        n, m = int(n), int(m)
        if 1 <= n <= m:
            return n, m
    except Exception:
        pass
    return None


def _le_toca(posicion, ayudante):
    """Reparte los grupos por turnos segun su lugar en la lista (1,2,3,4,1,2,3,4...).
    Si agregas grupos nuevos AL FINAL de grupos.csv, el reparto de los anteriores no cambia."""
    if ayudante is None:
        return True
    n, m = ayudante
    return posicion % m == n - 1


def leer_grupos_disponibles():
    """Grupos de esta persona donde no se ha publicado en las ultimas 48 horas."""
    disponibles = []
    if not os.path.exists(RUTA_CSV):
        print(f"[!] No se encontro el archivo de grupos en: {RUTA_CSV}")
        return disponibles

    ayudante = leer_ayudante()
    ahora = datetime.now()
    with open(RUTA_CSV, mode="r", encoding="utf-8-sig", newline="") as f:
        for posicion, row in enumerate(csv.DictReader(f)):
            if not _le_toca(posicion, ayudante):
                continue
            try:
                ultima = datetime.strptime(row["ultima_publicacion"], "%Y-%m-%d %H:%M:%S")
            except Exception:
                ultima = datetime(2000, 1, 1)
            if ahora - ultima >= timedelta(hours=HORAS_ENTRE_PUBLICACIONES):
                disponibles.append(row)
    return disponibles


def actualizar_fecha_grupo(url_objetivo):
    filas = []
    with open(RUTA_CSV, mode="r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if row["url"] == url_objetivo:
                row["ultima_publicacion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            filas.append(row)
    with open(RUTA_CSV, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS)
        writer.writeheader()
        writer.writerows(filas)


def publicaciones_hoy():
    """Cuantas publicaciones registro esta computadora hoy."""
    if not os.path.exists(RUTA_HISTORIAL):
        return 0
    hoy = datetime.now().strftime("%Y-%m-%d")
    with open(RUTA_HISTORIAL, encoding="utf-8-sig", newline="") as f:
        return sum(1 for fila in csv.DictReader(f) if fila.get("fecha_hora", "").startswith(hoy))


def registrar_publicacion(grupo, imagen):
    """Guarda una linea en data/historial.csv para saber que se publico, cuando y con que imagen."""
    existe = os.path.exists(RUTA_HISTORIAL)
    ayudante = leer_ayudante()
    with open(RUTA_HISTORIAL, mode="a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not existe:
            w.writerow(["fecha_hora", "persona", "grupo", "url", "imagen"])
        w.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            f"{ayudante[0]}/{ayudante[1]}" if ayudante else "todos",
            grupo["nombre"],
            grupo["url"],
            os.path.basename(imagen),
        ])
