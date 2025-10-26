from django.urls import path
from forum import views
from rental_gear.views import (
    catalog, filter_gear, view_cart, add_to_cart, remove_from_cart,
    add_to_cart_ajax, remove_from_cart_ajax, checkout_ajax, gear_detail,
    checkout, create_gear, update_gear, delete_gear, gear_json,
    admin_gear_list, admin_gear_create, admin_gear_update, admin_gear_delete
)

app_name = 'rental_gear'

urlpatterns = [
    # API URLs
    path('api/gear/<int:id>/', gear_detail, name='gear_api_detail'),
    path('gear/<int:id>/json/', gear_json, name='gear_json'),
    # Admin CRUD URLs
    path('admin/gear/', admin_gear_list, name='admin_gear_list'),
    path('admin/gear/add/', admin_gear_create, name='admin_gear_create'),
    path('admin/gear/<int:id>/edit/', admin_gear_update, name='admin_gear_update'),
    path('admin/gear/<int:id>/delete/', admin_gear_delete, name='admin_gear_delete'),
    path('gear/add/', create_gear, name='create_gear'),
    path('gear/<int:id>/edit/', update_gear, name='update_gear'),
    path('gear/<int:id>/delete/', delete_gear, name='delete_gear'),
    path('', catalog, name='catalog'),
    path('filter/', filter_gear, name='filter_gear'),
    path('community/', views.show_forum, name='show_forum'),
    path('cart/', view_cart, name='view_cart'),
    path('cart/add/<int:gear_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/add-ajax/<int:gear_id>/', add_to_cart_ajax, name='add_to_cart_ajax'),
    path('cart/remove-ajax/<int:item_id>/', remove_from_cart_ajax, name='remove_from_cart_ajax'),
    path('checkout-ajax/', checkout_ajax, name='checkout_ajax'),
    path('gear/<int:id>/', gear_detail, name='gear_detail'),
    path('checkout/', checkout, name='checkout'),
]
