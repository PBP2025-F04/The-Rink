# events/migrations/XXXX_seed_dummy_data.py
from django.db import migrations
from django.utils.text import slugify
import datetime

def create_dummy_events(apps, schema_editor):
    """
    Membuat data event dummy untuk The Rink.
    """
    Event = apps.get_model('events', 'Event')
    
    dummy_data = [
        {
            'name': 'Beginner Hockey Clinic',
            'category': 'workshop',
            'level': 'beginner',
            'description': 'Learn the fundamentals of hockey! This clinic covers skating, stickhandling, passing, and shooting. Full gear is required. Our certified instructors will guide you every step of the way.',
            'requirements': 'Full hockey gear (helmet, skates, gloves, pads, stick). Skate rentals available.',
            'date': datetime.date(2025, 11, 15),
            'start_time': datetime.time(9, 0, 0),
            'end_time': datetime.time(11, 0, 0),
            'price': 150000.00,
            'max_participants': 25,
            'instructor': 'Coach Budi Santoso'
        },
        {
            'name': 'Friday Night Open Skate',
            'category': 'social',
            'level': 'all',
            'description': 'Join us for our weekly Friday Night Open Skate! Bring your friends, family, or a date and enjoy skating under the lights with a live DJ playing top hits. All skill levels are welcome.',
            'requirements': 'Skates required. Rentals available.',
            'date': datetime.date(2025, 11, 14),
            'start_time': datetime.time(19, 0, 0),
            'end_time': datetime.time(22, 0, 0),
            'price': 75000.00,
            'max_participants': 100,
            'organizer': 'The Rink'
        },
        {
            'name': 'Regional Figure Skating Competition',
            'category': 'competition',
            'level': 'advanced',
            'description': 'The Rink is proud to host the annual Regional Figure Skating Competition. Watch top athletes from across the region compete in freestyle, pairs, and ice dance categories. Spectator tickets are available now!',
            'requirements': 'For registered competitors only. Spectator tickets required for viewing.',
            'date': datetime.date(2025, 11, 22),
            'start_time': datetime.time(8, 0, 0),
            'end_time': datetime.time(18, 0, 0),
            'price': 50000.00,
            'max_participants': 200,
            'organizer': 'Regional Skating Association'
        },
        {
            'name': 'Intermediate Power Skating',
            'category': 'training',
            'level': 'intermediate',
            'description': 'Take your skating to the next level. This training session focuses on edge control, speed, agility, and power. Designed for hockey players and figure skaters who have mastered the basics.',
            'requirements': 'Must be able to skate forwards, backwards, and stop comfortably.',
            'date': datetime.date(2025, 11, 18),
            'start_time': datetime.time(18, 0, 0),
            'end_time': datetime.time(19, 30, 0),
            'price': 200000.00,
            'max_participants': 20,
            'instructor': 'Coach Maria Lee'
        },
        {
            'name': 'Holiday Ice Show',
            'category': 'social',
            'level': 'all',
            'description': 'Celebrate the holiday season with us! A magical performance by our local skating club, featuring festive music, dazzling costumes, and special guest skaters. A perfect event for the whole family.',
            'requirements': 'None. Just bring your holiday spirit!',
            'date': datetime.date(2025, 12, 20),
            'start_time': datetime.time(17, 0, 0),
            'end_time': datetime.time(19, 0, 0),
            'price': 100000.00,
            'max_participants': 150,
            'organizer': 'The Rink Skating Club'
        }
    ]
    
    for item in dummy_data:
        # Buat slug unik jika diperlukan
        base_slug = slugify(item['name'])
        slug = base_slug
        counter = 1
        while Event.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        Event.objects.create(
            name=item['name'],
            slug=slug,
            category=item['category'],
            level=item['level'],
            description=item['description'],
            requirements=item['requirements'],
            date=item['date'],
            start_time=item['start_time'],
            end_time=item['end_time'],
            price=item['price'],
            max_participants=item['max_participants'],
            organizer=item.get('organizer', ''),
            instructor=item.get('instructor', ''),
            is_active=True
        )

def delete_dummy_events(apps, schema_editor):
    # Ini opsional, tapi bagus untuk 'un-migrate'
    Event = apps.get_model('events', 'Event')
    Event.objects.filter(instructor__icontains='Coach').delete()
    Event.objects.filter(organizer__icontains='The Rink').delete()
    Event.objects.filter(organizer__icontains='Association').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_alter_event_category_remove_packagebooking_package_and_more'), 
    ]

    operations = [
        migrations.RunPython(create_dummy_events, delete_dummy_events),
    ]