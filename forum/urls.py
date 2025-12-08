from django.urls import path
from forum.views import (
    show_forum,
    add_post,
    edit_post,
    delete_post,
    show_xml,
    show_json,
    show_xml_by_id,
    show_json_by_id,
    add_reply,
    get_replies,
    toggle_vote,
    delete_reply,
    edit_reply,
    get_top_posts_json,
    get_post_detail,
    admin_post_list,
    admin_post_create,
    admin_post_update,
    admin_post_delete,
    admin_reply_list,
    admin_reply_delete,
    proxy_image,
    add_post_flutter,
    edit_post_flutter,
    delete_post_flutter,
    add_reply_flutter,
    edit_reply_flutter,
    delete_reply_flutter,
)

app_name = 'forum'

urlpatterns = [
    path('', show_forum, name='show_forum'),

    # Django Post CRUD
    path('add-post', add_post, name='add_post'),
    path('edit-post/<int:id>/', edit_post, name='edit_post'),
    path('delete-post/<int:id>/', delete_post, name='delete_post'),

    # JSON & XML
    path('json/<str:post_id>/', show_json_by_id, name='show_json_by_id'),
    path('xml/<str:post_id>/', show_xml_by_id, name='show_xml_by_id'),
    path('json/', show_json, name='show_json'),
    path('xml/', show_xml, name='show_xml'),

    # Django Replies CRUD
    path('add-reply/<int:post_id>/', add_reply, name='add_reply'),
    path('get-replies/<int:post_id>/', get_replies, name='get_replies'),
    path("edit-reply/<int:reply_id>/", edit_reply, name="edit_reply"),
    path("delete-reply/<int:reply_id>/", delete_reply, name="delete_reply"),

    # Voting & top posts
    path('toggle-vote/', toggle_vote, name='toggle_vote'),
    path("get-top-posts-json/", get_top_posts_json, name="get_top_posts_json"),
    path("get-post/<int:post_id>/", get_post_detail, name="get_post_detail"),

    # Admin URLs
    path('admin/posts/', admin_post_list, name='admin_post_list'),
    path('admin/posts/add/', admin_post_create, name='admin_post_create'),
    path('admin/posts/<int:id>/edit/', admin_post_update, name='admin_post_update'),
    path('admin/posts/<int:id>/delete/', admin_post_delete, name='admin_post_delete'),
    path('admin/replies/', admin_reply_list, name='admin_reply_list'),
    path('admin/replies/<int:id>/delete/', admin_reply_delete, name='admin_reply_delete'),
    
    # Flutter Thumbnail
    path('proxy-image/', proxy_image, name='proxy_image'),

    # Flutter Post CRUD
    path('add-post-flutter/', add_post_flutter, name='add_post_flutter'),
    path('edit-post-flutter/<int:id>/', edit_post_flutter, name='edit_post_flutter'),
    path('delete-post-flutter/<int:id>/', delete_post_flutter, name='delete_post_flutter'),

    # Flutter Replies CRUD
    path('add-reply-flutter/<int:post_id>/', add_reply_flutter, name='add_reply_flutter'),
    path('edit-reply-flutter/<int:reply_id>/', edit_reply_flutter, name='edit_reply_flutter'),
    path('delete-reply-flutter/<int:reply_id>/', delete_reply_flutter, name='delete_reply_flutter'),
]
