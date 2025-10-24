from django.urls import path
from forum.views import show_forum, add_post, edit_post, delete_post, show_xml, show_json, show_xml_by_id, show_json_by_id, add_reply
from forum.views import add_reply, get_replies, toggle_vote, delete_reply, edit_reply, admin_post_list, admin_post_create, admin_post_update, admin_post_delete, admin_reply_list, admin_reply_delete

app_name = 'forum'

urlpatterns = [
    path('', show_forum, name='show_forum'),

    path('add-post', add_post, name='add_post'),
    path('edit-post/<int:id>/', edit_post, name='edit_post'),
    path('delete-post/<int:id>/', delete_post, name='delete_post'),

    path('json/<str:post_id>/', show_json_by_id, name='show_json_by_id'),
    path('xml/<str:post_id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/', show_json, name='show_json'),
    path('xml/', show_xml, name='show_xml'),

    path('add-reply/<int:post_id>/', add_reply, name='add_reply'),
    path('get-replies/<int:post_id>/', get_replies, name='get_replies'),
    path("delete-reply/<int:reply_id>/", delete_reply, name="delete_reply"),
    path("edit-reply/<int:reply_id>/", edit_reply, name="edit_reply"),
    path('toggle-vote/', toggle_vote, name='toggle_vote'),

    # Admin URLs
    path('admin/posts/', admin_post_list, name='admin_post_list'),
    path('admin/posts/add/', admin_post_create, name='admin_post_create'),
    path('admin/posts/<int:id>/edit/', admin_post_update, name='admin_post_update'),
    path('admin/posts/<int:id>/delete/', admin_post_delete, name='admin_post_delete'),
    path('admin/replies/', admin_reply_list, name='admin_reply_list'),
    path('admin/replies/<int:id>/delete/', admin_reply_delete, name='admin_reply_delete'),
]
