import os
import shutil
import time
import uuid

class FileScanner:
    def __init__(self, directory, callback=None, keep_copied_files=False):
        self.directory = directory
        self.callback = callback
        self.keep_copied_files = keep_copied_files
        self.image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
        self.video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
        self.archive_directory = os.path.join(self.directory, "Archive Editor")

        self.month_names = {
            '01': 'Ocak', '02': 'Şubat', '03': 'Mart', '04': 'Nisan',
            '05': 'Mayıs', '06': 'Haziran', '07': 'Temmuz', '08': 'Ağustos',
            '09': 'Eylül', '10': 'Ekim', '11': 'Kasım', '12': 'Aralık'
        }

    def scan_files(self):
        results = []
        try:
            if not os.path.exists(self.archive_directory):
                os.makedirs(self.archive_directory)

            for root, dirs, files in os.walk(self.directory):
                # "Archive Editor" klasörünü atlamak için kontrol
                dirs[:] = [d for d in dirs if os.path.join(root, d) != self.archive_directory]

                for file in files:
                    file_path = os.path.join(root, file)
                    file_extension = os.path.splitext(file_path)[1].lower()
                    file_type = "Diğer"
                    
                    if file_extension in self.image_extensions:
                        file_type = "Resim"
                    elif file_extension in self.video_extensions:
                        file_type = "Video"

                    # Dosyanın oluşturma tarihini al ve gün.ay.yıl formatına dönüştür
                    creation_time = os.path.getctime(file_path)
                    creation_date = time.strftime("%d.%m.%Y", time.localtime(creation_time))

                    # Dosyanın değiştirme tarihini al ve gün.ay.yıl formatına dönüştür
                    modification_time = os.path.getmtime(file_path)
                    modification_date = time.strftime("%d.%m.%Y", time.localtime(modification_time))

                    results.append((file_path, file_type, creation_date, modification_date))
                    self.callback(f"Tarandı: {file_path}\n---------------")

                    # Yıl ve ay bilgisini al
                    modification_year = time.strftime("%Y", time.localtime(modification_time))
                    modification_month = time.strftime("%m", time.localtime(modification_time))
                    modification_month_name = self.month_names.get(modification_month, modification_month)

                    # Dosya türüne göre klasör oluştur
                    type_directory = os.path.join(self.archive_directory, modification_year, modification_month_name, file_type)
                    if not os.path.exists(type_directory):
                        os.makedirs(type_directory)

                    # Yeni dosya yolunu belirle
                    new_file_path = os.path.join(type_directory, file)

                    if self.keep_copied_files:
                        if os.path.exists(new_file_path):
                            new_file_path = self.get_unique_filename(new_file_path)
                            print(f"1 - orj:{file} new:{new_file_path}")
                        else:
                            print(f"2 orj:{file} - new:{new_file_path}")
                    else:
                        print("0")

                    # Dosyayı taşı
                    shutil.move(file_path, new_file_path)
                    self.callback(f"Taşındı: {file_path} -> {new_file_path}\n---------------")

                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    self.callback(f"Klasör taranıyor: {dir_path}\n---------------")

        except Exception as e:
            error_message = f"Bir hata oluştu: {str(e)}\n---------------"
            self.callback(error_message)

        return results

    def get_unique_filename(self, filepath):
        filename, extension = os.path.splitext(filepath)
        unique_name = str(uuid.uuid4())
        new_filepath = f"{filename}_{unique_name}{extension}"
        return new_filepath

    def remove_empty_directories(self, directory):
        deleted_folders = []
        errors = []
        try:
            for root, dirs, files in os.walk(directory, topdown=False):
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    try:
                        if not os.listdir(dir_path):  # Klasör boşsa sil
                            os.rmdir(dir_path)
                            deleted_folders.append(dir_path)
                            self.callback(f"Klasör silindi: {dir_path}\n---------------")
                    except Exception as e:
                        error_message = f"Klasör silinemedi: {dir_path}. Hata: {str(e)}\n---------------"
                        errors.append(error_message)

        except Exception as e:
            error_message = f"Bir hata oluştu: {str(e)}\n---------------"
            self.callback(error_message)

        return deleted_folders, errors