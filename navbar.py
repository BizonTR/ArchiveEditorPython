import tkinter as tk

class Navbar:
    def __init__(self, parent, on_archive_editor_click):
        self.frame = tk.Frame(parent, bg="lightgray")
        self.create_widgets(on_archive_editor_click)

    def create_widgets(self, on_archive_editor_click):
        self.archive_editor_button = tk.Button(self.frame, text="Archive Editor", command=on_archive_editor_click)
        self.archive_editor_button.pack(side=tk.LEFT, padx=10, pady=5)

        # Daha fazla buton ve dropdown menüleri buraya ekleyebilirsiniz
        # Örnek bir dropdown menüsü
        self.menu_button = tk.Menubutton(self.frame, text="Menu", relief=tk.RAISED)
        self.menu = tk.Menu(self.menu_button, tearoff=0)
        self.menu.add_command(label="Option 1")
        self.menu.add_command(label="Option 2")
        self.menu_button.config(menu=self.menu)
        self.menu_button.pack(side=tk.LEFT, padx=10, pady=5)

    def pack(self, **kwargs):
        self.frame.pack(fill=tk.X, **kwargs)
