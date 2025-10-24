

import requests
import json
import os
import time # Buat ngasih jeda

# --- KONFIGURASI ---
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY") # Lebih baik pake .env
OUTPUT_FILE = "arena_data.json" # Tempat nyimpen hasil

# --- FUNGSI PENCARIAN ---
def cari_arena(query="arena ice skating indonesia"):
    search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    all_results = []
    params = {
        'query': query,
        'key': API_KEY,
        'language': 'id' # Biar hasilnya pake Bahasa Indonesia kalo bisa
    }

    while True:
        try:
            response = requests.get(search_url, params=params)
            response.raise_for_status() # Cek kalo ada error HTTP
            data = response.json()
            
            print(f"Mencari... Status: {data.get('status')}")
            
            results = data.get('results', [])
            all_results.extend(results)

            next_page_token = data.get('next_page_token')
            if next_page_token:
                print("Ada halaman berikutnya, menunggu 2 detik...")
                time.sleep(2) # Google minta jeda sebelum minta halaman berikutnya
                params['pagetoken'] = next_page_token
            else:
                break # Ga ada halaman lagi, selesai

        except requests.exceptions.RequestException as e:
            print(f"Error saat Text Search: {e}")
            break
        except Exception as e:
            print(f"Error tidak dikenal: {e}")
            break
            
    return all_results

# --- FUNGSI DAPETIN DETAIL ---
def get_detail_tempat(place_id):
    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        'place_id': place_id,
        'fields': 'name,formatted_address,photos,website,editorial_summary', # Minta field yg relevan
        'key': API_KEY,
        'language': 'id'
    }
    
    try:
        response = requests.get(details_url, params=params)
        response.raise_for_status()
        data = response.json()
        print(f"Mendapatkan detail untuk {place_id}... Status: {data.get('status')}")
        return data.get('result')
    except requests.exceptions.RequestException as e:
        print(f"Error saat Place Details ({place_id}): {e}")
        return None
    except Exception as e:
        print(f"Error tidak dikenal saat detail ({place_id}): {e}")
        return None

# --- FUNGSI DAPETIN URL GAMBAR (dari reference) ---
def get_photo_url(photo_reference, max_width=800):
    # Google Photos API ngasih reference, URL-nya kita bikin manual
    photo_url = f"https://maps.googleapis.com/maps/api/place/photo"
    params = {
        'photoreference': photo_reference,
        'maxwidth': max_width,
        'key': API_KEY
    }
    # Kita ga perlu request beneran, cukup return URL-nya
    # Browser yg akan load gambarnya nanti
    
    # Cara lebih canggih adalah pake library client Google, tapi ini cukup
    req = requests.Request('GET', photo_url, params=params).prepare()
    return req.url


# --- PROSES UTAMA ---
if __name__ == "__main__":
    print("Mulai mencari arena...")
    hasil_pencarian = cari_arena()
    
    dataset_final = []

    print(f"\nDitemukan {len(hasil_pencarian)} kandidat. Mendapatkan detail...")
    
    for tempat in hasil_pencarian:
        place_id = tempat.get('place_id')
        if not place_id:
            continue
            
        detail = get_detail_tempat(place_id)
        if not detail:
            continue

        # Ekstrak data yang kita mau
        nama = detail.get('name')
        lokasi = detail.get('formatted_address')
        
        # Deskripsi: Coba ambil dari editorial summary, kalo ga ada kosongin
        deskripsi = detail.get('editorial_summary', {}).get('overview', '') if detail.get('editorial_summary') else ''

        # Kapasitas: Hampir pasti GA ADA di API, kita isi None aja
        kapasitas = None 

        # Gambar: Ambil URL gambar pertama kalo ada
        url_gambar = None
        photos = detail.get('photos')
        if photos and len(photos) > 0:
            photo_ref = photos[0].get('photo_reference')
            if photo_ref:
                url_gambar = get_photo_url(photo_ref)

        data_arena = {
            "nama": nama,
            "lokasi": lokasi,
            "url_gambar": url_gambar,
            "deskripsi": deskripsi,
            "kapasitas": kapasitas
        }
        dataset_final.append(data_arena)
        
        # Kasih jeda sedikit antar request detail biar ga kena limit
        time.sleep(0.1) 

    # Simpen hasilnya ke file JSON
    print(f"\nSelesai. Menyimpan {len(dataset_final)} data arena ke {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(dataset_final, f, ensure_ascii=False, indent=2)

    print("Proses selesai.")