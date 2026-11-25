"""Crea PowerGym_Ayudante.zip para mandar a los ayudantes.
Solo incluye lo necesario. NO incluye sesiones de Facebook, historial ni archivos privados.
Ejecutar desde la carpeta del proyecto:  python empaquetar.py"""
import glob
import os
import zipfile

BASE = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(BASE, "PowerGym_Ayudante.zip")

ARCHIVOS = [
    "asistente.py",
    "requirements.txt",
    "instalar.bat",
    "Publicar Power Gym.bat",
    "LEEME.txt",
    "power_gym.ico",
    "utils/__init__.py",
    "utils/preparador.py",
    "utils/grupos.py",
    "data/grupos.csv",
    "data/spintax.txt",
]


def main():
    faltan = [a for a in ARCHIVOS if not os.path.exists(os.path.join(BASE, a))]
    if faltan:
        print("[!] No encuentro estos archivos (se omiten):", ", ".join(faltan))
    imagenes = sorted(glob.glob(os.path.join(BASE, "media", "*.jpg")))
    with zipfile.ZipFile(SALIDA, "w", zipfile.ZIP_DEFLATED) as z:
        for a in ARCHIVOS:
            ruta = os.path.join(BASE, a)
            if os.path.exists(ruta):
                z.write(ruta, "PowerGym/" + a.replace("\\", "/"))
        for img in imagenes:
            z.write(img, "PowerGym/media/" + os.path.basename(img))
    print(f"[OK] Creado: {SALIDA}")
    print(f"     {len(imagenes)} imagen(es) incluida(s). Mandalo por WhatsApp, Drive o correo.")


if __name__ == "__main__":
    main()
