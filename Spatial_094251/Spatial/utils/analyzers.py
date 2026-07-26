from qgis import processing

def jalankan_paket_analisis(layer_meter, daftar_analisis: list):
    """
    Mesin Universal Langsung Pakai.
    Menerima layer data dan daftar analisis dari file JSON,
    lalu mengeksekusinya satu per satu secara otomatis.
    """
    hasil_semua_analisis = []

    for item in daftar_analisis:
        print(f"[➔] Menjalankan: {item['nama_analisis']} ({item['algoritma']})")
        
        # Ambil parameter dari JSON dan masukkan INPUT layer kita
        params = item['parameter'].copy()
        params['INPUT'] = layer_meter
        
        # Set tempat penyimpanan otomatis di RAM
        nama_clean = item['algoritma'].replace(':', '_')
        params['OUTPUT'] = f'memory:Hasil_{nama_clean}'
        
        try:
            # Eksekusi instan lewat QGIS
            output_layer = processing.run(item['algoritma'], params)['OUTPUT']
            
            # Simpan hasilnya beserta warna presetnya untuk dioper ke main.py
            hasil_semua_analisis.append({
                'layer': output_layer,
                'warna': item['warna_preset']
            })
        except Exception as e:
            print(f"[-] Gagal menjalankan {item['nama_analisis']}: {str(e)}")
            
    return hasil_semua_analisis