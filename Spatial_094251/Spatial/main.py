import json
import os
import sys

# =============================================================================
# [FITUR 1] DETEKSI FLASHDISK OTOMATIS (UNIVERSAL DEVICE DETECTION)
# =============================================================================
# Blok ini bertugas mencari tahu di Drive mana (D:, E:, atau F:) folder ini berada, 
# meskipun skrip ini dibuka lewat Python Console QGIS yang sering menyembunyikan jalur asli.
try:
    folder_proyek = os.path.dirname(os.path.abspath(__file__))
except NameError:
    import utils
    folder_proyek = os.path.dirname(os.path.dirname(os.path.abspath(utils.__file__)))

# Daftarkan jalur folder ini ke memori Python QGIS agar tidak muncul error "No Module Named utils"
if folder_proyek not in sys.path:
    sys.path.append(folder_proyek)

# --- SEKARANG AMAN UNTUK MENG-IMPORT MODUL INTERNAL ---
from qgis.core import QgsProject
from utils.data_loader import load_filter_dan_reproject 
from utils.analyzers import jalankan_paket_analisis
from utils.styler import warnai_polygon_dengan_preset


def jalankan_pipeline_utama(jalur_file_klien: str, jalur_config_json: str):
    # -------------------------------------------------------------------------
    # [FITUR 2] SENSOR VALIDASI & KOORDINAT (DATA RESCUE GATEWAY)
    # -------------------------------------------------------------------------
    print("[1] Memasukkan data klien ke gerbang penyaring data...")
    layer_rapi, status = load_filter_dan_reproject(jalur_file_klien)
    
    # Jika gerbang mendeteksi file kosong, rusak, atau salah tipe, sistem berhenti dengan sopan
    if "ERROR" in status:
        print(f"[X] EKSEKUSI DIHENTIKAN: {status}. Silakan periksa file klien.")
        return
    
    # Baca file konfigurasi JSON berisi instruksi analisis
    with open(jalur_config_json, 'r') as f:
        daftar_analisis = json.load(f)
        
    # -------------------------------------------------------------------------
    # [FITUR 3] PENERJEMAH JALUR PORTABLE (DYNAMIC PATH TRANSLATOR)
    # -------------------------------------------------------------------------
    # Jika di dalam JSON ada analisis dependen (seperti Clip/Intersection) yang 
    # membutuhkan data sekunder (contoh: "hutan_lindung.geojson"), blok ini akan 
    # otomatis merakit alamat lengkapnya berbasis lokasi flashdisk saat ini.
    for item in daftar_analisis:
        params = item['parameter']
        for kunci, nilai in params.items():
            if isinstance(nilai, str) and nilai.endswith('.geojson'):
                params[kunci] = os.path.join(folder_proyek, nilai)
        
    # -------------------------------------------------------------------------
    # [FITUR 4] EKSEKUSI & VISUALISASI OTOMATIS (ENGINE & STYLER RUNNER)
    # -------------------------------------------------------------------------
    # Lempar data bersih ke mesin analisis asli yang murni tanpa modifikasi jalur
    semua_hasil = jalankan_paket_analisis(layer_rapi, daftar_analisis)
    
    # Warnai hasil analisis secara otomatis menggunakan preset estetika firmamu
    for hasil in semua_hasil:
        warnai_polygon_dengan_preset(hasil['layer'], hasil['warna'])
        QgsProject.instance().addMapLayer(hasil['layer'])
        
    print("[*] Sukses Total: Semua analisis di dalam JSON selesai dipetakan!")


if __name__ == "__main__":
    # Merakit jalur file secara dinamis agar selalu mengarah ke folder flashdisk saat ini
    file_uji_coba = os.path.join(folder_proyek, "lahan_klien.geojson")
    config_json = os.path.join(folder_proyek, "analisis_config.json")
    
    # Jalankan sistem utama
    jalankan_pipeline_utama(file_uji_coba, config_json)