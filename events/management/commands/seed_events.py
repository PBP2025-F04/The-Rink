import csv
import os
from django.core.management.base import BaseCommand
from events.models import Event
from django.utils.text import slugify
from datetime import datetime

class Command(BaseCommand):
    help = 'Inject event data from CSV to Database (Works on PWS)'

    def handle(self, *args, **kwargs):
        # Cari file CSV di root project
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        csv_file = os.path.join(base_dir, 'initial_events_data.csv')

        # Fallback jika path beda di server tertentu
        if not os.path.exists(csv_file):
             csv_file = 'initial_events_data.csv'

        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f'File csv tidak ditemukan di: {csv_file}'))
            return

        self.stdout.write(self.style.SUCCESS(f'Membaca data dari {csv_file}...'))

        events_created = 0
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                try:
                    # 1. Generate Slug Otomatis
                    slug = slugify(row['name'])
                    
                    # 2. Parsing Tanggal & Waktu
                    date_obj = datetime.strptime(row['date'], '%Y-%m-%d').date()
                    start_time_obj = datetime.strptime(row['start_time'], '%H:%M').time()
                    end_time_obj = datetime.strptime(row['end_time'], '%H:%M').time()

                    # 3. Simpan ke Database (Update jika ada, Create jika belum)
                    # Kita pakai update_or_create biar kalau di-run 2x tidak duplikat
                    event, created = Event.objects.update_or_create(
                        name=row['name'],
                        defaults={
                            'slug': slug,
                            'category': row['category'],
                            'level': row['level'],
                            'description': row['description'],
                            'requirements': row.get('requirements', ''),
                            'date': date_obj,
                            'start_time': start_time_obj,
                            'end_time': end_time_obj,
                            'location': row['location'],
                            'price': float(row['price']),
                            'max_participants': int(row['max_participants']),
                            'organizer': row.get('organizer', ''),
                            'instructor': row.get('instructor', ''),
                            'is_active': True,
                            # Image dibiarkan kosong atau default
                        }
                    )
                    
                    action = "Created" if created else "Updated"
                    self.stdout.write(f"{action}: {event.name}")
                    events_created += 1

                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Gagal memproses baris {row.get('name')}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS(f'Selesai! {events_created} events berhasil diproses.'))