import os
from qgis.core import QgsVectorLayer, QgsCoordinateReferenceSystem, QgsWkbTypes
from qgis import processing
from .geo_calculator import hitung_utm_global

def load_filter_dan_reproject(jalur_file: str):
    """
    GERBANG UTAMA: Memuat file klien dan langsung menyaring 4 skenario kerusakan data
    (CRS salah/kosong, file kosong, tipe geometri salah, format file aneh).
    """
    # -------------------------------------------------------------------------
    # PROTEKSI 1: Cek Keberadaan File Fisik
    # -------------------------------------------------------------------------
    if not os.path.exists(jalur_file):
        return None, "ERROR_FILE_TIDAK_DITEMUKAN"
        
    # Memuat file secara universal (Bisa .geojson, .shp, .kml, .gpkg, dll.)
    layer_mentah = QgsVectorLayer(jalur_file, "Lahan Mentah Klien", "ogr")
    
    # -------------------------------------------------------------------------
    # PROTEKSI 2: Cek Apakah File Rusak atau Kosong Tanpa Objek
    # -------------------------------------------------------------------------
    if not layer_mentah.isValid():
        return None, "ERROR_FORMAT_FILE_RUSAK"
        
    if layer_mentah.featureCount() == 0:
        return None, "ERROR_FILE_KOSONG_TANPA_DATA"

    # -------------------------------------------------------------------------
    # PROTECTIONS 3: Cek Tipe Geometri (Memastikan tipe data spasial valid)
    # -------------------------------------------------------------------------
    tipe_geom = layer_mentah.geometryType()
    # 0 = Point (Titik), 1 = Line (Garis), 2 = Polygon (Area), 3 = Unknown/No Geometry
    if tipe_geom == QgsWkbTypes.NullGeometry:
        return None, "ERROR_DATA_HANYA_TABEL_TANPA_GAMBAR_PETA"

    # -------------------------------------------------------------------------
    # PROTEKSI 4: Penyelamatan & Penyelarasan Sistem Koordinat (CRS)
    # -------------------------------------------------------------------------
    crs_asli = layer_mentah.crs()
    
    # Skenario A: File tidak punya identitas koordinat (Buta)
    if not crs_asli.isValid():
        print("[!] Warning: File buta koordinat. Dipaksa ke derajat standar WGS84.")
        layer_mentah.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))
        
    # Skenario B: File ternyata sudah dalam satuan Meter (Bypass proses)
    elif crs_asli.mapUnits() == 0:  # 0 artinya QgsUnitTypes.DistanceMeters
        print(f"[+] Info: Data sudah dalam satuan METER ({crs_asli.authid()}).")
        return layer_mentah, "SUKSES_METERAN"
        
    # Skenario C: File menggunakan koordinat derajat selain WGS84 standar
    elif crs_asli.authid() != "EPSG:4326" and crs_asli.mapUnits() == 2:  # 2 artinya Derajat
        print(f"[*] Info: Mengubah koordinat derajat aneh ({crs_asli.authid()}) ke WGS84 standar...")
        param_align = {
            'INPUT': layer_mentah,
            'TARGET_CRS': 'EPSG:4326',
            'OUTPUT': 'TEMPORARY_OUTPUT'
        }
        layer_mentah = processing.run('native:reprojectlayer', param_align)['OUTPUT']

    # -------------------------------------------------------------------------
    # PROSES AKHIR: HITUNG DAN AUTO-CONVERT KE METER GLOBAL (UTM)
    # -------------------------------------------------------------------------
    titik_tengah = layer_mentah.extent().center()
    epsg_target = hitung_utm_global(titik_tengah.x(), titik_tengah.y())
    
    parameter_reproject = {
        'INPUT': layer_mentah,
        'TARGET_CRS': epsg_target,
        'OUTPUT': 'TEMPORARY_OUTPUT'
    }
    hasil = processing.run('native:reprojectlayer', parameter_reproject)
    
    print(f"[✓] Data bersih & dikunci ke koordinat meter lokal bumi: {epsg_target}")
    return hasil['OUTPUT'], "SUKSES_DIUBAH_KE_METER"