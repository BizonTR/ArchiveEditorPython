import tkinter as tk
from navbar import Navbar
from ui import ArchiveApp

class UIGeneral:
    def __init__(self, root):
        self.root = root
        self.root.title("General UI")
        self.create_widgets()

    def create_widgets(self):
        self.navbar = Navbar(self.root, self.open_archive_editor)
        self.navbar.pack(pady=10)

    def open_archive_editor(self):
        # Varolan pencereyi temizleyin
        for widget in self.root.winfo_children():
            widget.destroy()

        # Navbar'ı tekrar ekleyin
        self.navbar = Navbar(self.root, self.open_archive_editor)
        self.navbar.pack(pady=10)

        # ArchiveManagerApp'i varolan pencerede başlatın
        app = ArchiveApp(self.root)