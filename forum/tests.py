from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from forum.models import Post, Reply, UpVote
from django.test.client import RequestFactory
import json


class ForumBaseTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="angga", password="123")
        self.user2 = User.objects.create_user(username="yafi", password="123")
        self.post = Post.objects.create(author=self.user, title="Test Post", content="Hello world!")

        self.client.login(username="angga", password="123")

class ModelTests(ForumBaseTest):
    def test_post_str(self):
        self.assertEqual(str(self.post), "Test Post")

    def test_reply_str(self):
        reply = Reply.objects.create(post=self.post, author=self.user, content="Nice post!")
        self.assertIn("Reply by angga", str(reply))

    def test_upvote_str(self):
        up = UpVote.objects.create(user=self.user, post=self.post, is_upvote=True)
        self.assertIn("👍 Post", str(up))

    def test_total_upvotes_downvotes(self):
        UpVote.objects.create(user=self.user, post=self.post, is_upvote=True)
        UpVote.objects.create(user=self.user2, post=self.post, is_upvote=False)
        self.assertEqual(self.post.total_upvotes(), 1)
        self.assertEqual(self.post.total_downvotes(), 1)

class PostViewTests(ForumBaseTest):
    def test_show_json(self):
        res = self.client.get(reverse("forum:show_json"))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(isinstance(data, list))
        self.assertIn("title", data[0])

    def test_show_json_by_id(self):
        res = self.client.get(reverse("forum:show_json_by_id", args=[self.post.id]))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["title"], self.post.title)

    def test_show_json_by_id_not_found(self):
        res = self.client.get(reverse("forum:show_json_by_id", args=[999]))
        self.assertEqual(res.status_code, 404)

    def test_add_post_valid(self):
        payload = {"title": "New Post", "content": "Hai semua"}
        res = self.client.post(reverse("forum:add_post"),
                               data=json.dumps(payload),
                               content_type="application/json")
        self.assertEqual(res.status_code, 201)
        self.assertEqual(Post.objects.count(), 2)

    def test_add_post_empty_content(self):
        payload = {"title": "Bad", "content": ""}
        res = self.client.post(reverse("forum:add_post"),
                               data=json.dumps(payload),
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)

    def test_edit_post_self(self):
        payload = {"title": "Edited", "content": "Changed content"}
        res = self.client.post(reverse("forum:edit_post", args=[self.post.id]),
                               data=json.dumps(payload),
                               content_type="application/json")
        self.assertEqual(res.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Edited")

    def test_edit_post_other_user_forbidden(self):
        self.client.logout()
        self.client.login(username="yafi", password="123")
        payload = {"title": "Hacked"}
        res = self.client.post(reverse("forum:edit_post", args=[self.post.id]),
                               data=json.dumps(payload),
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)  
    def test_delete_post_success(self):
        res = self.client.delete(reverse("forum:delete_post", args=[self.post.id]))
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

    def test_delete_post_not_found(self):
        res = self.client.delete(reverse("forum:delete_post", args=[999]))
        self.assertEqual(res.status_code, 200)

    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()

    def test_add_post_formdata_fallback(self):
        res = self.client.post(reverse("forum:add_post"), {
            "title": "Form Post",
            "content": "Created via form data"
        })
        self.assertEqual(res.status_code, 201)
        self.assertTrue(Post.objects.filter(title="Form Post").exists())

    def test_edit_post_json_decode_error(self):
        url = reverse("forum:edit_post", args=[self.post.id])
        res = self.client.post(url, data="{invalid_json", content_type="application/json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("error", res.json())

    def test_delete_post_invalid_method(self):
        url = reverse("forum:delete_post", args=[self.post.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 405)
        self.assertIn("Invalid", res.json()["message"])

    def test_admin_post_views(self):
        session = self.client.session
        session["is_admin"] = True
        session.save()

        res = self.client.get(reverse("forum:admin_post_list"))
        self.assertEqual(res.status_code, 200)

        res = self.client.post(reverse("forum:admin_post_create"), {
            "title": "Admin Made",
            "content": "By admin",
        })
        self.assertIn(res.status_code, [200, 302])  
        new_post = Post.objects.filter(title="Admin Made").first()
        if new_post:
            res2 = self.client.post(reverse("forum:admin_post_update", args=[new_post.id]), {
                "title": "Admin Edited",
                "content": "Updated content",
            })
            self.assertIn(res2.status_code, [200, 302])

            res3 = self.client.post(reverse("forum:admin_post_delete", args=[new_post.id]))
            self.assertIn(res3.status_code, [200, 302])

        res = self.client.get(reverse("forum:admin_reply_list"))
        self.assertEqual(res.status_code, 200)

        reply = Reply.objects.create(post=self.post, author=self.user, content="For admin delete")
        res = self.client.post(reverse("forum:admin_reply_delete", args=[reply.id]))
        self.assertIn(res.status_code, [200, 302])

class ReplyViewTests(ForumBaseTest):
    def setUp(self):
        super().setUp()
        self.reply = Reply.objects.create(post=self.post, author=self.user, content="Initial reply")

    def test_add_reply(self):
        payload = {"content": "Nice!"}
        res = self.client.post(reverse("forum:add_reply", args=[self.post.id]),
                               data=json.dumps(payload),
                               content_type="application/json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Reply.objects.filter(post=self.post).count(), 2)

    def test_get_replies(self):
        res = self.client.get(reverse("forum:get_replies", args=[self.post.id]))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(isinstance(data, list))
        self.assertIn("content", data[0])

    def test_edit_reply_self(self):
        payload = {"content": "Edited reply"}
        res = self.client.post(reverse("forum:edit_reply", args=[self.reply.id]),
                               data=json.dumps(payload),
                               content_type="application/json")
        self.assertEqual(res.status_code, 200)
        self.reply.refresh_from_db()
        self.assertEqual(self.reply.content, "Edited reply")

    def test_edit_reply_unauthorized(self):
        self.client.logout()
        self.client.login(username="yafi", password="123")
        payload = {"content": "Hack attempt"}
        res = self.client.post(reverse("forum:edit_reply", args=[self.reply.id]),
                               data=json.dumps(payload),
                               content_type="application/json")
        self.assertEqual(res.status_code, 403)

    def test_delete_reply_success(self):
        res = self.client.delete(reverse("forum:delete_reply", args=[self.reply.id]))
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Reply.objects.filter(id=self.reply.id).exists())

    def test_delete_reply_other_user_forbidden(self):
        self.client.logout()
        self.client.login(username="yafi", password="123")
        res = self.client.delete(reverse("forum:delete_reply", args=[self.reply.id]))
        self.assertEqual(res.status_code, 403)

    def test_delete_reply_not_found(self):
        fake_id = self.reply.id + 999
        url = reverse("forum:delete_reply", args=[fake_id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, 404)
        self.assertIn("error", res.json())

class VoteTests(ForumBaseTest):
    def test_toggle_vote_post_up(self):
        res = self.client.post(reverse("forum:toggle_vote"),
                               data=json.dumps({"type": "post", "id": self.post.id, "is_upvote": True}),
                               content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["upvotes"], 1)

    def test_toggle_vote_post_down(self):
        res = self.client.post(reverse("forum:toggle_vote"),
                               data=json.dumps({"type": "post", "id": self.post.id, "is_upvote": False}),
                               content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("downvotes", data)

    def test_toggle_vote_reply(self):
        reply = Reply.objects.create(post=self.post, author=self.user, content="Cool!")
        res = self.client.post(reverse("forum:toggle_vote"),
                               data=json.dumps({"type": "reply", "id": reply.id, "is_upvote": True}),
                               content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["upvotes"], 1)

    def test_toggle_vote_invalid_type(self):
        res = self.client.post(reverse("forum:toggle_vote"),
                               data=json.dumps({"type": "invalid", "id": self.post.id}),
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)

    def test_toggle_vote_invalid_json(self):
        url = reverse("forum:toggle_vote")

        res = self.client.post(url, data="{invalid_json", content_type="application/json")
        self.assertIn(res.status_code, [400, 500])

        bad_payload = {"type": "wrong", "id": 999}
        res2 = self.client.post(url, data=json.dumps(bad_payload), content_type="application/json")
        self.assertEqual(res2.status_code, 400)
        self.assertIn("error", res2.json())

class TopPostTests(ForumBaseTest):
    def test_get_top_posts_json(self):
        post2 = Post.objects.create(author=self.user, title="Another", content="Second")
        UpVote.objects.create(user=self.user, post=post2, is_upvote=True)
        res = self.client.get(reverse("forum:get_top_posts_json"))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(isinstance(data, list))
        self.assertIn("title", data[0])
