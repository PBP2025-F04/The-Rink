from django.urls import path
from authentication.views import register, login_user, logout_user, profile, seller_profile

app_name = 'authentication'

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('profile/', profile, name='profile'),
    path('seller-profile/', seller_profile, name='seller_profile'),
]
