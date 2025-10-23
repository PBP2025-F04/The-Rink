from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
import uuid

class Arena(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    capacity = models.IntegerField()
    location = models.CharField(max_length=200)
    img = models.ImageField(upload_to='arena_images/', null=True, blank=True)

    def __str__(self):
        return self.name

class TimeSlot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    DAY_CHOICES = (
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'),
        (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
    )
    arena = models.ForeignKey(Arena, on_delete=models.CASCADE, related_name='time_slot')
    day = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_avalaible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.arena.name} - {self.day} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"

class Booking(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = (
        ('Booked', 'Booked'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, null=True)
    date = models.DateField()
    booked_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Booked')

    class Meta:
        # Mencegah double book untuk slot & tanggal yang sama
        unique_together = ('time_slot', 'date')

    def __str__(self):
        return f"{self.user.username} @ {self.time_slot} on {self.date}"