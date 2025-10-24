from django.forms import ModelForm
from booking_arena.models import Arena, TimeSlot, Booking

class ArenaForm(ModelForm):
    class Meta:
        model = Arena
        fields = ["name", "description", "capacity", "location", "img"]

class TimeSlotForm(ModelForm):
    class Meta:
        model = TimeSlot
        fields = ["day", "start_time", "end_time", "is_avalaible"]

class BookingForm(ModelForm):
    class Meta:
        model = Booking
        fields = ["user", "time_slot", "date", "status"]
