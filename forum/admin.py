from django.contrib import admin
from .models import Post, Reply, UpVote

class ReplyInline(admin.TabularInline):
    model = Reply
    extra = 0 
    readonly_fields = ('author', 'content', 'created_at', 'updated_at')
    can_delete = True
    show_change_link = True

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'total_upvotes', 'total_downvotes', 'created_at')
    list_filter = ('author', 'created_at')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    inlines = [ReplyInline] 

@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'author', 'total_upvotes', 'total_downvotes', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(UpVote)
class UpVoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'post', 'reply', 'is_upvote', 'created_at')
    list_filter = ('is_upvote', 'created_at')
    search_fields = ('user__username', 'session_key')
    ordering = ('-created_at',)

