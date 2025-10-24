from django.urls import path
from booking_arena.views import *

app_name = 'booking_arena'
urlpatterns = [
    path('', show_arena, name='show_arena'),
    path('<uuid:arena_id>/', arena_detail, name="arena_detail"),
    path('<uuid:arena_id>/get-slots/', get_available_slots, name='get_available_slots'),
    path('book/<uuid:slot_id>/', create_booking, name='create_booking'),
    path('my-bookings/', user_booking_list, name='user_booking_list'),
    path('cancel/<uuid:booking_id>/', cancel_booking, name='cancel_booking'),

    # Admin URLs
    path('admin/arenas/', admin_arena_list, name='admin_arena_list'),
    path('admin/arenas/add/', admin_arena_create, name='admin_arena_create'),
    path('admin/arenas/<uuid:arena_id>/edit/', admin_arena_update, name='admin_arena_update'),
    path('admin/arenas/<uuid:arena_id>/delete/', admin_arena_delete, name='admin_arena_delete'),
    path('admin/bookings/', admin_booking_list, name='admin_booking_list'),
    path('admin/bookings/<uuid:booking_id>/delete/', admin_booking_delete, name='admin_booking_delete'),
]
