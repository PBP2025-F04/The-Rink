from django.urls import path
from booking_arena.views import *

app = 'booking_arena'
urlpatterns = [
    path('', show_arena, name='show_arena'),
    path('<uuid:arena_id>/', arena_detail, name="arena_detail"),
    path('<uuid:arena_id>/get-slots/', get_available_slots, name='get_available_slots'),
    path('book/<uuid:slot_id>/', create_booking, name='create_booking'),
    path('my-bookings/', user_booking_list, name='user_booking_list'),
    path('cancel/<uuid:booking_id>/', cancel_booking, name='cancel_booking'),
]