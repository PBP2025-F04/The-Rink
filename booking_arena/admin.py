# Register your models here.
from django.contrib import admin
from booking_arena.models import Arena, Booking, ArenaOpeningHours

class ArenaOpeningHoursInline(admin.TabularInline):
	model = ArenaOpeningHours
	extra = 7
	max_num = 7
	can_delete = False
	fields = ('day', 'open_time', 'close_time')

@admin.register(ArenaOpeningHours)
class ArenaOpeningHoursAdmin(admin.ModelAdmin):
	list_display = ('arena', 'get_day_display', 'open_time', 'close_time')
	list_filter = ('arena', 'day')
	search_fields = ('arena__name',)

@admin.register(Arena)
class ArenaAdmin(admin.ModelAdmin):
	list_display = ('name', 'location', 'capacity')
	search_fields = ('name', 'location')
	inlines = [ArenaOpeningHoursInline]

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
	list_display = ('user', 'date', 'display_hour', 'booked_at', 'status', 'activity')
	list_filter = ('user', 'status', 'arena', 'date', 'activity')
	search_fields = ('arena__name', 'user__username', 'activity')
	ordering = ('-date', '-start_hour')

	def display_hour(self, obj):
		return f"{obj.start_hour:02d}"
	display_hour.short_description = 'Start Time'
