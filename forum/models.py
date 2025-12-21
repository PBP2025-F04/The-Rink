from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    thumbnail_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_upvotes(self):
        return self.upvotes.filter(is_upvote=True).count()

    def total_downvotes(self):
        return self.upvotes.filter(is_upvote=False).count()

    def __str__(self):
        return self.title


class Reply(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_upvotes(self):
        return self.upvotes.filter(is_upvote=True).count()

    def total_downvotes(self):
        return self.upvotes.filter(is_upvote=False).count()

    def __str__(self):
        return f"Reply by {self.author.username} on {self.post.title}"


class UpVote(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='votes',
        null=True, blank=True
    )
    session_key = models.CharField(max_length=40, null=True, blank=True) 
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='upvotes', null=True, blank=True)
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE, related_name='upvotes', null=True, blank=True)
    is_upvote = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'],
                name='unique_vote_per_user_post',
                condition=models.Q(reply__isnull=True, user__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['user', 'reply'],
                name='unique_vote_per_user_reply',
                condition=models.Q(post__isnull=True, user__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['session_key', 'post'],
                name='unique_vote_per_session_post',
                condition=models.Q(reply__isnull=True, session_key__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['session_key', 'reply'],
                name='unique_vote_per_session_reply',
                condition=models.Q(post__isnull=True, session_key__isnull=False)
            ),
        ]

    def __str__(self):
        target = self.post if self.post else self.reply
        target_type = "Post" if self.post else "Reply"
        voter = self.user.username if self.user else f"Guest({self.session_key[:6]})"
        return f"{voter} {'👍' if self.is_upvote else '👎'} {target_type} {target}"

