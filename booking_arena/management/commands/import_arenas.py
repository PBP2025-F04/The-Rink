# File: booking_arena/management/commands/import_arenas.py

import json
import re
from datetime import datetime, time
from django.core.management.base import BaseCommand
from booking_arena.models import Arena, ArenaOpeningHours

# === HELPER FUNCTION PARSING JAM (VERSI SIMPLE) ===
def parse_opening_hours_simple(text_lines, day_of_week):
    day_name_map = {0: 'Senin', 1: 'Selasa', 2: 'Rabu', 3: 'Kamis', 4: 'Jumat', 5: 'Sabtu', 6: 'Minggu'}
    target_day_name = day_name_map.get(day_of_week)
    if not text_lines or not target_day_name: return None, None
    open_time, close_time = None, None
    for line in text_lines.splitlines():
        line_stripped = line.strip()
        if line_stripped.startswith(target_day_name):
            if "Tutup" in line_stripped or "Closed" in line_stripped: return None, None
            match = re.search(r'(\d{1,2}[:.]\d{2})\s*[-–—]\s*(\d{1,2}[:.]\d{2})', line_stripped)
            if match:
                open_str = match.group(1).replace('.', ':')
                close_str = match.group(2).replace('.', ':')
                try:
                    open_time = datetime.strptime(open_str, '%H:%M').time()
                    close_time = datetime.strptime(close_str, '%H:%M').time()
                    break # Berhasil, keluar loop
                except ValueError:
                    print(f"Warning: Could not parse time format in line: '{line_stripped}'")
                    return None, None # Gagal parse, anggap tutup/error
            else: # Format jam tidak cocok
                 return None, None
    # Jika loop selesai tanpa break (misal hari ga ada di teks), return None
    return open_time, close_time
# === AKHIR HELPER FUNCTION ===

class Command(BaseCommand):
    help = 'Loads arena data from a JSON file, including parsing and saving opening hours to ArenaOpeningHours model.'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file containing arena data')

    def handle(self, *args, **options):
        file_path = options['json_file']
        self.stdout.write(f"Starting import from: {file_path}")

        self.stdout.write(self.style.WARNING('Deleting existing Arena data...'))
        Arena.objects.all().delete()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"Error: File not found at {file_path}"))
            return
        except json.JSONDecodeError:
            self.stderr.write(self.style.ERROR(f"Error: Could not decode JSON from {file_path}"))
            return
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An unexpected error occurred opening the file: {e}"))
            return

        arenas_created_count = 0
        arenas_updated_count = 0
        hours_rules_processed = 0 # Counter for processed hour rules

        # Looping setiap item data di file JSON
        for item in data:
            arena_name = item.get('nama')
            if not arena_name:
                self.stderr.write(self.style.WARNING(f"Skipping item due to missing 'nama': {item}"))
                continue

            try:
                # 1. Update atau Create Arena dulu
                arena_obj, created = Arena.objects.update_or_create(
                    name=arena_name, # Kunci pencarian adalah nama arena
                    defaults={
                        # Mapping key JSON ke field Model Arena
                        'location': item.get('lokasi', ''),
                        'description': item.get('deskripsi', ''),
                        'capacity': item.get('kapasitas') if item.get('kapasitas') is not None else 0,
                        'img_url': item.get('url_gambar'),
                        'opening_hours_text': item.get('opt hours'), # Simpan teks asli
                        'google_maps_url': item.get('link_gmaps'),
                    }
                )
                if created:
                    arenas_created_count += 1
                    self.stdout.write(f"Created Arena: {arena_name}")
                else:
                    arenas_updated_count += 1
                    # self.stdout.write(f"Updated Arena: {arena_name}") # Uncomment jika ingin log update

                # 2. Parsing dan Simpan Jam Buka per Hari ke ArenaOpeningHours
                opening_hours_text = item.get('opt hours')
                if opening_hours_text:
                    self.stdout.write(f"  Processing opening hours for {arena_name}...")
                    for day_index in range(7): # Loop dari 0 (Senin) sampai 6 (Minggu)
                        open_t, close_t = parse_opening_hours_simple(opening_hours_text, day_index)

                        # Update atau create aturan jam buka untuk hari ini
                        hour_rule, rule_created_or_updated = ArenaOpeningHours.objects.update_or_create(
                            arena=arena_obj, # Link ke Arena yang baru dibuat/diupdate
                            day=day_index,   # Hari ke- (0-6)
                            defaults={       # Data jamnya
                                'open_time': open_t,
                                'close_time': close_t
                            }
                        )
                        hours_rules_processed += 1 # Hitung setiap rule yang diproses
                        # Opsi: Print detail per hari
                        # day_name = dict(ArenaOpeningHours.DAY_CHOICES).get(day_index)
                        # self.stdout.write(f"    - {day_name}: Open={open_t}, Close={close_t}")

                else:
                    self.stdout.write(self.style.WARNING(f"  No opening hours text found for {arena_name}, skipping hours rules."))


            except Exception as e:
                # Tangani error lain saat save Arena atau ArenaOpeningHours
                self.stderr.write(self.style.ERROR(f"Error processing item '{arena_name}': {e}"))
                # Lanjut ke item berikutnya
                continue

        # Tampilkan ringkasan hasil
        self.stdout.write(self.style.SUCCESS(
            f"\nImport finished. "
            f"Arenas Created: {arenas_created_count}, Arenas Updated: {arenas_updated_count}. "
            f"Total Opening Hours Rules processed: {hours_rules_processed}."
        ))