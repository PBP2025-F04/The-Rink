# events/urls.py
from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    # --- Event list & detail ---
    path('', views.event_list, name='list'),
    path('my-events/', views.my_events, name='my_events'),
    path('<slug:slug>/', views.event_detail, name='detail'),

    # --- HTMX Endpoints ---
    # GET untuk memuat modal
    path('<slug:slug>/get-modal/', views.get_registration_modal, name='get_modal'),

    # POST untuk mendaftar
    path('<slug:slug>/register/', views.register_event, name='register'),

    # POST untuk batal
    path('<slug:slug>/cancel/', views.cancel_registration, name='cancel'),
]
