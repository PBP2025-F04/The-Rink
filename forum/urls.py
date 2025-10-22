from django.urls import path
from forum.views import show_forum, add_post_via_ajax, edit_post_via_ajax, post_detail, show_xml, show_json, show_xml_by_id, show_json_by_id, add_reply
from forum.views import show_replies_json

app_name = 'forum'

urlpatterns = [
    path('', show_forum, name='forum'),
    path('create-post-ajax', add_post_via_ajax, name='add_post_via_ajax'),
    path('post_detail/<str:id>/', post_detail, name='post_detail'),
    path('ajax-edit-product', edit_post_via_ajax, name='edit_post_via_ajax'),

    path('json/replies/<int:post_id>/', show_replies_json, name='show_replies_json'),
    path('json/<str:post_id>/', show_json_by_id, name='show_json_by_id'),
    path('xml/<str:post_id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/', show_json, name='show_json'),
    path('xml/', show_xml, name='show_xml'),

    path('post/<int:id>/reply/', add_reply, name='add_reply'),
]
