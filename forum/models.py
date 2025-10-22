from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_upvotes(self):
        return self.upvotes.count()
    
    def total_downvotes(self):
        return self.votes.filter(is_upvote=False).count()

    def __str__(self):
        return self.title

class Reply(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def total_upvotes(self):
        return self.upvotes.count()
    
    def total_downvotes(self):
        return self.votes.filter(is_upvote=False).count()

    def __str__(self):
        return f"Reply by {self.author.username} on {self.post.title}"


class UpVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='upvotes', null=True, blank=True)
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE, related_name='upvotes', null=True, blank=True)

    class Meta:
        unique_together = ('user', 'post', 'reply')  # biar user cuma bisa upvote sekali

    def __str__(self):
        target = self.post if self.post else self.reply
        return f"{self.user.username} {'upvoted' if self.is_upvote else 'downvoted'} {target}"
