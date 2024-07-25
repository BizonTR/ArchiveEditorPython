import tkinter as tk

class Navbar:
    def __init__(self, parent, on_archive_editor_click, on_clone_scanner_click, on_homepage_click):
        self.frame = tk.Frame(parent, bg="lightgray")
        self.create_widgets(on_archive_editor_click, on_clone_scanner_click, on_homepage_click)

    def create_widgets(self, on_archive_editor_click, on_clone_scanner_click, on_homepage_click):
        self.clone_scanner_button = tk.Button(self.frame, text="Home Page", command=on_homepage_click)
        self.clone_scanner_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.archive_editor_button = tk.Button(self.frame, text="Archive Editor", command=on_archive_editor_click)
        self.archive_editor_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.clone_scanner_button = tk.Button(self.frame, text="Clone Scanner", command=on_clone_scanner_click)
        self.clone_scanner_button.pack(side=tk.LEFT, padx=10, pady=5)
        
    def pack(self, **kwargs):
        self.frame.pack(fill=tk.X, **kwargs)