import os
import sys
import importlib.util
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'the_rink.settings')
django.setup()

# Import the robust loader module (scripts/load_all_data.py) dynamically
loader_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'load_all_data.py')
spec = importlib.util.spec_from_file_location('load_all_data', loader_path)
load_all_data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(load_all_data)

if __name__ == '__main__':
    print('Running the improved ice skating loader from scripts/load_all_data.py')
    # Call only the ice skating loader so we don't clear or modify other categories
    load_all_data.load_ice_skating_equipment()
    print('\nIce skating data load complete.')