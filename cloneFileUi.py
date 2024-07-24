import tkinter as tk
from tkinter import ttk, filedialog
import hashlib
import os

class CloneFileFinderUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Clone File Finder")
        self.geometry("800x600")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        # Add Tabs
        self.scan_tab = ttk.Frame(self.notebook)
        self.clone_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.scan_tab, text="Scan Archives")
        self.notebook.add(self.clone_tab, text="Find Clones")

        # Treeview for clone files
        self.clone_tree = ttk.Treeview(self.clone_tab, columns=("File Path", "Size"), show="headings")
        self.clone_tree.heading("File Path", text="File Path")
        self.clone_tree.heading("Size", text="Size (Bytes)")
        self.clone_tree.pack(expand=True, fill="both")

        # Button to select folders and find clones
        self.select_folder_button = tk.Button(self.clone_tab, text="Select Folder", command=self.select_folder)
        self.select_folder_button.pack()

        self.find_clones_button = tk.Button(self.clone_tab, text="Find Clones", command=self.find_clones)
        self.find_clones_button.pack()

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        print(f"Selected folder: {self.folder_path}")

    def find_clones(self):
        if not hasattr(self, 'folder_path'):
            print("Please select a folder first.")
            return
        
        file_hashes = {}
        for root, dirs, files in os.walk(self.folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_hash = self.hash_file(file_path)
                
                if file_hash in file_hashes:
                    file_hashes[file_hash].append(file_path)
                else:
                    file_hashes[file_hash] = [file_path]

        for file_paths in file_hashes.values():
            if len(file_paths) > 1:
                for file_path in file_paths:
                    file_size = os.path.getsize(file_path)
                    self.clone_tree.insert("", "end", values=(file_path, file_size))

    @staticmethod
    def hash_file(file_path):
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()

if __name__ == "__main__":
    app = CloneFileFinderUI()
    app.mainloop()
