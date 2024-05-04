import platform
import socket
from termcolor import colored
from datetime import datetime, timedelta
import time
import glob
import ctypes
import matplotlib.pyplot as plt
import chardet
import os
import getpass
import argparse
import subprocess
import logging

euid = os.getpid() # User ID almak için
logging.basicConfig(level=logging.ERROR) # konfrigürasyon
username = getpass.getuser()
parser = argparse.ArgumentParser(description='Log yönetim aracı.')
parser.add_argument('-c', '--clear', action='store_true', help='Logları temizle')
parser.add_argument('-s', '--search', type=str, help='Logları ara')
parser.add_argument('-o', '--sort', type=str, choices=['date', 'size'], help='Logları sırala')
parser.add_argument('-d', '--days', type=int, help='Belirli bir tarihten önceki logları sil')
parser.add_argument('-g', '--graph', type=str,choices=['age','size','content'], help='Log dosyalarının yaşlarını, boyutlarını, içeriklerini grafikle göster')
args = parser.parse_args()

folder_path = '/var/log/'
log_files = glob.glob(os.path.join(folder_path, '**/**/*.log*'), recursive=True)

def clear_linux_logs():
   if log_files != []:
      lenghtlist = len(log_files)
      total = 0
      for log_file in log_files:
         if os.path.exists(log_file):
            file_size = os.path.getsize(log_file)
            total += file_size
            os.remove(log_file)
            time.sleep(0.3)
            print(colored(log_file, 'green'), " başarıyla silindi veya yeniden adlandırıldı\n")

      print(colored(f'\nSilinen dosya boyutu: {total / 1024} kilobayt\n', 'red'))

      print(colored(f"\nSilinen dosya sayısı: {lenghtlist}", 'red'))

   else:
      print("Log dosyası bulunamadı.")



def detect_file_encoding(file_path):
   with open(file_path, 'rb') as f:
      result = chardet.detect(f.read())
   return result['encoding']


def sort_logs_by_date():
   log_files.sort(key=os.path.getmtime)
   log_files.sort(key=os.path.getmtime)
   for log_file in log_files:
      time.sleep(0.2)
      modification_time = time.ctime(os.path.getmtime(log_file))
      print(log_file, "  /// INFO: Son değiştirilme zamanı: ", colored(modification_time, 'green'))
def age_graphic():
   log_files = glob.glob('/var/log/**/*.log*', recursive=True)
   log_file_ages = []
   for log_file in log_files:
      modification_time = os.path.getmtime(log_file)
      modification_date = datetime.fromtimestamp(modification_time)
      age = (datetime.now() - modification_date).days
      log_file_ages.append(age)
   plt.hist(log_file_ages, bins=20, edgecolor='black')
   plt.xlabel('Age (days)')
   plt.ylabel('Count')
   plt.title('Log Dosya Yaşlarınını Grafiksel Dağılımı')
   plt.show()



def classify_logs_by_error_messages():
    log_files = glob.glob('/var/log/**/*.log*', recursive=True)

    # Sınıflandırma kriterlerimiz
    categories = {
        "error": [],
        "warning": [],
        "info": [],
    }

    for log_file in log_files:
        try:
            with open(log_file, 'r') as file:
                content = file.read().lower()  # İçeriği oku ve küçük harfe çevir
                for category in categories:
                    if category in content:
                        categories[category].append(log_file)
        except UnicodeDecodeError:
            try:
                with open(log_file, 'r', encoding='ISO-8859-1') as file:
                    content = file.read().lower()
                    for category in categories:
                        if category in content:
                            categories[category].append(log_file)
            except Exception as e:
                print(f"Could not read file {log_file} due to {str(e)}")

    return categories

def graph_logs_by_error_messages():
   categories = classify_logs_by_error_messages()
   counts = {category: len(files) for category, files in categories.items()}
   plt.bar(counts.keys(), counts.values())
   plt.xlabel('Category')
   plt.ylabel('Count')

   plt.title('Error Mesajlarının Grafiksel Dağılımı')
   plt.show()


def size_graphic():
   log_file_sizes = []
   for log_file in log_files:
      size = os.path.getsize(log_file)
      log_file_sizes.append(size)

   plt.hist(log_file_sizes, bins=20, edgecolor='black')
   plt.xlabel('Size (bytes)')
   plt.ylabel('Count')
   plt.title('Log Dosyalarının Büyüklüğe Göre Grafiksel Dağılımı')
   plt.show()


def sort_logs_by_size():
   log_files.sort(key=os.path.getsize, reverse=True)
   for log_file in log_files:
      time.sleep(0.2)
      size_kb = os.path.getsize(log_file) / 1024
      print(log_file + " /// INFO: Dosya boyutu: ", colored(size_kb, 'green'), "kilobayt")


def search_logs(search_word):

   if os_name == 'Windows':
      log_files = glob.glob('C:\\Windows\\System32\\winevt\\Logs\\*')
      file_count = 0  # Bulunan dosyaları saymak için yeni bir değişken
      for log_file in log_files:
         word_found = False
         try:
            with open(log_file, 'r') as file:
               for line_number, line in enumerate(file, start=1):
                  if search_word in line:
                     print(
                        f'Aranan Kelime Bulundu: "{search_word}" Dosya ismi:{log_file} Satır numarası: {line_number}: {line.strip()}')
                     word_found = True
                     break  # Kelimeyi bulduktan sonra döngüyü kır
         except IOError:
            print(f"Hata: {log_file} açılamadı.")
            continue
         if word_found:
            file_count += 1  # Kelimeyi içeren her dosya için sayacı artırın
         else:
            print("Aranan kelime bu dosyada bulunamadı: " + log_file)
      print(f"Aranan kelime {file_count} dosyada bulundu.")  # Toplam dosya sayısını yazdırın

   if os_name == 'Linux':

      file_count = 0  # Bulunan dosyaları saymak için yeni bir değişken

      for log_file in log_files:
         word_found = False
         try:
            with open(log_file, 'rb') as file:
               for line_number, line in enumerate(file, start=1):
                  try:
                     line = line.decode('utf-8')
                  except UnicodeDecodeError:
                     encoding = detect_file_encoding(log_file)
                     if encoding is not None:
                        line = line.decode(encoding)
                     else:
                        continue
                  if search_word in line:
                     print(colored(
                        f'Aranan Kelime Bulundu: "{search_word}" Dosya ismi:{log_file} Satır numarası: {line_number}: {line.strip()}',
                        'green'))
                     word_found = True
                     break  # Kelimeyi bulduktan sonra döngüyü kır
         except IOError:
            print(f"Hata: {log_file} açılamadı.")
            continue
         if word_found:
            file_count += 1  # Kelimeyi içeren her dosya için sayacı artırın
         else:
            print(colored("Aranan kelime bu dosyada bulunamadı: ", 'red') + log_file)
      print(f"Aranan kelime {file_count} dosyada bulundu.")  # Toplam dosya sayısını yazdırın


def clear_windows_logs():
   # Windows Event Log'ları listele
   logs = subprocess.run(["wevtutil", "el"], capture_output=True, text=True).stdout.splitlines()

   # Silinen log sayısını takip etmek için bir sayaç oluştur
   deleted_logs_count = 0

   # Her bir log'u temizle
   for log in logs:
      print(f"Temizlenir: {log}")
      result = subprocess.run(["wevtutil", "cl", log], capture_output=True, text=True)

      # Eğer log başarıyla temizlendi ise, sayacı artır
      if "Log Dosyaları Başarıyla Temizlendi." in result.stdout:
         deleted_logs_count += 1

   print(f"Toplamda Silinen Log Sayısı: {deleted_logs_count}")


def calculate_days_ago(days):
   for log_file in log_files:
      if os.path.exists(log_file):  # Check if the file exists
         file_time = os.path.getmtime(log_file)
         file_date = datetime.fromtimestamp(file_time)
         current_datetime = datetime.now()
         days_ago = (current_datetime - file_date).days
         days_ago_time = current_datetime - timedelta(days=days)
         if days_ago_time >= file_date:
            print(colored("Dosya siliniyor...", 'red') + " dosya " + colored(f"{days_ago}",
                                       'red') + " gün önce oluşturuldu")
            os.system("rm -rf " + log_file)
         elif days_ago_time < file_date:
            print(colored("Dosya silinmiyor...", 'blue') + " dosya " + colored(f"{days_ago}",
                                                                               'blue') + " gün önce oluşturuldu")
         else:
            print(f"File does not exist: {log_file}")


def is_admin():
   try:
      return ctypes.windll.shell32.IsUserAnAdmin()
   except:
      return False


hostname = socket.gethostname()
os_name = platform.system()
print("İşletim Sistemi : "+colored('{}', 'red').format(os_name))
time.sleep(0.8)
print("Kullanıcı adı:" +colored('{}', 'red').format(username))
time.sleep(0.8)
if euid == 0 or is_admin():
   logging.info(colored("Sudo yetkisi alındı",'blue'))
   time.sleep(1)

   if args.search:
      search_logs(args.search)
   elif args.clear:
      if os_name == 'Windows':
         print("Windows logları temizleniyor...")
         clear_windows_logs()
      elif os_name == 'Linux':
         print("Linux logları temizleniyor...")
         clear_linux_logs()
   elif args.sort:
      if args.sort == 'date':
         sort_logs_by_date()
      elif args.sort == 'size':
         sort_logs_by_size()
   elif args.graph:
      if args.graph == 'age':
         age_graphic()
      elif args.graph == 'size':
         size_graphic()
      elif args.graph == 'content':
            graph_logs_by_error_messages()
   elif args.days:
      calculate_days_ago(args.days)
else:
   print(colored("Programı çalıştırmak için sudo yetkisi gerekmektedir. Lütfen sudo yetkisi ile çalıştırın.",'red'))