import tkinter as tk
from tkinter import filedialog, messagebox

class SimpleTextEditor:
    def __init__ (self,root):
        self.root = root
        self.text_area = tk.Text(self.root)
        self.text_area.pack(fill=tk.BOTH, expand=1)
        self.current_open_file = ''

    def new_file(self):
         if messagebox.askokcancel("Nuevo", "¿Estas seguro de que quieres crear un nuevo archivo? Podrías perder los datos no guardados"):
            self.text_area.delete("1.0", tk.END)
    def save_file(self):
        if not self.current_open_file:
            filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Archivos de texto", "*.txt")])
            if filename:
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(self.text_area.get("1.0", tk.END))
                    self.current_open_file = filename
        else:
            with open(self.current_open_file, 'w', encoding='utf-8') as file:
                file.write(self.text_area.get("1.0", tk.END))

    def open_file(self):
        filename = filedialog.askopenfilename()

        if filename:
            self.text_area.delete("1.0", tk.END)
            encodings = ['utf-8', 'latin1', 'iso-8859-1']  # Lista de codificaciones a intentar
            successful = False
            for encoding in encodings:
                try:
                    with open(filename, 'r', encoding=encoding) as file:
                        self.text_area.insert("1.0", file.read())
                    successful = True
                    break
                except UnicodeDecodeError:
                    continue
            
            if not successful:
                messagebox.showerror("Error", "No se puede abrir el archivo con ninguna codificación compatible.")
            else:
                self.current_open_file = filename

    def quit_confirm (self):
        if messagebox.askokcancel("Salir", "¿Estas seguro de que quieres salir?"):
            self.root.destroy()


root = tk.Tk()
root.title("Gestor de archivos")
root.geometry("700x500")

editor = SimpleTextEditor(root)

menu_bar = tk.Menu(root)
menu_opciones = tk.Menu(menu_bar, tearoff=0)


menu_opciones.add_command(label="Nuevo", command=editor.new_file)
menu_opciones.add_command(label="Abrir", command=editor.open_file)
menu_opciones.add_command(label="Guardar",command= editor.save_file)
menu_opciones.add_command(label="Cerrar", command=editor.quit_confirm)

root.config(menu=menu_bar)
menu_bar.add_cascade(label="Archivo", menu= menu_opciones)

root.mainloop()