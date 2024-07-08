import tkinter as tk
from tkinter import filedialog, scrolledtext, BooleanVar
from fileScanner import FileScanner

class ArchiveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Arşiv Düzenleme Programı")
        
        self.directory_path = None
        self.keep_copied_files_var = BooleanVar()
        self.keep_copied_files_var.set(False)  # Başlangıçta işaretli değil

        # Dosya bilgilerini gösterecek scrolledtext (scrollbar'lı metin kutusu)
        self.textbox = scrolledtext.ScrolledText(root, height=20, width=50)
        self.textbox.pack(pady=20)

        self.search_button = tk.Button(root, text="Arşiv Ara", command=self.search_archive)
        self.search_button.pack(pady=10)

        self.keep_copied_files_checkbox = tk.Checkbutton(root, text="Kopyalanan dosyaların ismini değiştirerek sakla",
                                                         variable=self.keep_copied_files_var)
        self.keep_copied_files_checkbox.pack()

        self.scan_button = tk.Button(root, text="Tarama Başlat", command=self.start_scan, state=tk.DISABLED)
        self.scan_button.pack(pady=10)

    def write_message(self, message):
        self.textbox.insert(tk.END, f"{message}\n")
        self.textbox.see(tk.END)  # Metin kutusunu en son yazılan satıra kaydır
        self.root.update_idletasks()  # Arayüzü güncelle

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
            self.scan_button.config(state=tk.DISABLED)  # Tarama başladığında butonu devre dışı bırak
            self.root.update_idletasks()  # Arayüzün güncellenmesi için gerekli

            # Dosya taramasını yapacak işlev çağrılıyor
            scanner = FileScanner(self.directory_path, callback=self.write_message, keep_copied_files=self.keep_copied_files_var.get())
            results = scanner.scan_files()

            # Tarama sonuçlarını metin kutusuna yazdır
            for result in results:
                self.write_message(f"Dosya: {result[0]}")
                self.write_message(f"Tür: {result[1]}")
                self.write_message(f"Oluşturma Tarihi: {result[2]}")
                self.write_message(f"Değiştirme Tarihi: {result[3]}")
                self.write_message("---------------")

            # Boş kalan klasörleri silme işlemlerini metin kutusuna yazdır
            self.write_message("Boş kalan klasörler siliniyor...")
            deleted_folders, errors = scanner.remove_empty_directories(self.directory_path)

            # Hataları en son yazdır
            if errors:
                self.write_message("Silinemeyen klasörler:")
                for error in errors:
                    self.write_message(error)

            self.write_message("Tarama tamamlandı.")
            self.write_message(f"{len(results)} adet dosya taşındı.")
            self.write_message(f"{len(deleted_folders)} adet klasör silindi.")
            self.scan_button.config(state=tk.NORMAL)  # Tarama tamamlandığında butonu tekrar etkinleştir