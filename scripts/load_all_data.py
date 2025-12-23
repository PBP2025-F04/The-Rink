import os
import sys
import csv
import re
from decimal import Decimal
import tempfile
import requests
from urllib.parse import urlparse
from django.core.files import File
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'the_rink.settings')
django.setup()

from rental_gear.models import Gear
from django.contrib.auth.models import User


def clean_price(price_str):
    """Cleans price string and converts to Decimal safely"""
    if not price_str or str(price_str).strip().lower() in ('n/a', '-', ''):
        return Decimal('0.00')

    s = str(price_str).strip()

    # Hapus simbol mata uang dan huruf
    s = re.sub(r'[^\d,.\s]', '', s)

    # Ganti koma menjadi titik kalau format desimal pakai koma
    if ',' in s and '.' not in s:
        s = s.replace(',', '.')

    # Hapus semua spasi
    s = s.replace(' ', '')

    # Kalau masih ada lebih dari satu titik, hapus yang bukan desimal terakhir
    if s.count('.') > 1:
        parts = s.split('.')
        s = ''.join(parts[:-1]) + '.' + parts[-1]

    try:
        return Decimal(s)
    except Exception:
        return Decimal('0.00')


def _save_image_from_url(instance, image_url, field_name='image'):
    """Download image from URL and save to model instance's ImageField."""
    try:
        resp = requests.get(image_url, stream=True, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"Failed to download image {image_url}: {e}")
        return False

    file_name = os.path.basename(urlparse(image_url).path) or 'image'
    if not file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        file_name += '.jpg'

    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    tmp.write(chunk)
            tmp.flush()
            tmp_name = tmp.name

        with open(tmp_name, 'rb') as f:
            getattr(instance, field_name).save(file_name, File(f), save=False)

        os.unlink(tmp_name)
        return True
    except Exception as e:
        print(f"Error saving image to model: {e}")
        try:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)
        except Exception:
            pass
        return False


def load_hockey_equipment():
    print("\nLoading hockey equipment...")

    # Load hockey skates
    print("Loading hockey skates...")
    skates_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Dataset', 'hockey', 'hockey_skates.csv')
    if os.path.exists(skates_file):
        with open(skates_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    price = clean_price(row.get('Price'))
                    daily_rate = (price / Decimal('30')).quantize(Decimal('0.01'))

                    name = f"{row.get('Brand','').strip()} {row.get('Name','').strip()}".strip()
                    if len(name) > 100:
                        name = name[:97] + '...'

                    # Get or create a default seller user
                    seller, created = User.objects.get_or_create(
                        username='default_seller',
                        defaults={
                            'email': 'seller@example.com',
                            'first_name': 'Default',
                            'last_name': 'Seller'
                        }
                    )

                    image_url = row.get('Image_URL') or row.get('Image')
                    item = Gear.objects.create(
                        name=name,
                        category='hockey',
                        price_per_day=daily_rate,
                        stock=3,
                        seller=seller,
                        image_url=image_url or None,
                    )

                    # Download and save image if URL is available
                    if image_url:
                        if _save_image_from_url(item, image_url):
                            print(f"Created: {item.name} (with image)")
                        else:
                            print(f"Created: {item.name} (image download failed)")
                    else:
                        print(f"Created: {item.name}")

                    item.save()
                except Exception as e:
                    print(f"Error creating skate {row.get('Name', 'Unknown')}: {str(e)}")

    # Load hockey sticks
    print("\nLoading hockey sticks...")
    sticks_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Dataset', 'hockey', 'hockey_sticks.csv')
    if os.path.exists(sticks_file):
        with open(sticks_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    price_usd = clean_price(row.get('Price'))
                    # Konversi USD ke IDR (kurs 16000)
                    price_idr = price_usd * Decimal('16000')
                    daily_rate = (price_idr / Decimal('30')).quantize(Decimal('0'))

                    name = f"{row.get('Brand','').strip()} {row.get('Name','').strip()}".strip()
                    if len(name) > 100:
                        name = name[:97] + '...'

                    # Get or create a default seller user
                    seller, created = User.objects.get_or_create(
                        username='default_seller',
                        defaults={
                            'email': 'seller@example.com',
                            'first_name': 'Default',
                            'last_name': 'Seller'
                        }
                    )

                    image_url = row.get('Image_URL') or row.get('Image')
                    item = Gear.objects.create(
                        name=name,
                        category='hockey',
                        price_per_day=daily_rate,
                        stock=3,
                        seller=seller,
                        image_url=image_url or None,
                    )

                    # Download and save image if URL is available
                    if image_url:
                        if _save_image_from_url(item, image_url):
                            print(f"Created: {item.name} (with image)")
                        else:
                            print(f"Created: {item.name} (image download failed)")
                    else:
                        print(f"Created: {item.name}")

                    item.save()
                except Exception as e:
                    print(f"Error creating stick {row.get('Name', 'Unknown')}: {str(e)}")


def load_ice_skating_equipment():
    print("\nLoading ice skating equipment...")

    figure_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Dataset', 'figure')
    if os.path.exists(figure_dir):
        for fname in os.listdir(figure_dir):
            if fname.endswith('.csv'):
                file_path = os.path.join(figure_dir, fname)
                print(f"\nProcessing {fname}...")

                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            price_usd = clean_price(row.get('Price'))
                            # Konversi USD ke IDR (kurs 16000)
                            price_idr = price_usd * Decimal('16000')
                            daily_rate = (price_idr / Decimal('30')).quantize(Decimal('0'))

                            name = row.get('Name','').strip()
                            if row.get('Brand'):
                                name = f"{row.get('Brand').strip()} {name}"
                            if len(name) > 100:
                                name = name[:97] + '...'

                            category = 'accessories'
                            item_lower = name.lower()
                            if any(word in item_lower for word in ['skate', 'boot']):
                                category = 'ice_skating'
                            elif any(word in item_lower for word in ['pant', 'dress', 'skirt', 'legging', 'tight', 'jacket']):
                                category = 'apparel'
                            elif any(word in item_lower for word in ['protect', 'pad', 'guard']):
                                category = 'protective_gear'

                            # Get or create a default seller user
                            seller, created = User.objects.get_or_create(
                                username='default_seller',
                                defaults={
                                    'email': 'seller@example.com',
                                    'first_name': 'Default',
                                    'last_name': 'Seller'
                                }
                            )

                            image_url = row.get('Image_URL') or row.get('Image')
                            item = Gear.objects.create(
                                name=name,
                                category=category,
                                price_per_day=daily_rate,
                                stock=3,
                                seller=seller,
                                image_url=image_url or None,
                            )

                            # Download and save image if URL is available
                            if image_url:
                                if _save_image_from_url(item, image_url):
                                    print(f"Created {category}: {item.name} (with image)")
                                else:
                                    print(f"Created {category}: {item.name} (image download failed)")
                            else:
                                print(f"Created {category}: {item.name}")

                            item.save()
                        except Exception as e:
                            print(f"Error creating figure skating item {row.get('Name', 'Unknown')}: {str(e)}")


def load_curling_equipment():
    print("\nLoading curling equipment...")

    # Load curling footwear
    print("\nLoading curling footwear...")
    footwear_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Dataset', 'curling', 'curlingstore_footwear.csv')
    if os.path.exists(footwear_file):
        with open(footwear_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    price_usd = clean_price(row.get('Price'))
                    # Konversi USD ke IDR (kurs 16000)
                    price_idr = price_usd * Decimal('16000')
                    daily_rate = (price_idr / Decimal('30')).quantize(Decimal('0'))

                    name = row.get('Name','').strip()
                    if row.get('Brand'):
                        name = f"{row.get('Brand').strip()} {name}"
                    if len(name) > 100:
                        name = name[:97] + '...'

                    # Get or create a default seller user
                    seller, created = User.objects.get_or_create(
                        username='default_seller',
                        defaults={
                            'email': 'seller@example.com',
                            'first_name': 'Default',
                            'last_name': 'Seller'
                        }
                    )

                    image_url = row.get('Image_URL') or row.get('Image')
                    item = Gear.objects.create(
                        name=name,
                        category='curling',
                        price_per_day=daily_rate,
                        stock=3,
                        seller=seller,
                        image_url=image_url or None,
                    )

                    # Download and save image if URL is available
                    if image_url:
                        if _save_image_from_url(item, image_url):
                            print(f"Created: {item.name} (with image)")
                        else:
                            print(f"Created: {item.name} (image download failed)")
                    else:
                        print(f"Created: {item.name}")

                    item.save()
                except Exception as e:
                    print(f"Error creating curling footwear {row.get('Name', 'Unknown')}: {str(e)}")

    # Load curling brooms
    print("\nLoading curling brooms...")
    brooms_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Dataset', 'curling', 'curlingstore_brooms.csv')
    if os.path.exists(brooms_file):
        with open(brooms_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    price_usd = clean_price(row.get('Price'))
                    # Konversi USD ke IDR (kurs 16000)
                    price_idr = price_usd * Decimal('16000')
                    daily_rate = (price_idr / Decimal('30')).quantize(Decimal('0'))

                    name = row.get('Name','').strip()
                    if row.get('Brand'):
                        name = f"{row.get('Brand').strip()} {name}"
                    if len(name) > 100:
                        name = name[:97] + '...'

                    # Get or create a default seller user
                    seller, created = User.objects.get_or_create(
                        username='default_seller',
                        defaults={
                            'email': 'seller@example.com',
                            'first_name': 'Default',
                            'last_name': 'Seller'
                        }
                    )

                    image_url = row.get('Image_URL') or row.get('Image')
                    item = Gear.objects.create(
                        name=name,
                        category='curling',
                        price_per_day=daily_rate,
                        stock=3,
                        seller=seller,
                        image_url=image_url or None,
                    )

                    # Download and save image if URL is available
                    if image_url:
                        if _save_image_from_url(item, image_url):
                            print(f"Created: {item.name} (with image)")
                        else:
                            print(f"Created: {item.name} (image download failed)")
                    else:
                        print(f"Created: {item.name}")

                    item.save()
                except Exception as e:
                    print(f"Error creating curling broom {row.get('Name', 'Unknown')}: {str(e)}")


if __name__ == '__main__':
    # Clear existing data
    print('Clearing existing items from database...')
    Gear.objects.all().delete()

    # Load all equipment by category
    load_hockey_equipment()
    load_ice_skating_equipment()
    load_curling_equipment()

    # Print summary
    print('\nData loading completed!')
    print('\nItems by category:')
    for category in ['hockey', 'ice_skating', 'curling', 'apparel', 'accessories', 'protective_gear']:
        count = Gear.objects.filter(category=category).count()
        print(f"{category}: {count} items")