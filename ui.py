import tkinter as tk
from tkinter import filedialog, scrolledtext, BooleanVar, messagebox
from tkinter import ttk
import os
import subprocess
import threading
from fileScanner import FileScanner

class ArchiveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Arşiv Düzenleme Programı")

        self.directory_paths = []
        self.output_directory_path = None
        self.keep_copied_files_var = BooleanVar()
        self.keep_copied_files_var.set(False)
        self.total_size = 0
        self.scanned_size = 0

        # Ana canvas oluştur ve tüm pencereyi kapla
        self.main_canvas = tk.Canvas(root, borderwidth=0, background="#ffffff")
        self.main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar oluştur ve ana canvas'a bağla
        self.scrollbar = tk.Scrollbar(root, orient="vertical", command=self.main_canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Ana frame oluştur ve canvas'a ekle
        self.main_frame = tk.Frame(self.main_canvas, background="#ffffff")
        self.main_frame.bind("<Configure>", self.on_frame_configure)

        self.main_canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)

        # Farne tekerleği ile kaydırma işlevi ekle
        self.main_canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

        # Frame'leri ana frame'e ekle
        self.setup_frames()

    def setup_frames(self):
        # Taranacak arşivler için frame
        self.archive_frame = tk.Frame(self.main_frame, width=400, height=600, bg="#f0f0f0")
        self.archive_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.archive_list_label = tk.Label(self.archive_frame, text="Taranacak Arşivler", bg="#f0f0f0")
        self.archive_list_label.pack()

        self.archive_tree_frame = tk.Frame(self.archive_frame)
        self.archive_tree_frame.pack(fill=tk.BOTH, expand=True)

        self.archive_tree = ttk.Treeview(self.archive_tree_frame, columns=("Dizin Yolu",), show='headings', height=10)
        self.archive_tree.heading("Dizin Yolu", text="Dizin Yolu")
        self.archive_tree.column("Dizin Yolu", minwidth=200, width=300, stretch=tk.YES)

        self.archive_tree_scroll_y = ttk.Scrollbar(self.archive_tree_frame, orient="vertical", command=self.archive_tree.yview)
        self.archive_tree.configure(yscrollcommand=self.archive_tree_scroll_y.set)
        self.archive_tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.archive_tree_scroll_x = ttk.Scrollbar(self.archive_tree_frame, orient="horizontal", command=self.archive_tree.xview)
        self.archive_tree.configure(xscrollcommand=self.archive_tree_scroll_x.set)
        self.archive_tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.archive_tree.pack(pady=10, fill=tk.BOTH, expand=True)

        self.search_button = tk.Button(self.archive_frame, text="Arşiv Ara", command=self.search_archive)
        self.search_button.pack(pady=10, side=tk.LEFT)

        self.remove_button = tk.Button(self.archive_frame, text="Seçileni Sil", command=self.remove_selected_archive)
        self.remove_button.pack(side=tk.LEFT, padx=10)

        # Çıktı klasörü için frame
        self.output_frame = tk.Frame(self.main_frame, width=400, height=600, bg="#f0f0f0")
        self.output_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.output_list_label = tk.Label(self.output_frame, text="Çıktı Klasörü", bg="#f0f0f0")
        self.output_list_label.pack()

        self.output_tree_frame = tk.Frame(self.output_frame)
        self.output_tree_frame.pack(fill=tk.BOTH, expand=False)

        self.output_tree = ttk.Treeview(self.output_tree_frame, columns=("Dizin Yolu",), show='headings')
        self.output_tree.heading("Dizin Yolu", text="Dizin Yolu")
        self.output_tree.column("Dizin Yolu", minwidth=200, width=300, stretch=tk.YES)

        self.output_tree_scroll_y = ttk.Scrollbar(self.output_tree_frame, orient="vertical", command=self.output_tree.yview)
        self.output_tree.configure(yscrollcommand=self.output_tree_scroll_y.set)
        self.output_tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.output_tree_scroll_x = ttk.Scrollbar(self.output_tree_frame, orient="horizontal", command=self.output_tree.xview)
        self.output_tree.configure(xscrollcommand=self.output_tree_scroll_x.set)
        self.output_tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.output_tree.pack(pady=10, fill=tk.BOTH, expand=True)

        self.select_output_button = tk.Button(self.output_frame, text="Çıktı Klasörü Seç", command=self.select_output_directory)
        self.select_output_button.pack(pady=10)

        # Sağ tarafta butonlar ve checkbox
        self.right_inner_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.right_inner_frame.grid(row=0, column=2, padx=20, pady=20, sticky="nsew")

        self.keep_copied_files_checkbox = tk.Checkbutton(self.right_inner_frame, text="Klon dosyaları farklı isimle sakla",
                                                         variable=self.keep_copied_files_var, bg="#f0f0f0")
        self.keep_copied_files_checkbox.grid(row=0, column=0, pady=10, padx=5)

        self.scan_button = tk.Button(self.right_inner_frame, text="Tarama Başlat", command=self.start_scan, state=tk.DISABLED)
        self.scan_button.grid(row=1, column=0, pady=10, padx=5)

        self.progress_frame = tk.Frame(self.right_inner_frame, bg="#f0f0f0")
        self.progress_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        self.total_size_label = tk.Label(self.progress_frame, text="Toplam Boyut: 0 MB", bg="#f0f0f0")
        self.total_size_label.pack()

        self.scanned_size_label = tk.Label(self.progress_frame, text="Tarama Boyutu: 0 MB", bg="#f0f0f0")
        self.scanned_size_label.pack()

        # Dosya bilgilerini gösterecek Treeview widget'ı için bir frame
        self.middle_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.middle_frame.grid(row=1, column=0, columnspan=3, padx=20, pady=20, sticky="nsew")

        self.tree = ttk.Treeview(self.middle_frame, columns=("Dosya Adı", "Dosya Yolu", "Yeni Yer", "Oluşturma Tarihi", "Değiştirme Tarihi", "Tür", "Boyut"), show='headings')
        self.tree.heading("Dosya Adı", text="Dosya Adı")
        self.tree.heading("Dosya Yolu", text="Dosya Yolu")
        self.tree.heading("Yeni Yer", text="Yeni Yer")
        self.tree.heading("Oluşturma Tarihi", text="Oluşturma Tarihi")
        self.tree.heading("Değiştirme Tarihi", text="Değiştirme Tarihi")
        self.tree.heading("Tür", text="Tür")
        self.tree.heading("Boyut", text="Boyut")

        self.tree.column("Dosya Adı", minwidth=100, width=150, stretch=tk.NO)
        self.tree.column("Dosya Yolu", minwidth=300, width=420, stretch=tk.NO)
        self.tree.column("Yeni Yer", minwidth=400, width=520, stretch=tk.NO)
        self.tree.column("Oluşturma Tarihi", minwidth=100, width=120, stretch=tk.NO)
        self.tree.column("Değiştirme Tarihi", minwidth=100, width=120, stretch=tk.NO)
        self.tree.column("Tür", minwidth=50, width=70, stretch=tk.NO)
        self.tree.column("Boyut", minwidth=50, width=70, stretch=tk.NO)

        self.tree_scroll = ttk.Scrollbar(self.middle_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scroll.set)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.horiz_scroll = ttk.Scrollbar(self.middle_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=self.horiz_scroll.set)
        self.horiz_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Dosya bilgilerini gösterecek scrolledtext (scrollbar'lı metin kutusu) için bir frame
        self.bottom_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.bottom_frame.grid(row=2, column=0, columnspan=3, padx=20, pady=20, sticky="nsew")

        self.textbox = scrolledtext.ScrolledText(self.bottom_frame, height=10, wrap=tk.NONE, state=tk.DISABLED)
        self.textbox.pack(fill=tk.BOTH, expand=True)

        self.textbox_scroll = ttk.Scrollbar(self.bottom_frame, orient="horizontal", command=self.textbox.xview)
        self.textbox.configure(xscrollcommand=self.textbox_scroll.set)
        self.textbox_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.bind("<Double-1>", self.open_file_explorer)
        self.archive_tree.bind("<Double-1>", self.open_directory_explorer)
        self.output_tree.bind("<Double-1>", self.open_directory_explorer)

    def on_frame_configure(self, event):
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))

    def on_mouse_wheel(self, event):
        if event.state & 0x0001:  # Shift tuşu basılıysa, yatay kaydırma
            self.main_canvas.xview_scroll(int(-1*(event.delta/120)), "units")
        else:  # Shift tuşu basılı değilse, dikey kaydırma
            self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

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

    def open_directory_explorer(self, event):
        widget = event.widget
        item = widget.selection()
        if item:
            item_values = widget.item(item)['values']
            if item_values:
                directory = item_values[0]  # Dizin yolu sütunu
                if os.path.exists(directory):
                    subprocess.Popen(['explorer', os.path.normpath(directory)])

    def search_archive(self):
        directory = filedialog.askdirectory()
        if directory:
            if directory in self.directory_paths:
                messagebox.showerror("Hata", "Bu dizin zaten taranacak arşivler listesinde!")
            else:
                self.directory_paths.append(directory)
                self.archive_tree.insert("", tk.END, values=(directory,))
                self.check_directories_selected()
                self.update_total_size()
        else:
            self.write_message("Hiçbir klasör seçilmedi.")

    def select_output_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            # Temizleme işlemi
            self.output_tree.delete(*self.output_tree.get_children())

            self.output_directory_path = directory
            self.output_tree.insert("", tk.END, values=(directory,))
            self.check_directories_selected()

    def remove_selected_archive(self):
        selected_item = self.archive_tree.selection()
        if selected_item:
            item_values = self.archive_tree.item(selected_item)['values']
            directory = item_values[0]
            self.directory_paths.remove(directory)
            self.archive_tree.delete(selected_item)
            self.write_message(f"Seçilen klasör kaldırıldı: {directory}")
            self.update_total_size()
        self.check_directories_selected()

    def check_directories_selected(self):
        if self.directory_paths and self.output_directory_path:
            self.scan_button.config(state=tk.NORMAL)
        else:
            self.scan_button.config(state=tk.DISABLED)

    def start_scan(self):
        if self.directory_paths and self.output_directory_path:
            self.write_message("Tarama başlatılıyor...")
            self.scan_button.config(state=tk.DISABLED)

            # Arka planda tarama işlemini başlat
            thread = threading.Thread(target=self.scan_files_in_background)
            thread.start()
        else:
            self.write_message("Lütfen arama yapılacak klasörleri ve çıktı klasörünü seçin.")

    def update_total_size(self):
        total_size = 0
        for directory in self.directory_paths:
            for dirpath, _, files in os.walk(directory):
                for file in files:
                    filepath = os.path.join(dirpath, file)
                    total_size += os.path.getsize(filepath)
        
        self.total_size = total_size / (1024 * 1024)  # MB
        self.total_size_label.config(text=f"Toplam Boyut: {self.total_size:.2f} MB")

    def scan_files_in_background(self):
        results = []
        deleted_folders = []
        self.scanned_size = 0
        self.total_size = 0

        # Arayüzdeki ilerleme çubuğunu güncellemek için bir fonksiyon
        def update_progress_bar():
            if self.total_size > 0:
                self.scanned_size_label.config(text=f"Tarama Boyutu: {self.scanned_size:.2f} MB")
            self.root.update_idletasks()

        # Toplam dosya boyutunu hesaplayalım
        def calculate_total_size():
            total_size = 0
            for directory in self.directory_paths:
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
            return total_size / (1024 * 1024)  # MB

        self.total_size = calculate_total_size()  # Toplam boyut
        self.total_size_label.config(text=f"Toplam Boyut: {self.total_size:.2f} MB")

        # Tarama işlemi
        def progress_callback(file_size):
            self.scanned_size += file_size
            update_progress_bar()

        for directory in self.directory_paths:
            scanner = FileScanner(directory, output_directory=self.output_directory_path, callback=self.write_message, keep_copied_files=self.keep_copied_files_var.get())
            results += scanner.scan_files(progress_callback=progress_callback)

            self.write_message("Boş kalan klasörler siliniyor...")
            deleted_folders_temp, errors = scanner.remove_empty_directories(directory)
            deleted_folders += deleted_folders_temp

            if errors:
                self.write_message("Silinemeyen klasörler:")
                for error in errors:
                    self.write_message(error)

        # Tarama tamamlandıktan sonra arayüzü güncelle
        self.root.after(0, lambda: self.write_message("Tarama tamamlandı."))
        self.root.after(0, lambda: self.write_message(f"{len(results)} adet dosya taşındı."))
        self.root.after(0, lambda: self.write_message(f"{len(deleted_folders)} adet klasör silindi."))
        self.root.after(0, lambda: self.scan_button.config(state=tk.NORMAL))




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
            self.textbox.config(state=tk.NORMAL)  # Yazma modunu etkinleştir
            self.textbox.insert(tk.END, f"{message}\n")
            self.textbox.see(tk.END)  # Metin kutusunu en son yazılan satıra kaydır
            self.textbox.config(state=tk.DISABLED)  # Yazma modunu devre dışı bırak
        self.root.update_idletasks()  # Arayüzü güncelle