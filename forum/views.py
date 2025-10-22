import datetime
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.http import HttpResponse
from django.core import serializers
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from forum.forms import PostForm
from forum.models import Reply, Post, UpVote

# @login_required(login_url='/login')
def show_forum(request):
    filter_type = request.GET.get("filter", "all") 
    if filter_type == "all":
        post_list = Post.objects.all()
    else:
        post_list = Post.objects.filter(user=request.user)

    context = {
        'posts': post_list,
    }
    return render(request, 'home.html', context)

# @login_required(login_url='/login')
def post_detail(request, id):
    post = get_object_or_404(Post, pk=id)
    replies = post.replies.all().order_by('-created_at')  

    context = {
        'post': post,
        'replies': replies,  
    }

    return render(request, "post_detail.html", context)

@csrf_exempt
@require_POST
def add_post_via_ajax(request):
    title = strip_tags(request.POST.get("title")) 
    content = strip_tags(request.POST.get("content")) 
    user = request.user

    new_post = Post(
        title=title, 
        content=content,
        user=user
    )
    new_post.save()

    return HttpResponse(b"CREATED", status=201)

def edit_post_via_ajax(request):
    post = get_object_or_404(Post, pk=id, user=request.user)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return JsonResponse({
                "success": True,
                "message": "Post updated successfully!"
            })
        else:
            return JsonResponse({
                "success": False,
                "message": "Please fix the errors below.",
                "errors": form.errors
            }, status=400)

    return JsonResponse({
        "success": False,
        "message": "Invalid request method."
    }, status=405)

def show_xml(request):
    post_list = Post.objects.all()
    xml_data = serializers.serialize("xml", post_list)
    return HttpResponse(xml_data, content_type="application/xml")

def show_json(request):
    post_list = Post.objects.all()
    data = [
        {
            'author': post.author.usertitle if post.author else None,
            'title': post.title,
            'content': post.content,
            'created_at': post.created_at.isoformat() if post.created_at else None,
            'updated_at' : post.updated_at,
            'user_id': post.user_id,
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
            'author': post.author.usertitle if post.author else None,
            'title': post.title,
            'content': post.content,
            'created_at': post.created_at.isoformat() if post.created_at else None,
            'updated_at' : post.updated_at,
            'user_id': post.user_id,
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

    
#@login_required
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

#@login_required
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