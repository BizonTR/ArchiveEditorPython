import tkinter as tk
from navbar import Navbar
from ui import ArchiveApp
from cloneFileUi import CloneFileFinderUI

class UIGeneral:
    def __init__(self, root):
        self.root = root
        self.root.title("General UI")
        self.create_widgets()

    def create_widgets(self):
        self.navbar = Navbar(self.root, self.open_archive_editor, self.open_clone_scanner, self.open_homepage)
        self.navbar.pack(pady=10)

    def open_homepage(self):
        # Varolan pencereyi temizleyin
        for widget in self.root.winfo_children():
            widget.destroy()

        app = UIGeneral(self.root)

    def open_archive_editor(self):
        # Varolan pencereyi temizleyin
        for widget in self.root.winfo_children():
            widget.destroy()

        # Navbar'ı tekrar ekleyin
        self.navbar = Navbar(self.root, self.open_archive_editor, self.open_clone_scanner, self.open_homepage)
        self.navbar.pack(pady=10)

        # ArchiveManagerApp'i varolan pencerede başlatın
        app = ArchiveApp(self.root)

    def open_clone_scanner(self):
        # Varolan pencereyi temizleyin
        for widget in self.root.winfo_children():
            widget.destroy()

        # Navbar'ı tekrar ekleyin
        self.navbar = Navbar(self.root, self.open_archive_editor, self.open_clone_scanner, self.open_homepage)
        self.navbar.pack(pady=10)

        # CloneFileFinderUI'i varolan pencerede başlatın
        app = CloneFileFinderUI(self.root)