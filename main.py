import tkinter as tk
from ui import ArchiveApp
from fileScanner import FileScanner

def on_directory_selected(directory_path):
    scanner = FileScanner(directory_path)
    scanner.scan_files()

def main():
    root = tk.Tk()
    root.title("Arşiv Düzenleme Programı")
    
    # Pencereyi ekranın tamamını kaplayacak şekilde ayarlayın
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}+0+0")  # Ekranın sol üst köşesine yerleştir

    app = ArchiveApp(root)  # ArchiveApp sınıfını sadece root argümanı ile başlatın
    app.search_button.config(command=app.search_archive)  # Arama butonu komutunu düzenleyin
    app.scan_button.config(command=app.start_scan)  # Tarama butonu komutunu düzenleyin

    root.mainloop()

if __name__ == "__main__":
    main()