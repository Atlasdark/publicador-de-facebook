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

    Extrae con precisión la última imagen asignada del bloque y limpia el texto.
    """
    bloques = _leer_bloques(ruta_txt)
    bloque = random.choice(bloques)
    imagen = imagen_defecto
    
    # Buscar todas las imágenes declaradas en este bloque específico
    matches = _PATRON_IMAGEN.findall(bloque)
    if matches:
        # Tomar la última imagen válida encontrada en el bloque
        nombre_img = matches[-1].strip()
        candidata = os.path.join(carpeta_media, nombre_img)
        
        if os.path.exists(candidata):
            imagen = candidata
        else:
            print(f"[!] Advertencia: La imagen '{nombre_img}' no se encontró en media.")
            archivos = [os.path.join(carpeta_media, f) for f in os.listdir(carpeta_media) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
            if archivos:
                imagen = archivos[0]
        
        # ELIMINAR TODAS las líneas @imagen: del bloque para que no salgan en Facebook
        bloque = _PATRON_IMAGEN.sub("", bloque)
    else:
        if not os.path.exists(imagen):
            archivos = [os.path.join(carpeta_media, f) for f in os.listdir(carpeta_media) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
            if archivos:
                imagen = archivos[0]
                
    # Resolver spintax y limpiar espacios sobrantes
    texto_limpio = _resolver_spintax(bloque).strip()
    return texto_limpio, imagen


def procesar_spintax(ruta_txt):
    """Compatibilidad: devuelve solo el texto de un anuncio al azar sin etiquetas."""
    bloque = random.choice(_leer_bloques(ruta_txt))
    bloque = _PATRON_IMAGEN.sub("", bloque).strip()
    return _resolver_spintax(bloque)


def mutar_imagen(ruta_imagen, carpeta_temp):
    """Copia el flyer a una carpeta temporal con nombre unico y devuelve la ruta."""
    os.makedirs(carpeta_temp, exist_ok=True)
    _, ext = os.path.splitext(ruta_imagen)
    destino = os.path.join(carpeta_temp, f"flyer_{int(time.time())}{ext}")
    shutil.copy2(ruta_imagen, destino)
    return destino