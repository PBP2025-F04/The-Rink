from django.forms import ModelForm
from forum.models import Post, Reply

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "thumbnail_url"]

class ReplyForm(ModelForm):
    class Meta:
        model = Reply
        fields = ["content"]
