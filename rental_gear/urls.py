from django.urls import path
from rental_gear.views import (
    catalog, filter_gear, view_cart, add_to_cart, remove_from_cart,
    add_to_cart_ajax, remove_from_cart_ajax, checkout_ajax, gear_detail,
    checkout, create_gear, update_gear, delete_gear, gear_json
)

app_name = 'rental_gear'

urlpatterns = [
    # API URLs
    path('api/gear/<int:id>/', gear_detail, name='gear_api_detail'),
    path('gear/<int:id>/json/', gear_json, name='gear_json'),
    # Admin CRUD URLs
    path('gear/add/', create_gear, name='create_gear'),
    path('gear/<int:id>/edit/', update_gear, name='update_gear'),
    path('gear/<int:id>/delete/', delete_gear, name='delete_gear'),
    path('', catalog, name='catalog'),
    path('filter/', filter_gear, name='filter_gear'),
    path('cart/', view_cart, name='view_cart'),
    path('cart/add/<int:gear_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/add-ajax/<int:gear_id>/', add_to_cart_ajax, name='add_to_cart_ajax'),
    path('cart/remove-ajax/<int:item_id>/', remove_from_cart_ajax, name='remove_from_cart_ajax'),
    path('checkout-ajax/', checkout_ajax, name='checkout_ajax'),
    path('gear/<int:id>/', gear_detail, name='gear_detail'),
    path('checkout/', checkout, name='checkout'),
]
