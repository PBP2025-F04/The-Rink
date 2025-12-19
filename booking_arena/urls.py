from django.urls import path, include
from rest_framework.routers import DefaultRouter
from booking_arena.views import * 

app_name = 'booking_arena'

# --- 1. SETUP ROUTER API (Buat Flutter) ---
# Ini bakal otomatis generate URL kayak /arenas/ dan /bookings/
router = DefaultRouter()
router.register(r'arenas', ArenaViewSet)
router.register(r'bookings', BookingViewSet)

urlpatterns = [
    # --- JALUR WEBSITE ---
    path('', show_arena, name='show_arena'),
    path('arena/<uuid:arena_id>/', arena_detail, name="arena_detail"), 
    path('<uuid:arena_id>/get-slots/', get_available_slots, name='get_available_slots'),
    path('my-bookings/', user_booking_list, name='user_booking_list'),
    path('cancel/<uuid:booking_id>/', cancel_booking, name='cancel_booking'),
    path('arena/<uuid:arena_id>/modal/<int:hour>/', get_sport_modal_partial, name='get_sport_modal'),
    path('arena/<uuid:arena_id>/book-hourly/', create_booking_hourly, name='create_booking_hourly'),
    path('add-ajax/', add_arena_ajax, name='add_arena_ajax'),
    path('delete-ajax/<uuid:arena_id>/', delete_arena_ajax, name='delete_arena_ajax'),

    # --- JALUR API (BUAT FLUTTER) ---
    # Nanti aksesnya jadi: localhost:8000/booking_arena/api/arenas/
    path('api/', include(router.urls)), 
]