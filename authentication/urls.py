from django.urls import path
from authentication.views import register, login_user, logout_user, profile, seller_profile, dashadmin, admin_user_list, admin_user_update, admin_user_delete

app_name = 'authentication'

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('profile/', profile, name='profile'),
    path('seller-profile/', seller_profile, name='seller_profile'),
    path('dashadmin/', dashadmin, name='dashadmin'),

    # Admin URLs
    path('admin/users/', admin_user_list, name='admin_user_list'),
    path('admin/users/<int:user_id>/edit/', admin_user_update, name='admin_user_update'),
    path('admin/users/<int:user_id>/delete/', admin_user_delete, name='admin_user_delete'),
]
