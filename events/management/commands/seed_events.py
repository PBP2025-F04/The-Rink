from django.core.management.base import BaseCommand
from events.models import Event  # Ganti 'events' kalau nama app lo beda (misal 'main')
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Inject dummy data for The Rink events'

    def handle(self, *args, **kwargs):
        # Data Dummy
        events_data = [
            {
                "name": "Winter Wonderland Gala",
                "description": "Dansa di atas es dengan lampu aurora.",
                "date": "2024-12-24",
                "start_time": "19:00",
                "location": "Grand Ice Hall",
                "price": 150000,
                "category": "social",
                "max_participants": 100,
            },
            {
                "name": "Pro Hockey: Bears vs Lions",
                "description": "Pertandingan sengit liga nasional.",
                "date": "2024-12-28",
                "start_time": "18:30",
                "location": "Main Stadium",
                "price": 75000,
                "category": "competition",
                "max_participants": 500,
            },
            {
                "name": "Intro to Figure Skating",
                "description": "Kelas pemula khusus dewasa.",
                "date": "2024-12-26",
                "start_time": "10:00",
                "location": "Rink B",
                "price": 200000,
                "category": "workshop",
                "max_participants": 15,
            },
            {
                "name": "Kids Frozen Adventure",
                "description": "Sesi khusus anak-anak.",
                "date": "2024-12-30",
                "start_time": "09:00",
                "location": "Kids Area",
                "price": 50000,
                "category": "social",
                "max_participants": 30,
            },
            {
                "name": "Speed Skating Qualifier",
                "description": "Babak kualifikasi atlet.",
                "date": "2025-01-02",
                "start_time": "08:00",
                "location": "Oval Track",
                "price": 25000,
                "category": "competition",
                "max_participants": 50,
            }
        ]

        self.stdout.write("--- MULAI INJECT DATA ---")

        for item in events_data:
            slug_candidate = slugify(item["name"])
            
            if not Event.objects.filter(slug=slug_candidate).exists():
                Event.objects.create(
                    name=item["name"],
                    slug=slug_candidate,
                    description=item["description"],
                    date=item["date"],
                    start_time=item["start_time"],
                    location=item["location"],
                    price=item["price"],
                    category=item["category"],
                    max_participants=item["max_participants"],
                    image=None,
                    is_active=True
                )
                self.stdout.write(self.style.SUCCESS(f"[OK] Created: {item['name']}"))
            else:
                self.stdout.write(self.style.WARNING(f"[SKIP] Exists: {item['name']}"))

        self.stdout.write(self.style.SUCCESS("--- SELESAI ---"))