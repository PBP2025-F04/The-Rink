# events/urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'events'

urlpatterns = [
    path('', views.event_list, name='list'),
    path('my-events/', views.my_events, name='my_events'),
    path('<slug:slug>/', views.event_detail, name='detail'),
    path('<slug:slug>/get-modal/', views.get_registration_modal, name='get_modal'),
    path('<slug:slug>/register/', views.register_event, name='register'),
    path('<slug:slug>/cancel/', views.cancel_registration, name='cancel'),
    path('admin/events/', views.admin_event_list, name='admin_event_list'),
    path('admin/events/add/', views.admin_event_create, name='admin_event_create'),
    path('admin/events/<int:id>/edit/', views.admin_event_update, name='admin_event_update'),
    path('admin/events/<int:id>/delete/', views.admin_event_delete, name='admin_event_delete'),
    
    path('api/list/', views.get_events_json, name='get_events_json'),
    path('api/join/<int:event_id>/', views.join_event_flutter, name='join_event_flutter'),
    path('api/detail/<int:event_id>/', views.get_event_detail_json),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)