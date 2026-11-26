"""Utilidades para main.py: elegir anuncio (con su imagen), resolver spintax y copiar el flyer."""
import os
import random
import re
import shutil
import time

_PATRON_SPINTAX = re.compile(r"\{([^{}]*)\}")
_PATRON_PENDIENTE = re.compile(r"<<[^<>]+>>")
_SEPARADOR = re.compile(r"^\s*={3,}\s*$", re.MULTILINE)
_PATRON_IMAGEN = re.compile(r"^\s*@imagen:\s*(.+?)\s*$", re.MULTILINE)


def _resolver_spintax(texto):
    """Resuelve {a|b|c}, incluso anidado."""
    while True:
        nuevo = _PATRON_SPINTAX.sub(lambda m: random.choice(m.group(1).split("|")), texto)
        if nuevo == texto:
            return texto
        texto = nuevo


def _leer_texto(ruta):
    """Lee el archivo aunque este guardado en UTF-8 o en la codificacion de Windows (cp850)."""
    with open(ruta, "rb") as f:
        datos = f.read()
    try:
        return datos.decode("utf-8-sig")
    except UnicodeDecodeError:
        return datos.decode("cp850")


def _leer_bloques(ruta_txt):
    lineas = [l for l in _leer_texto(ruta_txt).splitlines() if not l.startswith("##")]
    bloques = [b.strip() for b in _SEPARADOR.split("\n".join(lineas)) if b.strip()]
    if not bloques:
        raise ValueError(f"No hay anuncios en {ruta_txt}")
    pendientes = sorted({p for b in bloques for p in _PATRON_PENDIENTE.findall(b)})
    if pendientes:
        raise ValueError("Faltan datos por llenar en los anuncios: " + ", ".join(pendientes))
    return bloques


def elegir_anuncio(ruta_txt, carpeta_media, imagen_defecto):
    """Elige UN anuncio al azar y devuelve (texto_final, ruta_de_su_imagen).

    La linea '@imagen: nombre.jpg' dentro del anuncio indica su flyer en carpeta_media.
    Si no la tiene, o el archivo no existe, usa imagen_defecto.
    """
    bloque = random.choice(_leer_bloques(ruta_txt))
    imagen = imagen_defecto
    m = _PATRON_IMAGEN.search(bloque)
    if m:
        candidata = os.path.join(carpeta_media, m.group(1))
        if os.path.exists(candidata):
            imagen = candidata
        else:
            print(f"[!] No existe la imagen {candidata}; uso {imagen_defecto}")
        bloque = _PATRON_IMAGEN.sub("", bloque, count=1).strip()
    return _resolver_spintax(bloque), imagen


def procesar_spintax(ruta_txt):
    """Compatibilidad: devuelve solo el texto de un anuncio al azar."""
    bloque = random.choice(_leer_bloques(ruta_txt))
    bloque = _PATRON_IMAGEN.sub("", bloque, count=1).strip()
    return _resolver_spintax(bloque)


def mutar_imagen(ruta_imagen, carpeta_temp):
    """Copia el flyer a una carpeta temporal con nombre unico y devuelve la ruta.

    main.py borra este archivo al terminar, asi el original nunca se toca.
    """
    os.makedirs(carpeta_temp, exist_ok=True)
    _, ext = os.path.splitext(ruta_imagen)
    destino = os.path.join(carpeta_temp, f"flyer_{int(time.time())}{ext}")
    shutil.copy2(ruta_imagen, destino)
    return destino
