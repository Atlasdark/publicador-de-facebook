import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MEDIA_DIR = os.path.join(BASE_DIR, "media")
LISTA_GRUPOS = os.path.join(DATA_DIR, "lista_grupos.txt")
SPINTAX_FILE = os.path.join(DATA_DIR, "spintax.txt")

def pedir_texto_grande(root, numero_promo):
    """Abre una ventana amplia multilinea para pegar la promocion completa."""
    ventana = tk.Toplevel(root)
    ventana.title(f"Promoción #{numero_promo}")
    ventana.geometry("620x420")
    ventana.attributes("-topmost", True)
    ventana.grab_set()

    ventana.update_idletasks()
    x = (ventana.winfo_screenwidth() // 2) - (620 // 2)
    y = (ventana.winfo_screenheight() // 2) - (420 // 2)
    ventana.geometry(f"620x420+{x}+{y}")

    tk.Label(
        ventana,
        text=f"Pega o escribe tu PROMOCIÓN #{numero_promo}:",
        font=("Segoe UI", 11, "bold")
    ).pack(anchor="w", padx=15, pady=(15, 2))

    tk.Label(
        ventana,
        text="Puedes usar varios renglones, emojis y {opcion1|opcion2} para spintax.",
        font=("Segoe UI", 9),
        fg="#555555"
    ).pack(anchor="w", padx=15, pady=(0, 8))

    caja_texto = scrolledtext.ScrolledText(
        ventana,
        wrap=tk.WORD,
        font=("Segoe UI", 10),
        height=14
    )
    caja_texto.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
    caja_texto.focus_set()

    resultado = {"texto": None}

    def guardar():
        contenido = caja_texto.get("1.0", tk.END).strip()
        if not contenido:
            messagebox.showwarning("Campo vacío", "Escribe o pega el texto de la promoción antes de continuar.", parent=ventana)
            return
        resultado["texto"] = contenido
        ventana.destroy()

    def cancelar():
        ventana.destroy()

    frame_botones = tk.Frame(ventana)
    frame_botones.pack(fill=tk.X, padx=15, pady=12)

    tk.Button(
        frame_botones,
        text="Cancelar / Terminar",
        command=cancelar,
        font=("Segoe UI", 10),
        width=18
    ).pack(side=tk.LEFT)

    tk.Button(
        frame_botones,
        text="Guardar y elegir imagen →",
        command=guardar,
        bg="#2E7D32",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        width=24
    ).pack(side=tk.RIGHT)

    ventana.wait_window()
    return resultado["texto"]

def configurar():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(MEDIA_DIR, exist_ok=True)

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    # 1. PASO DE GRUPOS
    if messagebox.askyesno("Paso 1: Grupos de Facebook", "¿Quieres configurar o actualizar tu lista de grupos?"):
        messagebox.showinfo(
            "Bloc de Notas - Grupos",
            "Se abrirá el Bloc de notas.\n\nPega tus enlaces de grupos (uno por línea), guarda los cambios (Ctrl + G) y ciérralo para continuar."
        )
        if not os.path.exists(LISTA_GRUPOS):
            with open(LISTA_GRUPOS, "w", encoding="utf-8") as f:
                f.write("# Pega aqui tus grupos (un enlace por linea):\n")
        os.system(f'notepad "{LISTA_GRUPOS}"')

    # 2. PASO DE PROMOCIONES E IMÁGENES PASO A PASO
    if messagebox.askyesno("Paso 2: Promociones", "¿Quieres registrar tus promociones y sus imágenes una por una?"):
        reemplazar = messagebox.askyesno(
            "Modo de guardado",
            "¿Quieres BORRAR las promociones anteriores para empezar limpias?\n\n(Sí = Borrar anteriores / No = Agregar al final)"
        )
        modo = "w" if reemplazar else "a"

        contador = 1
        bloques_nuevos = []

        while True:
            texto = pedir_texto_grande(root, contador)
            if not texto:
                break

            archivos_media = [f for f in os.listdir(MEDIA_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
            nombre_imagen_final = ""

            if archivos_media:
                # Ventana con ambos botones: Usar existente o Subir nueva de PC
                top = tk.Toplevel(root)
                top.title(f"Selecciona imagen para Promo #{contador}")
                top.geometry("450x340")
                top.attributes("-topmost", True)
                top.grab_set()

                top.update_idletasks()
                x = (top.winfo_screenwidth() // 2) - (450 // 2)
                y = (top.winfo_screenheight() // 2) - (340 // 2)
                top.geometry(f"450x340+{x}+{y}")

                tk.Label(top, text=f"Elige una imagen existente para la Promo #{contador}:", font=("Segoe UI", 10, "bold")).pack(pady=10)

                lb = tk.Listbox(top, font=("Segoe UI", 10), selectmode=tk.SINGLE)
                for am in archivos_media:
                    lb.insert(tk.END, am)
                lb.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

                seleccion = {"val": None}

                def usar_existente():
                    idx = lb.curselection()
                    if idx:
                        seleccion["val"] = lb.get(idx)
                        top.destroy()
                    else:
                        messagebox.showwarning("Aviso", "Selecciona primero una imagen de la lista.", parent=top)

                def subir_nueva():
                    seleccion["val"] = "SUBIR_NUEVA"
                    top.destroy()

                frame_botones_img = tk.Frame(top)
                frame_botones_img.pack(fill=tk.X, padx=15, pady=12)

                tk.Button(
                    frame_botones_img,
                    text="📁 Subir nueva de PC",
                    command=subir_nueva,
                    bg="#1976D2",
                    fg="white",
                    font=("Segoe UI", 9, "bold")
                ).pack(side=tk.LEFT)

                tk.Button(
                    frame_botones_img,
                    text="Usar esta imagen",
                    command=usar_existente,
                    bg="#2E7D32",
                    fg="white",
                    font=("Segoe UI", 9, "bold")
                ).pack(side=tk.RIGHT)

                top.wait_window()
                nombre_imagen_final = seleccion["val"]

            # Si no hay archivos en media o si eligió explícitamente "Subir nueva de PC"
            if not nombre_imagen_final or nombre_imagen_final == "SUBIR_NUEVA":
                messagebox.showinfo(
                    f"Subir Imagen Nueva - Promo #{contador}",
                    f"Selecciona en tu computadora la imagen que irá ligada a la PROMOCIÓN #{contador}."
                )
                ruta_img = filedialog.askopenfilename(
                    title=f"Elige la imagen para la Promoción #{contador}",
                    filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.webp")]
                )
                if ruta_img:
                    nombre_destino = f"promo_{contador}_{os.path.basename(ruta_img).replace(' ', '_')}"
                    ruta_destino = os.path.join(MEDIA_DIR, nombre_destino)
                    shutil.copy2(ruta_img, ruta_destino)
                    nombre_imagen_final = nombre_destino

            linea_imagen = f"\n@imagen: {nombre_imagen_final}" if nombre_imagen_final else ""
            bloque = f"===\n{texto}\n{linea_imagen.lstrip()}\n===\n" if linea_imagen else f"===\n{texto}\n===\n"
            bloques_nuevos.append(bloque)

            if not messagebox.askyesno("Continuar", f"¡Promoción #{contador} guardada con éxito!\n\n¿Quieres registrar la PROMOCIÓN #{contador + 1}?"):
                break
            contador += 1

        if bloques_nuevos:
            with open(SPINTAX_FILE, modo, encoding="utf-8") as f:
                f.writelines(bloques_nuevos)

    messagebox.showinfo("Completado", "¡Tus grupos y promociones han quedado perfectamente guardados y vinculados!")

if __name__ == "__main__":
    configurar()