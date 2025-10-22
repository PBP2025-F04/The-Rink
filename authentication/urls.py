from django.urls import path
<<<<<<< HEAD
from . import views

app_name = 'authentication'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
=======
from authentication.views import register, login_user, logout_user

app_name = 'main'

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
>>>>>>> d4093bfe0e5ab84a85d77ef2323fd24229824147
]