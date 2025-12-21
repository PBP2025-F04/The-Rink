from django.urls import path
from auth_mob.views import login, register, logout, get_user_data, update_profile, get_user_type, get_seller_profile, update_seller_profile, get_admin_stats, get_users_list, update_user, delete_user, get_arenas_admin, create_arena_admin, update_arena_admin, delete_arena_admin, get_bookings_admin, update_booking_admin, get_events_admin, create_event_admin, update_event_admin, delete_event_admin, get_posts_admin, delete_post_admin, get_replies_admin, delete_reply_admin, get_gears_admin, delete_gear_admin

app_name = 'auth_mob'

urlpatterns = [
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout, name='logout'),
    path('user/', get_user_data, name='get_user_data'),
    path('user-type/', get_user_type, name='get_user_type'),
    path('profile/', update_profile, name='update_profile'),
    path('seller-profile/', get_seller_profile, name='get_seller_profile'),
    path('seller-profile/update/', update_seller_profile, name='update_seller_profile'),
    path('admin/stats/', get_admin_stats, name='get_admin_stats'),
    path('admin/users/', get_users_list, name='get_users_list'),
    path('admin/users/<int:user_id>/', update_user, name='update_user'),
    path('admin/users/<int:user_id>/delete/', delete_user, name='delete_user'),
    path('admin/arenas/', get_arenas_admin, name='get_arenas_admin'),
    path('admin/arenas/create/', create_arena_admin, name='create_arena_admin'),
    path('admin/arenas/<uuid:arena_id>/', update_arena_admin, name='update_arena_admin'),
    path('admin/arenas/<uuid:arena_id>/delete/', delete_arena_admin, name='delete_arena_admin'),
    path('admin/bookings/', get_bookings_admin, name='get_bookings_admin'),
    path('admin/bookings/<uuid:booking_id>/', update_booking_admin, name='update_booking_admin'),
    path('admin/events/', get_events_admin, name='get_events_admin'),
    path('admin/events/create/', create_event_admin, name='create_event_admin'),
    path('admin/events/<int:event_id>/', update_event_admin, name='update_event_admin'),
    path('admin/events/<int:event_id>/delete/', delete_event_admin, name='delete_event_admin'),
    path('admin/posts/', get_posts_admin, name='get_posts_admin'),
    path('admin/posts/<int:post_id>/delete/', delete_post_admin, name='delete_post_admin'),
    path('admin/replies/', get_replies_admin, name='get_replies_admin'),
    path('admin/replies/<int:reply_id>/delete/', delete_reply_admin, name='delete_reply_admin'),
    path('admin/gears/', get_gears_admin, name='get_gears_admin'),
    path('admin/gears/<int:gear_id>/delete/', delete_gear_admin, name='delete_gear_admin'),
]
