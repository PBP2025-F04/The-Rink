from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify 
import datetime

class Event(models.Model):
    CATEGORY_CHOICES = [
        ('competition', 'Competition'),
        ('workshop', 'Workshop'),
        ('social', 'Social Event'),
        ('training', 'Training Session'),
    ]
    
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('all', 'All Levels'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='social')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='all')
    description = models.TextField()
    requirements = models.TextField(blank=True, null=True)
    
    date = models.DateField(default=timezone.now)
    start_time = models.TimeField(default=datetime.time(9, 0))
    end_time = models.TimeField(default=datetime.time(17, 0))
    location = models.CharField(max_length=100, default="Main Arena")
    
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_participants = models.IntegerField(default=30)
    
    organizer = models.CharField(max_length=200, blank=True, null=True)
    instructor = models.CharField(max_length=200, blank=True, null=True)
    
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return self.name
    
    @property
    def current_participants(self):
        # Diubah: Menggunakan related_name 'registrations' dari EventRegistration
        return self.registrations.count()
    
    @property
    def is_full(self):
        return self.current_participants >= self.max_participants
    
    @property
    def spots_left(self):
        return self.max_participants - self.current_participants
    
    @property
    def is_past(self):
        return self.date < timezone.now().date()
    
    def is_registered(self, user):
        if user.is_authenticated:
            # Diubah: Mengecek ke model EventRegistration
            return self.registrations.filter(user=user).exists()
        return False


class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    registered_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['event', 'user']
        ordering = ['-registered_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.event.name}"