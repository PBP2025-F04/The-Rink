from django.contrib import admin

# Register your models here.
from django.contrib import admin
from booking_arena.models import Arena, TimeSlot, Booking

@admin.register(Arena)
class ArenaAdmin(admin.ModelAdmin):
	list_display = ('name', 'location', 'capacity')
	search_fields = ('name', 'location')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
	list_display = ('user', 'date', 'time_slot', 'booked_at', 'status')
	list_filter = ('user', 'status', 'date')
	search_fields = ('arena__name', 'user__username')

admin.site.register(TimeSlot)
