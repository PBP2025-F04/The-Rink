import os
import sys
import csv
from decimal import Decimal
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'the_rink.settings')
django.setup()

from rental_gear.models import Gear

def clean_price(price_str):
    """Removes $ and commas, converts to decimal"""
    return Decimal(price_str.replace('$', '').replace(',', ''))

def load_hockey_skates():
    print("\nLoading hockey skates data...")
    skates_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Dataset', 'hockey', 'hockey_skates.csv')
    
    with open(skates_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                # Calculate daily rental rate (1/30 of purchase price)
                price = clean_price(row['Price'])
                daily_rate = (price / Decimal('30')).quantize(Decimal('0.01'))
                
                # Create gear name from brand and name 
                name = f"{row['Brand']} {row['Name']}"
                if len(name) > 100:
                    name = name[:97] + '...'

                item = Gear.objects.create(
                    name=name,
                    category='hockey',
                    price_per_day=daily_rate,
                    size='Standard',  # You may want to extract size if available in data
                    stock=3,  # Default stock
                    image=row['Image_URL']
                )
                print(f"Created: {item.name}")
            except Exception as e:
                print(f"Error creating item {row.get('Name', 'Unknown')}: {str(e)}")

def load_hockey_sticks():
    print("\nLoading hockey sticks data...")
    sticks_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Dataset', 'hockey', 'hockey_sticks.csv')
    
    with open(sticks_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                # Calculate daily rental rate (1/30 of purchase price)
                price = clean_price(row['Price'])
                daily_rate = (price / Decimal('30')).quantize(Decimal('0.01'))
                
                # Create gear name from brand and name
                name = f"{row['Brand']} {row['Name']}"
                if len(name) > 100:
                    name = name[:97] + '...'

                item = Gear.objects.create(
                    name=name,
                    category='hockey',
                    price_per_day=daily_rate,
                    size='Standard',  # You may want to extract size if available
                    stock=3,  # Default stock
                    image=row['Image_URL']
                )
                print(f"Created: {item.name}")
            except Exception as e:
                print(f"Error creating item {row.get('Name', 'Unknown')}: {str(e)}")

if __name__ == '__main__':
    print('Clearing existing hockey items...')
    Gear.objects.filter(category='hockey').delete()
    
    print('Loading Hockey Equipment data...')
    load_hockey_skates()
    load_hockey_sticks()
    
    print('\nData loading completed!')
    print('\nHockey items loaded:', Gear.objects.filter(category='hockey').count())