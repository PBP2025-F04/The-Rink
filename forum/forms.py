from django.forms import ModelForm
from forum.models import Post

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content"]