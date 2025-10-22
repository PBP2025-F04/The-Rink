# events/urls.py
from django.urls import path
from . import views

app_name = 'events' 

urlpatterns = [
    # --- Paket ---
    # e.g., /packages/
    path('packages/', views.package_list_view, name='package_list'),
    
    # e.g., /packages/5/book/ (URL ini untuk GET modal dan POST form)
    path('packages/<int:package_id>/book/', views.book_package_view, name='book_package'),

    # --- Event ---
    # e.g., /events/
    path('events/', views.event_list_view, name='event_list'),
    
    # e.g., /events/12/
    path('events/<int:event_id>/', views.event_detail_view, name='event_detail'),
    
    # e.g., /events/12/register/ (HTMX POST)
    path('events/<int:event_id>/register/', views.register_event_view, name='register_event'),
    
    # e.g., /events/12/unregister/ (HTMX POST)
    path('events/<int:event_id>/unregister/', views.unregister_event_view, name='unregister_event'),
]