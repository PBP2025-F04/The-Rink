from django.contrib import admin
from .models import Arena, Booking


@admin.register(Arena)
class ArenaAdmin(admin.ModelAdmin):
	list_display = ('name', 'location', 'capacity')
	search_fields = ('name', 'location')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
	list_display = ('arena', 'user', 'date', 'start_time', 'end_time', 'status')
	list_filter = ('status', 'date')
	search_fields = ('arena__name', 'user__username')
