"""Asistente semi-manual: prepara anuncio + imagen y abre el grupo en TU navegador normal.
Tu solo pegas (Ctrl+V dos veces) y haces clic en Publicar."""
import os
import random
import subprocess
import tempfile
import time
import webbrowser

from utils.grupos import (
    CARPETA_MEDIA,
    MAX_POR_DIA,
    RUTA_IMAGEN,
    RUTA_SPINTAX,
    actualizar_fecha_grupo,
    leer_ayudante,
    leer_grupos_disponibles,
    publicaciones_hoy,
    registrar_publicacion,
)
from utils.preparador import elegir_anuncio

try:
    import keyboard  # pip install keyboard
except ImportError:
    keyboard = None

def _powershell(comando):
    subprocess.run(["powershell", "-NoProfile", "-STA", "-Command", comando], check=True)


# ---- Portapapeles rapido (ctypes). Si algo falla, se usa PowerShell como respaldo ----
CF_DIB = 8
CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002


def _poner_en_portapapeles(formato, datos):
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    kernel32.GlobalAlloc.restype = ctypes.c_void_p
    kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    user32.OpenClipboard.argtypes = [wintypes.HWND]
    user32.SetClipboardData.argtypes = [wintypes.UINT, ctypes.c_void_p]
    user32.SetClipboardData.restype = ctypes.c_void_p

    h = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(datos))
    p = kernel32.GlobalLock(h)
    ctypes.memmove(p, datos, len(datos))
    kernel32.GlobalUnlock(h)

    for _ in range(40):
        if user32.OpenClipboard(None):
            break
        time.sleep(0.05)
    else:
        raise RuntimeError("No pude abrir el portapapeles")
    try:
        user32.EmptyClipboard()
        if not user32.SetClipboardData(formato, h):
            raise RuntimeError("SetClipboardData fallo")
    finally:
        user32.CloseClipboard()


def _imagen_a_dib(ruta):
    """Convierte una imagen (jpg/png) a formato DIB para el portapapeles. Requiere Pillow."""
    import io
    from PIL import Image

    with Image.open(ruta) as im:
        buf = io.BytesIO()
        im.convert("RGB").save(buf, "BMP")
    return buf.getvalue()[14:]  # quita el encabezado de archivo BMP (14 bytes)


def copiar_texto(texto):
    try:
        datos = (texto.replace("\r\n", "\n").replace("\n", "\r\n") + "\0").encode("utf-16-le")
        _poner_en_portapapeles(CF_UNICODETEXT, datos)
        return
    except Exception:
        pass
    with tempfile.NamedTemporaryFile(
        "w", suffix=".txt", delete=False, encoding="utf-8", newline=""
    ) as f:
        f.write(texto)
        ruta = f.name
    try:
        _powershell(f"Get-Content -Raw -Encoding UTF8 -LiteralPath '{ruta}' | Set-Clipboard")
    finally:
        os.remove(ruta)


def copiar_imagen(ruta):
    try:
        _poner_en_portapapeles(CF_DIB, _imagen_a_dib(ruta))
        return
    except Exception:
        pass
    ruta = os.path.abspath(ruta).replace("'", "''")
    _powershell(
        "Add-Type -AssemblyName System.Windows.Forms; "
        "Add-Type -AssemblyName System.Drawing; "
        f"$img = [System.Drawing.Image]::FromFile('{ruta}'); "
        "$d = New-Object System.Windows.Forms.DataObject; "
        "$d.SetImage($img); "
        "[System.Windows.Forms.Clipboard]::SetDataObject($d, $true)"
    )


def _pegar_con_atajos(texto, imagen):
    """Ctrl+V #1 pega el texto; el programa cambia el portapapeles a la imagen; Ctrl+V #2 la pega."""
    estado = {"pegados": 0}

    def al_pegar():
        estado["pegados"] += 1
        if estado["pegados"] == 1:
            time.sleep(0.5)  # deja terminar el pegado del texto
            try:
                copiar_imagen(imagen)
                print("   [OK] Imagen lista: pega con Ctrl+V otra vez.")
            except Exception as e:
                print(f"   [!] No pude copiar la imagen: {e}")

    def recopiar_texto():
        estado["pegados"] = 0
        copiar_texto(texto)
        print("   [OK] Texto copiado de nuevo (F8).")

    def recopiar_imagen():
        estado["pegados"] = 2
        copiar_imagen(imagen)
        print("   [OK] Imagen copiada de nuevo (F9).")

    h1 = keyboard.add_hotkey("ctrl+v", al_pegar)
    h2 = keyboard.add_hotkey("f8", recopiar_texto)
    h3 = keyboard.add_hotkey("f9", recopiar_imagen)
    return (h1, h2, h3)


def ciclo():
    ayudante = leer_ayudante()
    if ayudante:
        print(f"[i] Persona {ayudante[0]} de {ayudante[1]}: solo veras los grupos que te tocan.")

    restantes = MAX_POR_DIA - publicaciones_hoy()
    if restantes <= 0:
        print(f"[*] Ya publicaste en {MAX_POR_DIA} grupos hoy (el maximo recomendado). Vuelve manana.")
        return

    grupos = leer_grupos_disponibles()
    if not grupos:
        print("[!] No hay grupos disponibles hoy (todos usados en las ultimas 48 horas).")
        return
    random.shuffle(grupos)

    if keyboard is None:
        print("[i] Sin la libreria 'keyboard': usare ENTER para pasar de texto a imagen.")
        print("    Para el modo Ctrl+V doble instala:  pip install keyboard\n")

    hechos = 0
    for grupo in grupos:
        if hechos >= restantes:
            print(f"[*] Llegaste al maximo recomendado de {MAX_POR_DIA} grupos por dia.")
            break

        texto, imagen = elegir_anuncio(RUTA_SPINTAX, CARPETA_MEDIA, RUTA_IMAGEN)
        print("\n" + "=" * 60)
        print(f"GRUPO: {grupo['nombre']}")
        print(f"IMAGEN: {os.path.basename(imagen)}")
        print("=" * 60)

        copiar_texto(texto)
        webbrowser.open(grupo["url"])
        print("1. Se abrio el grupo. Asegurate de estar como PAGINA Power Gym.")
        print("2. Abre 'Escribe algo...', haz clic dentro del cuadro de texto.")

        hooks = ()
        if keyboard is not None:
            print("3. Ctrl+V  -> pega el TEXTO.")
            print("4. Espera 1 segundo y Ctrl+V otra vez -> pega la IMAGEN.")
            print("   (F8 = copiar el texto de nuevo, F9 = copiar la imagen de nuevo)")
            hooks = _pegar_con_atajos(texto, imagen)
        else:
            print("3. Ctrl+V para pegar el texto.")
            input("4. Cuando el texto este pegado, presiona ENTER aqui para copiar la imagen... ")
            copiar_imagen(imagen)
            print(f"   [OK] Imagen copiada. Pegala con Ctrl+V. Si no se adjunta, usa Foto/video: {imagen}")

        print("5. Revisa texto e imagen y haz clic en 'Publicar'.")
        try:
            r = input("\nYa publicaste? (s = si / n = omitir este grupo / q = salir): ").strip().lower()
        finally:
            for h in hooks:
                try:
                    keyboard.remove_hotkey(h)
                except Exception:
                    pass

        if r == "q":
            break
        if r == "s":
            actualizar_fecha_grupo(grupo["url"])
            registrar_publicacion(grupo, imagen)
            hechos += 1
            print("[OK] Grupo marcado. No se vuelve a usar por 48 horas.")
            if hechos < restantes:
                if input("Seguir con otro grupo? (s/n): ").strip().lower() != "s":
                    break

    print("\n[*] Listo.")


if __name__ == "__main__":
    ciclo()
