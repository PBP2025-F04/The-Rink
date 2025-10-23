from django.urls import path
from . import views

app_name = 'booking_arena'

urlpatterns = [
    path('', views.arena_list, name='arena_list'),
    path('arena/<int:pk>/', views.arena_detail, name='arena_detail'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('arena/<int:pk>/book-ajax/', views.ajax_book_arena, name='ajax_book_arena'),
    path('booking/<int:pk>/cancel-ajax/', views.ajax_cancel_booking, name='ajax_cancel_booking'),
]
