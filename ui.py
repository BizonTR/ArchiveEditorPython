import tkinter as tk
from tkinter import filedialog, scrolledtext, BooleanVar
from tkinter import ttk
import os
import subprocess
from fileScanner import FileScanner

class ArchiveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Arşiv Düzenleme Programı")

        self.directory_path = None
        self.keep_copied_files_var = BooleanVar()
        self.keep_copied_files_var.set(False)

        # Üst kısımda butonlar ve checkbox için bir frame oluştur
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(side=tk.TOP, pady=20, padx=20, fill=tk.BOTH, expand=True)

        self.search_button = tk.Button(self.top_frame, text="Arşiv Ara", command=self.search_archive)
        self.search_button.pack(pady=10)

        self.keep_copied_files_checkbox = tk.Checkbutton(self.top_frame, text="Klon dosya varsa ismini değiştirerek sakla",
                                                         variable=self.keep_copied_files_var)
        self.keep_copied_files_checkbox.pack()

        self.scan_button = tk.Button(self.top_frame, text="Tarama Başlat", command=self.start_scan, state=tk.DISABLED)
        self.scan_button.pack(pady=10)

        # Dosya bilgilerini gösterecek Treeview widget'ı için bir frame oluştur
        self.middle_frame = tk.Frame(root)
        self.middle_frame.pack(side=tk.TOP, pady=20, padx=20, fill=tk.BOTH, expand=True)

        # Treeview widget'ı oluştur ve sütunları ayarla
        self.tree = ttk.Treeview(self.middle_frame, columns=("Dosya Adı", "Dosya Yolu", "Yeni Yer", "Oluşturma Tarihi", "Değiştirme Tarihi", "Tür", "Boyut"), show='headings')
        self.tree.heading("Dosya Adı", text="Dosya Adı")
        self.tree.heading("Dosya Yolu", text="Dosya Yolu")
        self.tree.heading("Yeni Yer", text="Yeni Yer")
        self.tree.heading("Oluşturma Tarihi", text="Oluşturma Tarihi")
        self.tree.heading("Değiştirme Tarihi", text="Değiştirme Tarihi")
        self.tree.heading("Tür", text="Tür")
        self.tree.heading("Boyut", text="Boyut")

        # Sütun genişliklerini ayarla
        self.tree.column("Dosya Adı", minwidth=100, width=150, stretch=tk.NO)
        self.tree.column("Dosya Yolu", minwidth=300, width=500, stretch=tk.NO)
        self.tree.column("Yeni Yer", minwidth=400, width=600, stretch=tk.NO)
        self.tree.column("Oluşturma Tarihi", minwidth=100, width=120, stretch=tk.NO)
        self.tree.column("Değiştirme Tarihi", minwidth=100, width=120, stretch=tk.NO)
        self.tree.column("Tür", minwidth=50, width=70, stretch=tk.NO)
        self.tree.column("Boyut", minwidth=50, width=70, stretch=tk.NO)

        # Scrollbar oluştur ve Treeview'e bağla
        self.tree_scroll = ttk.Scrollbar(self.middle_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scroll.set)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.horiz_scroll = ttk.Scrollbar(self.middle_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=self.horiz_scroll.set)
        self.horiz_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Dosya bilgilerini gösterecek scrolledtext (scrollbar'lı metin kutusu) için bir frame oluştur
        self.bottom_frame = tk.Frame(root)
        self.bottom_frame.pack(side=tk.BOTTOM, pady=20, padx=20, fill=tk.BOTH, expand=True)

        self.textbox = scrolledtext.ScrolledText(self.bottom_frame, height=10, wrap=tk.NONE)
        self.textbox.pack(fill=tk.BOTH, expand=True)

        # Yatay scrollbar oluştur ve textbox'a bağla
        self.textbox_scroll = ttk.Scrollbar(self.bottom_frame, orient="horizontal", command=self.textbox.xview)
        self.textbox.configure(xscrollcommand=self.textbox_scroll.set)
        self.textbox_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        # Treeview'e çift tıklama olayı ekle
        self.tree.bind("<Double-1>", self.open_file_explorer)

    def write_message(self, message):
        if isinstance(message, dict):
            item_id = self.tree.insert("", tk.END, values=(
                message['file_name'],
                message['file_path'],
                message['new_file_path'],
                message['creation_date'],
                message['modification_date'],
                message['file_type'],
                message['file_size'],
            ))
            self.tree.see(item_id)  # Son eklenen satıra kaydır
        else:
            self.textbox.insert(tk.END, f"{message}\n")
            self.textbox.see(tk.END)  # Metin kutusunu en son yazılan satıra kaydır
        self.root.update_idletasks()  # Arayüzü güncelle

    def open_file_explorer(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item_values = self.tree.item(selected_item)['values']
            new_file_path = item_values[2]  # "Yeni Yer" sütunundaki dosya yolunu al
            new_file_path = new_file_path.replace('/', '\\')  # Ters eğik çizgiye dönüştür
            folder_path = os.path.dirname(new_file_path)  # Klasör yolunu al
            #print(f"Gidilecek dosya yolu: {folder_path}")
            
            # Dosya gezgini aç
            if os.path.exists(folder_path):
                if os.name == 'nt':  # Windows
                    subprocess.Popen(f'explorer "{folder_path}"')
                elif os.name == 'posix':  # MacOS/Linux
                    subprocess.Popen(['open', folder_path])

    def search_archive(self):
        self.directory_path = filedialog.askdirectory()
        if self.directory_path:
            self.write_message(f"Seçilen klasör yolu: {self.directory_path}")
            self.scan_button.config(state=tk.NORMAL)
        else:
            self.write_message("Klasör seçilmedi!")
            self.scan_button.config(state=tk.DISABLED)

    def start_scan(self):
        if self.directory_path:
            self.write_message("Tarama başlatıldı...")
            self.scan_button.config(state=tk.DISABLED)

            scanner = FileScanner(self.directory_path, callback=self.write_message, keep_copied_files=self.keep_copied_files_var.get())
            results = scanner.scan_files()

            self.write_message("Boş kalan klasörler siliniyor...")
            deleted_folders, errors = scanner.remove_empty_directories(self.directory_path)

            if errors:
                self.write_message("Silinemeyen klasörler:")
                for error in errors:
                    self.write_message(error)

            self.write_message("Tarama tamamlandı.")
            self.write_message(f"{len(results)} adet dosya taşındı.")
            self.write_message(f"{len(deleted_folders)} adet klasör silindi.")
            self.scan_button.config(state=tk.NORMAL)