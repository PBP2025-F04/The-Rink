from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Arena, TimeSlot, Booking

admin.site.register(Arena)
admin.site.register(TimeSlot)
admin.site.register(Booking)

