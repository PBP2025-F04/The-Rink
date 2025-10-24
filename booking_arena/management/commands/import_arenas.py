import json
from django.core.management.base import BaseCommand
from booking_arena.models import Arena

class Command(BaseCommand):
    help = 'Loads arena data from a JSON file into the database'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file')

    def handle(self, *args, **options):
        file_path = options['json_file']

        self.stdout.write(self.style.WARNING('Deleting existing Arena data...'))
        Arena.objects.all().delete()

        self.stdout.write(f"Loading data from {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File not found: {file_path}"))
            return
        except json.JSONDecodeError:
            self.stderr.write(self.style.ERROR(f"Error decoding JSON from {file_path}"))
            return

        arenas_created_count = 0
        arenas_updated_count = 0

        for item in data:
            arena_obj, created = Arena.objects.update_or_create(
                name=item.get('nama'),
                defaults={
                    'location': item.get('lokasi', ''),
                    'description': item.get('deskripsi', ''),
                    'capacity': item.get('kapasitas') if item.get('kapasitas') is not None else 0,
                    'img_url': item.get('url_gambar'), 
                    'opening_hours_text': item.get('opt hours'),
                    'google_maps_url': item.get('map url'),
                }
            )

            if created:
                arenas_created_count += 1
            else:
                arenas_updated_count += 1

            # self.stdout.write(f"{'Created' if created else 'Updated'} arena: {arena_obj.name}")

        self.stdout.write(self.style.SUCCESS(
            f"Successfully loaded data. Created: {arenas_created_count}, Updated: {arenas_updated_count}"
        ))