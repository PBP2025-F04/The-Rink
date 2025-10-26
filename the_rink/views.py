from django.shortcuts import render
from rental_gear.models import Gear

def main_page(request):
    gears = Gear.objects.filter(is_featured=True)
    return render(request, 'main.html', {'gears': gears})
