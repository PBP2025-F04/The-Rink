from django.urls import path
from forum.views import show_forum, add_post, edit_post, delete_post, show_xml, show_json, show_xml_by_id, show_json_by_id, add_reply
from forum.views import show_replies_json

app_name = 'forum'

urlpatterns = [
    path('', show_forum, name='show_forum'),

    path('add-post', add_post, name='add_post'),
    path('edit-post/<int:id>/', edit_post, name='edit_post'),
    path('delete-post/<int:id>/', delete_post, name='delete_post'),

    path('json/replies/<int:post_id>/', show_replies_json, name='show_replies_json'),

    path('json/<str:post_id>/', show_json_by_id, name='show_json_by_id'),
    path('xml/<str:post_id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/', show_json, name='show_json'),
    path('xml/', show_xml, name='show_xml'),

    path('post/<int:id>/reply/', add_reply, name='add_reply'),
]
