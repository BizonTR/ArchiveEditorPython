import tkinter as tk
from uiGeneral import UIGeneral

def main():
    root = tk.Tk()
    root.title("Arşiv Düzenleme Programı")
    
    # Pencereyi ekranın tamamını kaplayacak şekilde ayarlayın
    window_width = root.winfo_screenwidth()
    window_height = root.winfo_screenheight()
    root.geometry(f"{window_width}x{window_height}+0+0")  # Ekranın sol üst köşesine yerleştirin

    app = UIGeneral(root)  # UIGeneral sınıfını başlatın
    root.mainloop()

if __name__ == "__main__":
    main()