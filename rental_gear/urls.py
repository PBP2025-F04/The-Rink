from django.urls import path
from forum import views
from rental_gear.views import (
    catalog, filter_gear, view_cart, add_to_cart, remove_from_cart,
    add_to_cart_ajax, remove_from_cart_ajax, checkout_ajax, gear_detail,
    checkout, create_gear, update_gear, delete_gear, gear_json,
    admin_gear_list, admin_gear_create, admin_gear_update, admin_gear_delete,
    # Flutter endpoints
    get_gears_json, get_gear_detail_json, get_cart_json, add_to_cart_flutter,
    update_cart_item_flutter, remove_from_cart_flutter, checkout_flutter,
    get_rentals_json, create_gear_flutter, update_gear_flutter, delete_gear_flutter,
    get_seller_gears_json, admin_gears_flutter, update_gear_admin_flutter, delete_gear_flutter
)

app_name = 'rental_gear'

urlpatterns = [
    # Flutter JSON API endpoints
    path('api/flutter/gears/', get_gears_json, name='flutter_gears_json'),
    path('api/flutter/gears/<int:id>/', get_gear_detail_json, name='flutter_gear_detail_json'),
    path('api/flutter/cart/', get_cart_json, name='flutter_cart_json'),
    path('api/flutter/cart/add/', add_to_cart_flutter, name='flutter_add_to_cart'),
    path('api/flutter/cart/update/<int:item_id>/', update_cart_item_flutter, name='flutter_update_cart'),
    path('api/flutter/cart/remove/<int:item_id>/', remove_from_cart_flutter, name='flutter_remove_from_cart'),
    path('api/flutter/checkout/', checkout_flutter, name='flutter_checkout'),
    path('api/flutter/rentals/', get_rentals_json, name='flutter_rentals_json'),
    path('api/flutter/seller/gears/', get_seller_gears_json, name='flutter_seller_gears'),
    path('api/flutter/seller/gears/create/', create_gear_flutter, name='flutter_create_gear'),
    path('api/flutter/seller/gears/<int:id>/update/', update_gear_flutter, name='flutter_update_gear'),
    path('api/flutter/seller/gears/<int:id>/delete/', delete_gear_flutter, name='flutter_delete_gear'),
    path('api/admin/gears/', admin_gears_flutter, name='admin_gears_flutter'),
    path('api/admin/gears/<int:gear_id>/update/', update_gear_admin_flutter, name='update_gear_admin_flutter'),
    path('api/delete-gear/<int:gear_id>/', delete_gear_flutter, name='delete_gear_flutter'),
    
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
