from rest_framework import serializers
from .models import Arena, ArenaOpeningHours, Booking
from django.contrib.auth.models import User

# --- USER SERIALIZER ---
# Kita butuh ini biar frontend tau nama yang booking siapa
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

# --- ARENA & OPENING HOURS ---
class ArenaOpeningHoursSerializer(serializers.ModelSerializer):
    day_display = serializers.CharField(source='get_day_display', read_only=True)
    
    class Meta:
        model = ArenaOpeningHours
        fields = ['id', 'day', 'day_display', 'open_time', 'close_time']

class ArenaSerializer(serializers.ModelSerializer):
    # Nested serializer biar pas fetch Arena, jam bukanya langsung kebawa
    opening_hours_rules = ArenaOpeningHoursSerializer(many=True, read_only=True)
    
    class Meta:
        model = Arena
        fields = [
            'id', 'name', 'description', 'capacity', 'location', 
            'img_url', 'opening_hours_text', 'google_maps_url',
            'opening_hours_rules' 
        ]

# --- BOOKING SERIALIZER ---
class BookingSerializer(serializers.ModelSerializer):
    # ReadOnly: Kita cuma mau nampilin info user, bukan ngedit user lewat sini
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'arena', 'user', 'user_details', 
            'date', 'start_hour', 'booked_at', 
            'status', 'activity'
        ]
        read_only_fields = ['user', 'booked_at', 'status']

    # Validasi biar gak tabrakan slot (Optional, karena unique_together udah handle, tapi ini lebih rapi error-nya)
    def validate(self, data):
        # Cek apakah slot ini udah ada yang booking & statusnya bukan Cancelled
        existing = Booking.objects.filter(
            arena=data['arena'],
            date=data['date'],
            start_hour=data['start_hour']
        ).exclude(status='Cancelled')
        
        if existing.exists():
            raise serializers.ValidationError("Slot ini sudah dibooking orang lain, bro.")
            
        return data