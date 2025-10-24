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

def show_forum(request):
    posts = Post.objects.all()
    context = {'posts': posts}
    return render(request, "home.html", context)


@csrf_exempt
@require_POST
def add_post(request):
    import json

    try:
        # Coba baca body JSON
        data = json.loads(request.body.decode('utf-8'))
        title = data.get('title', 'Untitled')
        content = data.get('content', '')
        thumbnail_url = data.get('thumbnail_url', None)
    except:
        # fallback ke form-data
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
         "user_id": post.author.id,              # ✅ tambahkan
    "author": post.author.username,         # ✅ tambahkan
    }, status=201)


@login_required
@csrf_exempt
def edit_post(request, id):
    try:
        post = get_object_or_404(Post, pk=id, author=request.user)

        # Bisa handle JSON atau FormData
        if request.POST:
            title = request.POST.get("title", post.title)
            content = request.POST.get("content", post.content)
            thumbnail = request.POST.get("thumbnail", "")
        else:
            import json
            data = json.loads(request.body.decode('utf-8'))
            title = data.get("title", post.title)
            content = data.get("content", post.content)
            thumbnail = data.get("thumbnail", "")

        post.title = title
        post.content = content
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
            # ✅ Ubah dari 404 jadi 200 agar tidak spam error di terminal
            return JsonResponse({"success": True, "message": "Post already deleted."})
    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)


def show_xml(request):
    post_list = Post.objects.all()
    xml_data = serializers.serialize("xml", post_list)
    return HttpResponse(xml_data, content_type="application/xml")

def show_json(request):
    post_list = Post.objects.all()
    data = [
        {
            'id': post.id, 
            'author': post.author.username if post.author else None,  # ← fix di sini
            'title': post.title,
            'content': post.content,
            "created_at": localtime(post.created_at).isoformat(),
            "thumbnail_url": post.thumbnail_url,
            'updated_at': post.updated_at,
            'user_id': post.author.id,      
            
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
    
def show_replies_json(request, post_id):
    replies = Reply.objects.filter(post_id=post_id).select_related('author').order_by('-created_at')
    data = [
        {
            'author': reply.author.usertitle,
            'content': reply.content,
            'created_at': reply.created_at.strftime("%H:%M, %d %b %Y")
        }
        for reply in replies
    ]
    return JsonResponse(data, safe=False)

    
@login_required
def add_reply(request, id):
    post = get_object_or_404(Post, pk=id)

    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Reply.objects.create(
                post=post,
                author=request.user,
                content=content
            )
    return redirect('main:post_detail', id=post.id)

@login_required
def toggle_vote(request, post_id=None, reply_id=None, is_upvote=True):
    if post_id:
        target = get_object_or_404(Post, id=post_id)
        vote, created = UpVote.objects.get_or_create(user=request.user, post=target)
    elif reply_id:
        target = get_object_or_404(Reply, id=reply_id)
        vote, created = UpVote.objects.get_or_create(user=request.user, reply=target)
    else:
        return JsonResponse({'error': 'Invalid target'}, status=400)

    if not created:
        if vote.is_upvote == is_upvote:
            vote.delete()  # toggle off
        else:
            vote.is_upvote = is_upvote
            vote.save()
    else:
        vote.is_upvote = is_upvote
        vote.save()

    return JsonResponse({
        'upvotes': target.total_upvotes(),
        'downvotes': target.total_downvotes(),
        'reputation': target.author.profile.reputation,
    })