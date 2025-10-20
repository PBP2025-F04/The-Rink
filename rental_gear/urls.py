from django.urls import path
from . import views

urlpatterns = [
    path('', views.catalog, name='catalog'),
    path('filter/', views.filter_gear, name='filter_gear'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:gear_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('gear/<int:id>/', views.gear_detail, name='gear_detail'),
    path('checkout/', views.checkout, name='checkout'),
]
