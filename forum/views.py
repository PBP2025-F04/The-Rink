from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.http import HttpResponse
from django.core import serializers
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from forum.models import Reply, Post, UpVote
from django.utils.timezone import localtime
from django.db.models import Count, Q
from django.db.models import F
import json

def show_forum(request):
    posts = Post.objects.order_by("-created_at", "-id")

    top_posts = (
        Post.objects
        .annotate(
            total_up=Count('upvotes', filter=Q(upvotes__is_upvote=True)),
            total_down=Count('upvotes', filter=Q(upvotes__is_upvote=False))
        )
        .annotate(score=F('total_up') - F('total_down'))
        .order_by('-score', '-total_up', '-total_down', '-created_at', '-id')[:5]
    )

    return render(request, "home.html", {"posts": posts, "top_posts": top_posts})


@csrf_exempt
@require_POST
def add_post(request):
    import json

    try:
        data = json.loads(request.body.decode('utf-8'))
        title = data.get('title', 'Untitled')
        content = data.get('content', '')
        thumbnail_url = data.get('thumbnail_url', None)
    except:
        title = request.POST.get('title', 'Untitled')
        content = request.POST.get('content', '')
        thumbnail_url = request.POST.get('thumbnail_url', None)

    if not content:
        return JsonResponse({"error": "Content cannot be empty"}, status=400)

    post = Post.objects.create(
        author=request.user,
        title=title,
        content=content,
        thumbnail_url=thumbnail_url,
    )

    return JsonResponse({
        "message": "Post created successfully",
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "thumbnail_url": post.thumbnail_url,
        "created_at": localtime(post.created_at).isoformat(),
        "user_id": post.author.id,            
        "author": post.author.username,       
    }, status=201)


@login_required
@csrf_exempt
def edit_post(request, id):
    try:
        post = get_object_or_404(Post, pk=id, author=request.user)

        if request.POST:
            title = request.POST.get("title", post.title)
            content = request.POST.get("content", post.content)
            thumbnail_url = request.POST.get("thumbnail_url", post.thumbnail_url)
        else:
            data = json.loads(request.body.decode('utf-8'))
            title = data.get("title", post.title)
            content = data.get("content", post.content)
            thumbnail_url = data.get("thumbnail_url", post.thumbnail_url)

        post.title = title
        post.content = content
        post.thumbnail_url = thumbnail_url 
        post.save()

        return JsonResponse({
            "success": True,
            "message": "Post updated successfully!"
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
@csrf_exempt
def delete_post(request, id):
    if request.method == "DELETE":
        try:
            post = Post.objects.get(pk=id, author=request.user)
            post.delete()
            return JsonResponse({"success": True, "message": "Post deleted successfully!"})
        except Post.DoesNotExist:
            return JsonResponse({"success": True, "message": "Post already deleted."})
    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)


def show_xml(request):
    post_list = Post.objects.all()
    xml_data = serializers.serialize("xml", post_list)
    return HttpResponse(xml_data, content_type="application/xml")

def show_json(request):
    post_list = (
        Post.objects
        .all()
        .order_by("-created_at", "-id") 
    )

    data = [
        {
            'id': post.id, 
            'author': post.author.username if post.author else None,
            'title': post.title,
            'content': post.content,
            "created_at": localtime(post.created_at).isoformat(),
            "thumbnail_url": post.thumbnail_url,
            'updated_at': post.updated_at,
            'user_id': post.author.id if post.author else None,
            'upvotes_count': post.total_upvotes(),
            'downvotes_count': post.total_downvotes(), 
        }
        for post in post_list
    ]

    return JsonResponse(data, safe=False)

def show_xml_by_id(request, post_id):
    try:   
        post_item = Post.objects.filter(pk=post_id)
        xml_data = serializers.serialize("xml", post_item)
        return HttpResponse(xml_data, content_type="application/xml")
    except Post.DoesNotExist:
        return HttpResponse(status=404)

def show_json_by_id(request, post_id):
    try:
        post = Post.objects.select_related('author').get(pk=post_id)
        data = {
            'author': post.author.username if post.author else None,
            'title': post.title,
            'content': post.content,
            'created_at': post.created_at.isoformat() if post.created_at else None,
            'updated_at' : post.updated_at,
            'user_id': post.author.id if post.author else None,
        }
        return JsonResponse(data)
    except Post.DoesNotExist:
        return JsonResponse({'detail': 'Not found'}, status=404)

@login_required
@csrf_exempt
def add_reply(request, post_id):
    if request.method == "POST":
        data = json.loads(request.body)
        content = data.get("content")

        post = Post.objects.get(id=post_id)
        reply = Reply.objects.create(
            post=post,
            author=request.user,
            content=content
        )

        return JsonResponse({
            "id": reply.id,
            "author": reply.author.username,
            "author_id": reply.author.id,  
            "content": reply.content,
            "created_at": reply.created_at.isoformat(),
            "post_id": reply.post.id,      
        })
    
def get_replies(request, post_id):
    replies = Reply.objects.filter(post_id=post_id).order_by("created_at")
    data = [{
        "id": r.id,
        "author": r.author.username,
        "author_id": r.author.id, 
        "post_id": r.post.id,  
        "content": r.content,
        "created_at": r.created_at.isoformat().replace("+00:00", "Z"),
        "upvotes_count": r.total_upvotes(),
        "downvotes_count": r.total_downvotes(),
    } for r in replies]
    return JsonResponse(data, safe=False)

@csrf_exempt
@login_required
def delete_reply(request, reply_id):
    if request.method == "DELETE":
        try:
            reply = Reply.objects.get(pk=reply_id)

            if reply.author != request.user:
                return JsonResponse({"error": "Unauthorized"}, status=403)

            reply.delete()
            return JsonResponse({"success": True}, status=200)

        except Reply.DoesNotExist:
            return JsonResponse({"error": "Reply not found"}, status=404)

    return JsonResponse({"error": "Invalid method"}, status=405)

@login_required
@require_POST
def edit_reply(request, reply_id):
    reply = get_object_or_404(Reply, pk=reply_id)

    if reply.author != request.user:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    data = json.loads(request.body)
    new_content = data.get("content", "").strip()

    if not new_content:
        return JsonResponse({"error": "Empty content"}, status=400)

    reply.content = new_content
    reply.save()

    return JsonResponse({
        "id": reply.id,
        "content": reply.content,
        "updated_at": reply.updated_at.isoformat()
    })

@csrf_exempt
def toggle_vote(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user = request.user if request.user.is_authenticated else None
            target_type = data.get("type")
            target_id = data.get("id")
            is_upvote = data.get("is_upvote", True)

            if not request.session.session_key:
                request.session.save()
            session_key = request.session.session_key

            if target_type == "post":
                target = Post.objects.get(pk=target_id)
                vote_filter = {"post": target}
            elif target_type == "reply":
                target = Reply.objects.get(pk=target_id)
                vote_filter = {"reply": target}
            else:
                return JsonResponse({"error": "Invalid target type"}, status=400)

            # 🟩 Toggle logic
            if user:
                vote, created = UpVote.objects.get_or_create(user=user, **vote_filter)
            else:
                vote, created = UpVote.objects.get_or_create(session_key=session_key, **vote_filter)

            if not created and vote.is_upvote == is_upvote:
                vote.delete()
            else:
                vote.is_upvote = is_upvote
                vote.save()

            target.refresh_from_db()

            return JsonResponse({
                "upvotes": target.upvotes.filter(is_upvote=True).count(),
                "downvotes": target.upvotes.filter(is_upvote=False).count(),
            })

        except Exception as e:
            print("Vote toggle error:", e)
            return JsonResponse({"error": "Vote failed"}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)



def get_top_posts_json(request):
    posts = (
        Post.objects
        .annotate(
            total_up=Count('upvotes', filter=Q(upvotes__is_upvote=True)),
            total_down=Count('upvotes', filter=Q(upvotes__is_upvote=False))
        )
        .annotate(score=F('total_up') - F('total_down'))
        .order_by('-score', '-total_up', '-total_down', '-created_at', '-id')[:3]
    )

    data = [
        {
            "id": p.id,
            "title": p.title,
            "content": strip_tags(p.content)[:120],
            "total_up": p.total_up,
            "total_down": p.total_down,
            "replies": p.replies.count(),
            "thumbnail_url": p.thumbnail_url,
            "created_at": localtime(p.created_at).isoformat() if p.created_at else None,
        }
        for p in posts
    ]

    return JsonResponse(data, safe=False)

def get_post_detail(request, post_id):
    try:
        post = Post.objects.select_related("author").get(pk=post_id)
        data = {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "thumbnail_url": post.thumbnail_url,
            "created_at": localtime(post.created_at).isoformat() if post.created_at else None,
            "author": post.author.username if post.author else "Anonymous",
            "user_id": post.author.id if post.author else None,
            "upvotes_count": post.total_upvotes(),
            "downvotes_count": post.total_downvotes(),
            "replies_count": post.replies.count(),
        }
        return JsonResponse(data)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status=404)


# Admin views for forum
from django.contrib import messages

def admin_post_list(request):
    if not request.session.get('is_admin'):
        return redirect('authentication:login')
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'forum/admin_post_list.html', {'posts': posts})


def admin_post_create(request):
    if not request.session.get('is_admin'):
        return redirect('authentication:login')
    from .forms import PostForm
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user  # Admin as author
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('forum:admin_post_list')
    else:
        form = PostForm()
    return render(request, 'forum/admin_post_form.html', {'form': form, 'action': 'Create'})


def admin_post_update(request, id):
    if not request.session.get('is_admin'):
        return redirect('authentication:login')
    from .forms import PostForm
    post = get_object_or_404(Post, id=id)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('forum:admin_post_list')
    else:
        form = PostForm(instance=post)
    return render(request, 'forum/admin_post_form.html', {'form': form, 'action': 'Update'})


def admin_post_delete(request, id):
    if not request.session.get('is_admin'):
        return redirect('authentication:login')
    post = get_object_or_404(Post, id=id)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('forum:admin_post_list')
    return render(request, 'forum/admin_post_confirm_delete.html', {'post': post})


def admin_reply_list(request):
    if not request.session.get('is_admin'):
        return redirect('authentication:login')
    replies = Reply.objects.all().order_by('-created_at')
    return render(request, 'forum/admin_reply_list.html', {'replies': replies})


def admin_reply_delete(request, id):
    if not request.session.get('is_admin'):
        return redirect('authentication:login')
    reply = get_object_or_404(Reply, id=id)
    if request.method == 'POST':
        reply.delete()
        messages.success(request, 'Reply deleted successfully!')
        return redirect('forum:admin_reply_list')
    return render(request, 'forum/admin_reply_confirm_delete.html', {'reply': reply})
