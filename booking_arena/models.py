from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
import uuid

class Arena(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    capacity = models.IntegerField()
    location = models.CharField(max_length=200)
    img_url = models.URLField(max_length=500, null=True, blank=True)
    opening_hours_text = models.TextField(null=True, blank=True)
    google_maps_url = models.URLField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name
    
class ArenaOpeningHours(models.Model):
    arena = models.ForeignKey(Arena, on_delete=models.CASCADE, related_name='opening_hours_rules')
    DAY_CHOICES = ((0, 'Monday'), 
                   (1, 'Tuesday'), 
                   (2, 'Wednesday'), 
                   (3, 'Thursday'),
                   (4, 'Friday'), 
                   (5, 'Saturday'), 
                   (6, 'Sunday')
    )
    day = models.IntegerField(choices=DAY_CHOICES)
    open_time = models.TimeField(null=True, blank=True)
    close_time = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ('arena', 'day') # Satu aturan per hari per arena
        ordering = ['arena', 'day'] # Urutkan
        verbose_name = "Opening Hour Rule" # Nama yg bagus di admin
        verbose_name_plural = "Opening Hours Rules" # Nama jamak yg bagus

    def __str__(self):
        if self.open_time and self.close_time:
            return f"{self.arena.name} - {self.get_day_display()}: {self.open_time.strftime('%H:%M')} - {self.close_time.strftime('%H:%M')}"
        else:
            return f"{self.arena.name} - {self.get_day_display()}: Closed"

class Booking(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    arena = models.ForeignKey(Arena, on_delete=models.CASCADE, related_name='bookings')
    STATUS_CHOICES = (
        ('Booked', 'Booked'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
    )
    ACTIVITY_CHOICES = (
        ('ice_skating', 'Ice Skating'),
        ('ice_hockey', 'Ice Hockey'),
        ('curling', 'Curling'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    date = models.DateField()
    start_hour = models.IntegerField()
    booked_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Booked')
    activity = models.CharField(max_length=50, choices=ACTIVITY_CHOICES, blank=True, null=True)

    class Meta:
        # Mencegah double book untuk slot & tanggal yang sama
        unique_together = ('arena', 'date', 'start_hour')

    def __str__(self):
        return f"{self.user.username} @ {self.arena.name} on {self.date} ({self.start_hour:02d}:00)"