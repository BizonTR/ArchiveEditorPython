import os
import time
import hashlib

class CloneFileScanner:
    def __init__(self, directories, callback=None):
        if not isinstance(directories, list):
            raise TypeError("Directories should be a list.")
        self.directories = directories  # Şimdi bir liste olarak dizinler
        self.callback = callback
        self.scanned_size = 0  # Toplam taranan dosya boyutu

    def hash_file(self, file_path):
        if not isinstance(file_path, str):
            raise TypeError("file_path should be a string.")
        hasher = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                buf = f.read()
                hasher.update(buf)
        except Exception as e:
            self.callback(f"Error hashing file {file_path}: {e}")
            return None
        return hasher.hexdigest()

    def scan_files(self, progress_callback=None):
        results = []
        file_hashes = {}

        try:
            # Tüm dizinleri tek bir kök dizin gibi tarayın
            for directory in self.directories:
                if not os.path.isdir(directory):
                    self.callback(f"Directory not found: {directory}")
                    continue
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            file_size = os.path.getsize(file_path)
                            file_size_mb = file_size / (1024 * 1024)  # MB

                            # Dosyanın oluşturma tarihini al ve gün.ay.yıl formatına dönüştür
                            creation_time = os.path.getctime(file_path)
                            creation_date = time.strftime("%d.%m.%Y", time.localtime(creation_time))

                            # Dosyanın değiştirme tarihini al ve gün.ay.yıl formatına dönüştür
                            modification_time = os.path.getmtime(file_path)
                            modification_date = time.strftime("%d.%m.%Y", time.localtime(modification_time))

                            # Dosya hash'ini hesapla
                            file_hash = self.hash_file(file_path)
                            if file_hash is None:
                                continue

                            if file_hash in file_hashes:
                                file_hashes[file_hash].append({
                                    'file_name': file,
                                    'file_path': file_path,
                                    'creation_date': creation_date,
                                    'modification_date': modification_date,
                                    'file_size': file_size_mb
                                })
                            else:
                                file_hashes[file_hash] = [{
                                    'file_name': file,
                                    'file_path': file_path,
                                    'creation_date': creation_date,
                                    'modification_date': modification_date,
                                    'file_size': file_size_mb
                                }]

                            # Callback ile verileri ilet
                            self.callback({
                                'file_name': file,
                                'file_path': file_path,
                                'creation_date': creation_date,
                                'modification_date': modification_date,
                                'file_size': f"{file_size_mb:.2f} MB"
                            })
                            
                            # Her dosya tarandıktan sonra arayüzü güncelle
                            if progress_callback:
                                progress_callback(file_size_mb)

                            # Klasörün ilerleme durumu
                            self.callback(f"Klasör taranıyor: {root}\n---------------")

                        except Exception as e:
                            self.callback(f"Error processing file {file_path}: {e}")

            # Klon dosyaları bul
            for file_paths in file_hashes.values():
                if len(file_paths) > 1:
                    for file_info in file_paths:
                        results.append(file_info)
            
            return results

        except Exception as e:
            error_message = f"Bir hata oluştu: {str(e)}\n---------------"
            self.callback(error_message)
            return results
    
    def get_scanned_size(self):
        return self.scanned_size