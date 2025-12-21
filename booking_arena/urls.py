from django.urls import path
from booking_arena.views import *
from . import views
app_name = 'booking_arena'

urlpatterns = [
    # =================================================
    # 1. JALUR WEBSITE (HTMX & Template) - JANGAN DIUBAH
    # =================================================
    path('', show_arena, name='show_arena'),
    path('arena/<uuid:arena_id>/', arena_detail, name="arena_detail"), 
    path('<uuid:arena_id>/get-slots/', get_available_slots, name='get_available_slots'),
    path('my-bookings/', user_booking_list, name='user_booking_list'),
    path('cancel/<uuid:booking_id>/', cancel_booking, name='cancel_booking'),
    path('arena/<uuid:arena_id>/modal/<int:hour>/', get_sport_modal_partial, name='get_sport_modal'),
    path('arena/<uuid:arena_id>/book-hourly/', create_booking_hourly, name='create_booking_hourly'),
    path('add-ajax/', add_arena_ajax, name='add_arena_ajax'),
    path('delete-ajax/<uuid:arena_id>/', delete_arena_ajax, name='delete_arena_ajax'),

    # =================================================
    # 2. JALUR API FLUTTER (BARU & SEDERHANA)
    # =================================================
    path('api/arenas/', get_arenas_flutter, name='get_arenas_flutter'),
    path('api/bookings/', get_bookings_flutter, name='get_bookings_flutter'),
    path('api/booking/create/', create_booking_flutter, name='create_booking_flutter'),
    path('api/booking/cancel/', cancel_booking_flutter, name='cancel_booking_flutter'),
    path('api/my-history/', my_history_flutter, name='my_history_flutter'),
    path('api/delete/<uuid:arena_id>/', delete_arena_flutter, name='delete_arena_flutter'),

    # Admin URLs
    path('admin/arenas/', views.admin_arena_list, name='admin_arena_list'),
    path('admin/bookings/', views.admin_booking_list, name='admin_booking_list'),
]