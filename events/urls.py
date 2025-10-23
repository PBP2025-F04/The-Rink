# events/urls.py
from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.event_list, name='list'),
    path('my-events/', views.my_events, name='my_events'),
    path('<slug:slug>/', views.event_detail, name='detail'),
    
<<<<<<< HEAD
    # --- HTMX Endpoints ---
    # GET untuk memuat modal
    path('<slug:slug>/get-modal/', views.get_registration_modal, name='get_modal'), 
=======
    # e.g., /packages/5/book/ (URL ini untuk GET modal dan POST form)
    path('packages/<int:package_id>/book/', views.book_package_view, name='book_package'),

    # --- Event ---
    # e.g., /events/
    path('', views.event_list_view, name='event_list'),
>>>>>>> d5c473d (Test)
    
    # POST untuk mendaftar
    path('<slug:slug>/register/', views.register_event, name='register'),
    
    # POST untuk batal
    path('<slug:slug>/cancel/', views.cancel_registration, name='cancel'),
]