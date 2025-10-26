from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from forum.models import Post, Reply, UpVote
from django.utils.timezone import now
import json


class ForumViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.client.login(username='testuser', password='pass123')

        self.post = Post.objects.create(
            author=self.user, title="Test Post", content="Test Content"
        )
        self.reply = Reply.objects.create(
            post=self.post, author=self.user, content="Reply content"
        )

    def test_show_forum(self):
        response = self.client.get(reverse('forum:show_forum'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_add_post_json(self):
        data = {"title": "New Post", "content": "Some content"}
        response = self.client.post(
            reverse('forum:add_post'),
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("Post created successfully", response.json()["message"])

    def test_add_post_form(self):
        data = {"title": "Form Post", "content": "Form content"}
        response = self.client.post(reverse('forum:add_post'), data)
        self.assertEqual(response.status_code, 201)

    def test_add_post_empty_content(self):
        response = self.client.post(reverse('forum:add_post'), {"content": ""})
        self.assertEqual(response.status_code, 400)

    def test_edit_post_success(self):
        data = {"title": "Edited Title", "content": "Edited Content"}
        response = self.client.post(
            reverse('forum:edit_post', args=[self.post.id]),
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Edited Title")

    def test_edit_post_unauthorized(self):
        other_user = User.objects.create_user(username="other", password="123")
        other_post = Post.objects.create(author=other_user, title="Oth", content="ccc")
        response = self.client.post(
            reverse('forum:edit_post', args=[other_post.id]),
            json.dumps({"title": "Hack"}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_post_success(self):
        response = self.client.delete(reverse('forum:delete_post', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)

    def test_delete_post_invalid_method(self):
        response = self.client.get(reverse('forum:delete_post', args=[self.post.id]))
        self.assertEqual(response.status_code, 405)

    def test_show_json(self):
        response = self.client.get(reverse('forum:show_json'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data) > 0)

    def test_show_xml(self):
        response = self.client.get(reverse('forum:show_xml'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"<object", response.content)

    def test_show_json_by_id_valid(self):
        response = self.client.get(reverse('forum:show_json_by_id', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)

    def test_show_json_by_id_invalid(self):
        response = self.client.get(reverse('forum:show_json_by_id', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_add_reply(self):
        data = {"content": "Nice!"}
        response = self.client.post(
            reverse('forum:add_reply', args=[self.post.id]),
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Nice!", response.json()["content"])

    def test_get_replies(self):
        response = self.client.get(reverse('forum:get_replies', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data) >= 1)

    def test_delete_reply_success(self):
        response = self.client.delete(reverse('forum:delete_reply', args=[self.reply.id]))
        self.assertEqual(response.status_code, 200)

    def test_delete_reply_invalid_method(self):
        response = self.client.get(reverse('forum:delete_reply', args=[self.reply.id]))
        self.assertEqual(response.status_code, 405)

    def test_delete_reply_unauthorized(self):
        other = User.objects.create_user(username="other2", password="123")
        reply = Reply.objects.create(post=self.post, author=other, content="hey")
        response = self.client.delete(reverse('forum:delete_reply', args=[reply.id]))
        self.assertEqual(response.status_code, 403)

    def test_edit_reply_success(self):
        data = {"content": "Edited reply"}
        response = self.client.post(
            reverse('forum:edit_reply', args=[self.reply.id]),
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_edit_reply_empty(self):
        data = {"content": ""}
        response = self.client.post(
            reverse('forum:edit_reply', args=[self.reply.id]),
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_toggle_vote_post(self):
        data = {"type": "post", "id": self.post.id, "is_upvote": True}
        response = self.client.post(
            reverse('forum:toggle_vote'),
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_toggle_vote_reply(self):
        data = {"type": "reply", "id": self.reply.id, "is_upvote": True}
        response = self.client.post(
            reverse('forum:toggle_vote'),
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_toggle_vote_invalid_type(self):
        data = {"type": "invalid", "id": self.post.id}
        response = self.client.post(
            reverse('forum:toggle_vote'),
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_toggle_vote_unauthenticated(self):
        self.client.logout()
        data = {"type": "post", "id": self.post.id}
        response = self.client.post(
            reverse('forum:toggle_vote'),
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)

    def test_get_top_posts_json(self):
        response = self.client.get(reverse('forum:get_top_posts_json'))
        self.assertEqual(response.status_code, 200)
