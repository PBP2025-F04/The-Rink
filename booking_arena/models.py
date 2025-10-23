from django.db import models
from django.conf import settings


class Arena(models.Model):
	name = models.CharField(max_length=150)
	location = models.CharField(max_length=200, blank=True)
	capacity = models.PositiveIntegerField(default=0)
	description = models.TextField(blank=True)
	image = models.ImageField(upload_to='arenas/', blank=True, null=True)

	def __str__(self):
		return self.name


class Booking(models.Model):
	STATUS_CHOICES = (
		('pending', 'Pending'),
		('confirmed', 'Confirmed'),
		('cancelled', 'Cancelled'),
	)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	arena = models.ForeignKey(Arena, on_delete=models.CASCADE)
	date = models.DateField()
	start_time = models.TimeField()
	end_time = models.TimeField()
	created_at = models.DateTimeField(auto_now_add=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

	def __str__(self):
		return f"{self.arena.name} - {self.user.username} on {self.date} {self.start_time}" 
