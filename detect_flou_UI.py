import os
import cv2
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
from tkinter import messagebox


def is_blurry(image_path, threshold=30):
    try:
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        return laplacian_var < threshold
    except:
        return False

def scan_folder(folder):
    blurry_images = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                path = os.path.join(root, file)
                if is_blurry(path):
                    blurry_images.append(path)
    return blurry_images

def delete_selected():
    for i, var in enumerate(checkbox_vars):
        if var.get():
            os.remove(image_paths[i])
    root.destroy()

# --- Interface Tkinter ---

folder = filedialog.askdirectory(title="Choisissez le dossier de photos à analyser")
if not folder:
    exit()

image_paths = scan_folder(folder)

root = Tk()
root.title("Photos floues détectées")

canvas = Canvas(root)
frame = Frame(canvas)
scrollbar = Scrollbar(root, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)
canvas.create_window((0, 0), window=frame, anchor='nw')

checkbox_vars = []

for idx, path in enumerate(image_paths):
    try:
        img = Image.open(path)
        img.thumbnail((200, 200))
        tk_img = ImageTk.PhotoImage(img)

        # — Fonction qui s'exécute quand on clique sur la miniature —
        def open_full_image(img_path=path):
            top = Toplevel(root)
            top.title(os.path.basename(img_path))
            img_large = Image.open(img_path)
            img_large.thumbnail((1000, 1000))  # Pour éviter que ça dépasse l’écran
            tk_large = ImageTk.PhotoImage(img_large)
            lbl = Label(top, image=tk_large)
            lbl.image = tk_large  # important pour que l'image s'affiche
            lbl.pack()

        # — Miniature cliquable —
        panel = Label(frame, image=tk_img, cursor="hand2")
        panel.image = tk_img
        panel.grid(row=idx, column=0, padx=5, pady=5)
        panel.bind("<Button-1>", lambda e, p=path: open_full_image(p))

        # — Case à cocher —
        var = BooleanVar()
        chk = Checkbutton(frame, text=os.path.basename(path), variable=var)
        chk.grid(row=idx, column=1, sticky="w")
        checkbox_vars.append(var)

    except Exception as e:
        print(f"Erreur sur {path} : {e}")
        continue

# — Bouton pour supprimer les images sélectionnées —
btn = Button(root, text="🗑️ Supprimer les sélectionnées", command=delete_selected, bg="#e5f2ff", fg="black", activebackground="#cce5ff")
btn.pack(pady=10)


# — Bouton pour supprimer toutes les images floues —
def delete_all():
    confirm = messagebox.askyesno("Confirmation", "Êtes-vous sûr(e) de vouloir TOUT supprimer ?")
    if confirm:
        for path in image_paths:
            try:
                os.remove(path)
            except Exception as e:
                print(f"Erreur en supprimant {path} : {e}")
        root.destroy()

btn_all = Button(root, text="🔥 Tout supprimer", command=delete_all, bg="#ffe5e5", fg="black", activebackground="#ffcccc")
btn_all.pack(pady=5)

# Ajuster la taille de la fenêtre
frame.update_idletasks()
canvas.config(scrollregion=canvas.bbox("all"))

root.mainloop()