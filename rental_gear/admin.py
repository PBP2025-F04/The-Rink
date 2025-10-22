from django.contrib import admin
from .models import Gear, CartItem, Rental, RentalItem

@admin.register(Gear)
class GearAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'size', 'price_per_day', 'stock')
    list_filter = ('category',)
    search_fields = ('name',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'gear', 'quantity')

@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'user', 'rental_date', 'return_date', 'total_cost')

@admin.register(RentalItem)
class RentalItemAdmin(admin.ModelAdmin):
    list_display = ('rental', 'gear_name', 'quantity', 'price_per_day_at_checkout')
