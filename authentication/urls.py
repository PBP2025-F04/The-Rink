from django.urls import path
from authentication.views import register, login_user, logout_user

<<<<<<< HEAD
app_name = 'authentication'
=======
app_name = 'main'
>>>>>>> origin

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
]