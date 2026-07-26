from qgis.core import QgsSymbol, QgsSimpleFillSymbolLayer
from PyQt5.QtGui import QColor

# Kumpulan warna siap pakai (Preset Palette)
# Format: (R, G, B, Alpha)
WARNA_PRESET = {
    "MERAH_BAHAYA": (255, 0, 0, 120),
    "HIJAU_AMAN": (0, 255, 0, 80),
    "BIRU_AIR": (0, 120, 255, 100),
    "KUNING_PERINGATAN": (255, 200, 0, 100),
    "ABU_BANGUNAN": (128, 128, 128, 150)
}

def warnai_polygon_dengan_preset(layer, nama_warna: str, lebar_garis: float = 0.6):
    """
    Mewarnai layer menggunakan pilihan warna siap pakai yang sudah disediakan.
    Jika nama_warna tidak ditemukan, otomatis menggunakan warna ABU_BANGUNAN.
    """
    # Ambil nilai RGBA dari preset berdasarkan nama yang dipilih
    r, g, b, alpha = WARNA_PRESET.get(nama_warna, WARNA_PRESET["ABU_BANGUNAN"])
    
    warna_isi = QColor(r, g, b, alpha)
    warna_garis = QColor(r, g, b, 255) # Garis tepi dibuat solid (tidak transparan)
    
    simbol_layer = QgsSimpleFillSymbolLayer.create({
        'color': f'{warna_isi.red()},{warna_isi.green()},{warna_isi.blue()},{warna_isi.alpha()}',
        'outline_color': f'{warna_garis.red()},{warna_garis.green()},{warna_garis.blue()},{warna_garis.alpha()}',
        'outline_width': str(lebar_garis),
        'style': 'solid',
        'outline_style': 'solid'
    })
    
    if simbol_layer is not None:
        layer.renderer().setSymbol(simbol_layer)
        layer.triggerRepaint()
        print(f"[+] Sukses: Layer otomatis diwarnai dengan preset: {nama_warna}")