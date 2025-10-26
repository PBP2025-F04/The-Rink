# File: booking_arena/urls.py

from django.urls import path
from booking_arena.views import *

app_name = 'booking_arena'
urlpatterns = [
    path('', show_arena, name='show_arena'),
    path('arena/<uuid:arena_id>/', arena_detail, name="arena_detail"), 
    path('<uuid:arena_id>/get-slots/', get_available_slots, name='get_available_slots'),
    path('my-bookings/', user_booking_list, name='user_booking_list'),
    path('cancel/<uuid:booking_id>/', cancel_booking, name='cancel_booking'),
    path('arena/<uuid:arena_id>/modal/<int:hour>/', get_sport_modal_partial, name='get_sport_modal'),
    path('arena/<uuid:arena_id>/book-hourly/', create_booking_hourly, name='create_booking_hourly'),
    path('add-ajax/', add_arena_ajax, name='add_arena_ajax'),
    path('delete-ajax/<uuid:arena_id>/', delete_arena_ajax, name='delete_arena_ajax'),

    # Admin views
    path('admin/arenas/', admin_arena_list, name='admin_arena_list'),
    path('admin/arenas/create/', admin_arena_create, name='admin_arena_create'),
    path('admin/arenas/<uuid:id>/update/', admin_arena_update, name='admin_arena_update'),
    path('admin/arenas/<uuid:id>/delete/', admin_arena_delete, name='admin_arena_delete'),
    path('admin/bookings/', admin_booking_list, name='admin_booking_list'),
    path('admin/bookings/<uuid:id>/delete/', admin_booking_delete, name='admin_booking_delete'),

    # View lama lu yg pake JSON (kalo masih dipake di tempat lain)
    # path('create-multiple/', create_multiple_bookings, name='create_multiple_bookings'),
]
