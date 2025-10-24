import os
import sys
import csv
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'the_rink.settings')
django.setup()

from rental_gear.models import Gear

def clean_price(price_str):
    """Removes 'USD ' prefix and converts to decimal"""
    return float(price_str.replace('USD ', ''))

def get_category(item_name, description):
    """Determine the appropriate category based on item details"""
    name_lower = item_name.lower()
    desc_lower = description.lower() if description else ""
    
    if any(word in name_lower for word in ['tights', 'socks', 'gloves']):
        return 'accessories'
    elif any(word in name_lower for word in ['guard', 'protective']):
        return 'protective_gear'
    elif any(word in name_lower for word in ['jacket', 'dress', 'outfit', 'pants', 'vest']):
        return 'apparel'
    else:
        return 'accessories'  # Default to accessories since most remaining items are accessories

def load_figure_skating_apparel():
    print("\nStarting to load items...")
    with open('../Dataset/figure/figure_skating_apparel.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            category = get_category(row['Name'], row['Description'])
            try:
                item = Gear.objects.create(
                    name=row['Name'],
                    category=category,
                    price_per_day=clean_price(row['Price']) / 10,  # Daily rental price is 1/10 of purchase price
                    size='One Size',  # Default size since apparel data doesn't include sizes
                    stock=5,  # Default stock of 5 units per item
                    image=row['Image_URL']
                )
                print(f"Created: {item.name} (Category: {category})")
            except Exception as e:
                print(f"Error creating item {row['Name']}: {str(e)}")

if __name__ == '__main__':
    print('Clearing existing figure skating items...')
    Gear.objects.filter(category__in=['apparel', 'accessories', 'protective_gear', 'other']).delete()
    
    print('Loading Figure Skating Apparel data...')
    load_figure_skating_apparel()
    
    print('\nData loading completed!')
    print('\nItems by category:')
    categories = ['apparel', 'accessories', 'protective_gear', 'other']
    for category in categories:
        count = Gear.objects.filter(category=category).count()
        print(f'- {category.replace("_", " ").title()}: {count} items')