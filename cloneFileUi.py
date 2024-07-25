import tkinter as tk
from tkinter import ttk, filedialog
import os
import threading
import subprocess
from cloneFileScanner import CloneFileScanner

class CloneFileFinderUI:
    def __init__(self, root):
        self.root = root
        self.selected_folders = []  # Seçilen dizinleri saklamak için liste
        self.create_widgets()

    def create_widgets(self):
        # Split the root frame into two parts
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # Split the top frame into left and right parts
        self.top_left_frame = tk.Frame(self.top_frame, width=300)
        self.top_left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        self.top_right_frame = tk.Frame(self.top_frame)
        self.top_right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Add treeview for selected folders to the top left frame
        self.selected_folders_tree = ttk.Treeview(self.top_left_frame, columns=("Folder Path",), show="headings")
        self.selected_folders_tree.heading("#1", text="Folder Path")
        self.selected_folders_tree.bind("<Double-1>", self.open_folder)
        self.selected_folders_tree.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        # Add buttons to the top left frame
        self.button_frame = tk.Frame(self.top_left_frame)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.select_folder_button = tk.Button(self.button_frame, text="Select Folder", command=self.select_folder)
        self.select_folder_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.delete_folder_button = tk.Button(self.button_frame, text="Delete Selected Folder", command=self.delete_selected_folder)
        self.delete_folder_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.find_clones_button = tk.Button(self.button_frame, text="Scan Clones", command=self.start_scan_thread)
        self.find_clones_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Add textbox to log the scan results and errors to the top right frame
        self.log_text = tk.Text(self.top_right_frame, height=10)
        self.log_text.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        # Treeview for clone files in the bottom frame
        self.clone_tree = ttk.Treeview(self.bottom_frame, columns=("File Name", "File Path", "Creation Date", "Modification Date", "Size"), show="headings")
        self.clone_tree.heading("#1", text="File Name")
        self.clone_tree.heading("#2", text="File Path")
        self.clone_tree.heading("#3", text="Creation Date")
        self.clone_tree.heading("#4", text="Modification Date")
        self.clone_tree.heading("#5", text="Size (MB)")
        self.clone_tree.bind("<Double-1>", self.open_file)
        self.clone_tree.pack(expand=True, fill="both")

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.selected_folders.append(folder_path)
            self.selected_folders_tree.insert("", "end", values=(folder_path,))

    def delete_selected_folder(self):
        selected_item = self.selected_folders_tree.selection()
        if selected_item:
            folder_path = self.selected_folders_tree.item(selected_item, "values")[0]
            if folder_path in self.selected_folders:
                self.selected_folders.remove(folder_path)
            self.selected_folders_tree.delete(selected_item)
        else:
            self.log_text.insert(tk.END, "No folder selected for deletion.\n")
            self.log_text.see(tk.END)

    def start_scan_thread(self):
        if not self.selected_folders:
            self.log_text.insert(tk.END, "Please select folders first.\n")
            self.log_text.see(tk.END)
            return

        # Start a new thread for scanning files
        scan_thread = threading.Thread(target=self.find_clones)
        scan_thread.start()

    def find_clones(self):
        # Clear previous results
        for item in self.clone_tree.get_children():
            self.clone_tree.delete(item)

        # Scan each folder for clone files
        for folder in self.selected_folders:
            scanner = CloneFileScanner(folder, self.update_ui)
            clones = scanner.scan_files(self.update_progress)

            for clone in clones:
                self.clone_tree.insert("", "end", values=(
                    clone['file_name'],
                    clone['file_path'],
                    clone['creation_date'],
                    clone['modification_date'],
                    f"{clone['file_size']:.2f} MB"
                ))

    def update_ui(self, data):
        # Update the UI with the data received from the scanner
        if isinstance(data, dict):
            log_entry = f"Name: {data['file_name']}, Path: {data['file_path']}, Size: {data['file_size']}, Created: {data['creation_date']}, Modified: {data['modification_date']}\n"
            self.log_text.insert(tk.END, log_entry)
        else:
            self.log_text.insert(tk.END, data + "\n")
        self.log_text.see(tk.END)

    def update_progress(self, scanned_size_mb):
        # Optionally update a progress bar or similar UI element
        pass

    def open_folder(self, event):
        selected_item = self.selected_folders_tree.selection()
        if selected_item:
            folder_path = self.selected_folders_tree.item(selected_item, "values")[0]
            self.open_folder_path(folder_path)

    def open_file(self, event):
        selected_item = self.clone_tree.selection()
        if selected_item:
            item_values = self.clone_tree.item(selected_item)['values']
            file_path = item_values[1]  # "File Path" sütunundaki dosya yolunu al
            self.open_file_path(file_path)

    def open_folder_path(self, folder_path):
        # Konsola gitmek istenilen adresi yazdır
        print(f"Trying to open folder path: {folder_path}")

        # Dosyanın gerçekten var olup olmadığını kontrol et
        if os.path.exists(folder_path):
            try:
                if os.name == 'nt':  # Windows
                    subprocess.run(['explorer', folder_path.replace('/', '\\')], check=True)
                elif os.name == 'posix':  # MacOS/Linux
                    subprocess.run(['xdg-open', folder_path], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Failed to open folder: {e}")
        else:
            print(f"Path does not exist: {folder_path}")

    def open_file_path(self, file_path):
        # Konsola gitmek istenilen adresi yazdır
        print(f"Trying to open file path: {file_path}")

        # Dosyanın gerçekten var olup olmadığını kontrol et
        if os.path.exists(file_path):
            # Dosyanın bulunduğu dizini al
            folder_path = os.path.dirname(file_path)
            print(f"Opening folder containing file: {folder_path}")
            try:
                if os.name == 'nt':  # Windows
                    subprocess.run(['explorer', folder_path.replace('/', '\\')], check=True)
                elif os.name == 'posix':  # MacOS/Linux
                    subprocess.run(['xdg-open', folder_path], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Failed to open folder: {e}")
        else:
            print(f"Path does not exist: {file_path}")

