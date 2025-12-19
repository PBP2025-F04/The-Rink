from django.urls import path
from auth_mob.views import login, register, logout, get_user_data, update_profile, get_user_type, get_seller_profile, update_seller_profile

app_name = 'authentication'

urlpatterns = [
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout, name='logout'),
    path('user/', get_user_data, name='get_user_data'),
    path('user-type/', get_user_type, name='get_user_type'),
    path('profile/', update_profile, name='update_profile'),
    path('seller-profile/', get_seller_profile, name='get_seller_profile'),
    path('seller-profile/update/', update_seller_profile, name='update_seller_profile'),
]
