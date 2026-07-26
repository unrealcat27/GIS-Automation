import math

def hitung_utm_global(longitude: float, latitude: float) -> str:
    """Murni menghitung kode EPSG berdasarkan koordinat global"""
    zona = math.floor((longitude + 180) / 6) + 1
    
    # Pengecualian batas wilayah khusus (Norwegia & Svalbard)
    if 56.0 <= latitude < 64.0 and 3.0 <= longitude < 12.0:
        zona = 32
    elif 72.0 <= latitude < 84.0:
        if 0.0 <= longitude < 9.0: zona = 31
        elif 9.0 <= longitude < 21.0: zona = 33
        elif 21.0 <= longitude < 33.0: zona = 35
        elif 33.0 <= longitude < 42.0: zona = 37

    if latitude < 0:
        return f"EPSG:{32700 + zona}"  # Selatan
    return f"EPSG:{32600 + zona}"      # Utara