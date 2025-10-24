from django.db import models
from django.contrib.auth.models import User

class Gear(models.Model):
    CATEGORY_CHOICES = [
        ('hockey', 'Hockey'),
        ('curling', 'Curling'),
        ('apparel', 'Apparel'),
        ('accessories', 'Accessories'),
        ('protective_gear', 'Protective Gear'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price_per_day = models.DecimalField(max_digits=8, decimal_places=2)
    image_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)
    stock = models.PositiveIntegerField(default=1)
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gear = models.ForeignKey(Gear, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    days = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        return self.gear.price_per_day * self.quantity * self.days


class Rental(models.Model):
    customer_name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    rental_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class RentalItem(models.Model): #Buat simpan detail gear yang di rental
    rental = models.ForeignKey(Rental, related_name='items', on_delete=models.CASCADE)
    gear_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    price_per_day_at_checkout = models.DecimalField(max_digits=8, decimal_places=2)

    def get_subtotal(self):
        return self.price_per_day_at_checkout * self.quantity
