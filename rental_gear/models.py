from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User 

class Gear(models.Model):
    CATEGORY_CHOICES = [
        ('hockey', 'Hockey'),
        ('curling', 'Curling'),
        ('ice_skating', 'Ice Skating'),
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    size = models.CharField(max_length=10)
    price_per_day = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='gears/', blank=True, null=True)

    def __str__(self):
        return self.name


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gear = models.ForeignKey(Gear, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        return self.gear.price * self.quantity




class Rental(models.Model):
    customer_name = models.CharField(max_length=100)
    items = models.ManyToManyField(CartItem)
    rental_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateField()

    def total_cost(self):
        return sum(item.total_price() for item in self.items.all())
