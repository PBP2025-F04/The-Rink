import csv
import os
from decimal import Decimal
from urllib.parse import urlparse
from urllib.request import urlretrieve
from django.core.management.base import BaseCommand
from django.core.files import File
from rental_gear.models import Gear
from django.conf import settings
import tempfile

class Command(BaseCommand):
    help = 'Import gear data from CSV files'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The CSV file to import')
        parser.add_argument('category', type=str, help='The category of gear (hockey, curling, ice_skating)')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        category = kwargs['category']

        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Convert price string to decimal and calculate daily rate
                price_str = row['Price'].replace('$', '').replace(',', '')
                try:
                    price = Decimal(price_str)
                    daily_rate = (price / Decimal('30')).quantize(Decimal('0.01'))  # Monthly price divided by 30
                except:
                    self.stdout.write(self.style.WARNING(f'Invalid price format for {row["Name"]}, skipping...'))
                    continue

                # Create gear name from brand and name
                name = f"{row['Brand']} {row['Name']}"
                if len(name) > 100:
                    name = name[:97] + '...'

                # Create gear object
                gear = Gear(
                    name=name,
                    category=category,
                    price_per_day=daily_rate,
                    size='Standard',  # Default size since not provided in CSV
                    stock=5  # Default stock value
                )

                # Handle image download and save
                image_url = row.get('Image_URL')
                if image_url:
                    try:
                        # Get file name from URL
                        img_temp = tempfile.NamedTemporaryFile(delete=True)
                        img_temp.close()
                        
                        # Download the image
                        filename = os.path.basename(urlparse(image_url).path)
                        if not filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                            filename += '.jpg'
                        
                        urlretrieve(image_url, img_temp.name)
                        
                        # Save the image
                        with open(img_temp.name, 'rb') as img_file:
                            gear.image.save(filename, File(img_file), save=False)
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'Failed to download image for {name}: {str(e)}'))

                try:
                    gear.save()
                    self.stdout.write(self.style.SUCCESS(f'Successfully imported {name}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Failed to save {name}: {str(e)}'))