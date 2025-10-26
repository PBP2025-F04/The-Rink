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

    # Admin URLs
    path('admin/events/', views.admin_event_list, name='admin_event_list'),
    path('admin/events/add/', views.admin_event_create, name='admin_event_create'),
    path('admin/events/<int:id>/edit/', views.admin_event_update, name='admin_event_update'),
    path('admin/events/<int:id>/delete/', views.admin_event_delete, name='admin_event_delete'),
]
