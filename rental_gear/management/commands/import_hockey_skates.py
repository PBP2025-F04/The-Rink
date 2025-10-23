import csv
import os
from django.core.management.base import BaseCommand
from rental_gear.models import Gear
from django.core.files import File
from django.conf import settings
import requests
from urllib.parse import urlparse
from pathlib import Path

class Command(BaseCommand):
    help = 'Import hockey skates data from CSV file'

    def handle(self, *args, **options):
        # Path ke file CSV
        csv_file = os.path.join(settings.BASE_DIR, 'Dataset', 'hockey_skates_all.csv')
        
        # Buat direktori untuk menyimpan gambar jika belum ada
        media_root = os.path.join(settings.MEDIA_ROOT, 'gears')
        if not os.path.exists(media_root):
            os.makedirs(media_root)

        with open(csv_file, encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Bersihkan data harga
                price_str = row['Price'].replace('$', '').replace(',', '')
                price = float(price_str)

                # Download dan simpan gambar
                image_url = row['Image_URL']
                image_filename = None
                if image_url:
                    try:
                        # Ambil nama file dari URL
                        parsed_url = urlparse(image_url)
                        image_filename = os.path.basename(parsed_url.path)
                        image_path = os.path.join(media_root, image_filename)

                        # Download gambar jika belum ada
                        if not os.path.exists(image_path):
                            response = requests.get(image_url)
                            if response.status_code == 200:
                                with open(image_path, 'wb') as image_file:
                                    image_file.write(response.content)
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Error downloading image for {row["Name"]}: {str(e)}'))

                # Buat atau update item di database
                gear, created = Gear.objects.get_or_create(
                    name=row['Name'],
                    defaults={
                        'category': 'ice_skating',  # karena ini hockey skates
                        'size': 'Standard',  # bisa disesuaikan jika ada informasi size
                        'price_per_day': price / 30,  # Harga per hari (dibagi 30 dari harga penuh)
                        'stock': 5,  # default stock
                        'image': f'gears/{image_filename}' if image_filename else None
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f'Successfully created gear "{row["Name"]}"'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Successfully updated gear "{row["Name"]}"'))

        self.stdout.write(self.style.SUCCESS('Data import completed successfully'))