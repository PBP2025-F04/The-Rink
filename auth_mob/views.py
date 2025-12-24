from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login
from django.http import JsonResponse
import json
from django.contrib.auth.models import User
from django.contrib.auth import logout as auth_logout
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from authentication.models import UserProfile, SellerProfile, UserType
from rental_gear.models import Gear, Rental
from events.models import Event, EventRegistration
from forum.models import Post, Reply
from booking_arena.models import Arena, Booking
from django.utils import timezone

@ensure_csrf_cookie
@csrf_exempt
def login(request):
    username = ""
    password = ""
    
    # ini coba baca dari JSON (FLUTTER)
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
    except:
        username = request.POST.get('username')
        password = request.POST.get('password')

    if not username or not password:
         return JsonResponse({
            "status": False, 
            "message": "Username atau Password tidak boleh kosong."
        }, status=400)

    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            auth_login(request, user)
            csrf_token = get_token(request)
            # Login status successful.
            return JsonResponse({
                "username": user.username,
                "status": True,
                "message": "Login successful!",
                "csrf_token": csrf_token
                # Add other data if you want to send data to Flutter.
            }, status=200)
        else:
            return JsonResponse({
                "status": False,
                "message": "Login failed, account is disabled."
            }, status=401)

    else:
        return JsonResponse({
            "status": False,
            "message": "Login failed, please check your username or password."
        }, status=401)

@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data['username']
        password1 = data['password1']
        password2 = data['password2']

        # Check if the passwords match
        if password1 != password2:
            return JsonResponse({
                "status": False,
                "message": "Passwords do not match."
            }, status=400)
        
        # Check if the username is already taken
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                "status": False,
                "message": "Username already exists."
            }, status=400)
        
        # Create the new user
        user = User.objects.create_user(username=username, password=password1)
        user.save()
        
        return JsonResponse({
            "username": user.username,
            "status": 'success',
            "message": "User created successfully!"
        }, status=200)
    
    else:
        return JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=400)

@csrf_exempt
def logout(request):
    username = request.user.username
    try:
        auth_logout(request)
        return JsonResponse({
            "username": username,
            "status": True,
            "message": "Logged out successfully!"
        }, status=200)
    except:
        return JsonResponse({
            "status": False,
            "message": "Logout failed."
        }, status=401)

@csrf_exempt
def get_user_data(request):
    if request.user.is_authenticated:
        try:
            # Get user type
            user_type_obj = UserType.objects.get(user=request.user)
            user_type = user_type_obj.user_type

            # Get user profile (customer data)
            profile, created = UserProfile.objects.get_or_create(user=request.user, defaults={'email': request.user.email})

            # Base response data
            response_data = {
                "username": request.user.username,
                "user_type": user_type,
                "email": profile.email or request.user.email,
                "full_name": profile.full_name,
                "phone_number": profile.phone_number,
                "date_of_birth": profile.date_of_birth.isoformat() if profile.date_of_birth else None,
                "address": profile.address,
                "is_superuser": request.user.is_superuser,
                "status": True,
                "message": "User data retrieved successfully!"
            }

            # Add seller-specific data if user is a seller
            if user_type == 'seller':
                try:
                    seller_profile, seller_created = SellerProfile.objects.get_or_create(user=request.user)
                    response_data.update({
                        "business_name": seller_profile.business_name,
                        "business_address": seller_profile.business_address,
                    })
                except Exception as e:
                    # If seller profile fails, still return basic data
                    response_data.update({
                        "business_name": "",
                        "business_address": "",
                    })

            return JsonResponse(response_data, status=200)

        except UserType.DoesNotExist:
            # Default to customer if no type is set
            profile, created = UserProfile.objects.get_or_create(user=request.user, defaults={'email': request.user.email})
            return JsonResponse({
                "username": request.user.username,
                "user_type": "customer",
                "email": profile.email or request.user.email,
                "full_name": profile.full_name,
                "phone_number": profile.phone_number,
                "date_of_birth": profile.date_of_birth.isoformat() if profile.date_of_birth else None,
                "address": profile.address,
                "is_superuser": request.user.is_superuser,
                "status": True,
                "message": "User data retrieved successfully!"
            }, status=200)
    else:
        return JsonResponse({
            "status": False,
            "message": "User not authenticated."
        }, status=401)

@login_required
@csrf_exempt
def update_profile(request):
    if request.method == 'POST':
        try:
            profile, created = UserProfile.objects.get_or_create(user=request.user)

            # Update profile fields
            profile.full_name = request.POST.get('full_name', profile.full_name)
            profile.phone_number = request.POST.get('phone_number', profile.phone_number)
            profile.email = request.POST.get('email', profile.email)
            if request.POST.get('date_of_birth'):
                profile.date_of_birth = request.POST.get('date_of_birth')
            profile.address = request.POST.get('address', profile.address)

            profile.save()

            return JsonResponse({
                "status": True,
                "message": "Profile updated successfully!"
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": False,
                "message": f"Failed to update profile: {str(e)}"
            }, status=400)
    else:
        return JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=405)

@login_required
@csrf_exempt
def get_admin_stats(request):
    """Get admin dashboard statistics for Flutter"""
    if not request.user.is_superuser:
        return JsonResponse({
            "status": False,
            "message": "Access denied. Admin privileges required."
        }, status=403)

    gear_count = Gear.objects.count()
    event_count = Event.objects.filter(date__gte=timezone.now().date()).count()
    post_count = Post.objects.count()
    user_count = User.objects.count()
    arena_count = Arena.objects.count()
    booking_count = Booking.objects.count()

    return JsonResponse({
        "gear_count": gear_count,
        "event_count": event_count,
        "post_count": post_count,
        "user_count": user_count,
        "arena_count": arena_count,
        "booking_count": booking_count,
        "status": True,
        "message": "Admin stats retrieved successfully!"
    }, status=200)

@login_required
@csrf_exempt
def get_users_list(request):
    """Get list of all users for admin"""
    if not request.user.is_superuser:
        return JsonResponse({
            "status": False,
            "message": "Access denied. Admin privileges required."
        }, status=403)

    users = User.objects.all().order_by('-date_joined')
    user_data = []

    for user in users:
        try:
            user_type_obj = UserType.objects.get(user=user)
            user_type = user_type_obj.user_type
        except UserType.DoesNotExist:
            user_type = "customer"

        try:
            profile = UserProfile.objects.get(user=user)
            full_name = profile.full_name
            phone = profile.phone_number
            address = profile.address
        except UserProfile.DoesNotExist:
            full_name = ""
            phone = ""
            address = ""

        user_data.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "date_joined": user.date_joined.isoformat(),
            "user_type": user_type,
            "full_name": full_name,
            "phone_number": phone,
            "address": address,
        })

    return JsonResponse({
        "users": user_data,
        "status": True,
        "message": "Users list retrieved successfully!"
    }, status=200)

@login_required
@csrf_exempt
def update_user(request, user_id):
    """Update user details for admin"""
    if not request.user.is_superuser:
        return JsonResponse({
            "status": False,
            "message": "Access denied. Admin privileges required."
        }, status=403)

    if request.method != 'POST':
        return JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=405)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({
            "status": False,
            "message": "User not found."
        }, status=404)

@login_required
@csrf_exempt
def get_arenas_admin(request):
    """Get list of all arenas for admin"""
    if not request.user.is_superuser:
        return JsonResponse({
            "status": False,
            "message": "Access denied. Admin privileges required."
        }, status=403)

    arenas = Arena.objects.all()
    data = []
    for arena in arenas:
        data.append({
            "id": str(arena.id),
            "name": arena.name,
            "description": arena.description,
            "capacity": arena.capacity,
            "location": arena.location,
            "img_url": arena.img_url,
            "opening_hours_text": arena.opening_hours_text,
            "google_maps_url": arena.google_maps_url,
        })

    return JsonResponse({
        "arenas": data,
        "status": True,
        "message": "Arenas list retrieved successfully!"
    }, status=200)

@login_required
@csrf_exempt
def create_arena_admin(request):
    """Create new arena for admin"""
    if not request.user.is_superuser:
        return JsonResponse({
            "status": False,
            "message": "Access denied. Admin privileges required."
        }, status=403)

    if request.method != 'POST':
        return JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=405)

    try:
        data = json.loads(request.body)
        arena = Arena.objects.create(
            name=data['name'],
            description=data['description'],
            capacity=data['capacity'],
            location=data['location'],
            img_url=data.get('img_url'),
            opening_hours_text=data.get('opening_hours_text'),
            google_maps_url=data.get('google_maps_url'),
        )
        return JsonResponse({
            "status": True,
            "message": "Arena created successfully!",
            "arena_id": str(arena.id)
        }, status=201)
    except Exception as e:
        return JsonResponse({
            "status": False,
            "message": f"Failed to create arena: {str(e)}"
        }, status=400)

@login_required
@csrf_exempt
def update_arena_admin(request, arena_id):
    """Update arena for admin"""
    if not request.user.is_superuser:
        return JsonResponse({
            "status": False,
            "message": "Access denied. Admin privileges required."
        }, status=403)

    if request.method != 'POST':
        return JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=405)

    try:
        arena = Arena.objects.get(id=arena_id)
        data = json.loads(request.body)

        arena.name = data.get('name', arena.name)
        arena.description = data.get('description', arena.description)
        arena.capacity = data.get('capacity', arena.capacity)
        arena.location = data.get('location', arena.location)
        arena.img_url = data.get('img_url', arena.img_url)
        arena.opening_hours_text = data.get('opening_hours_text', arena.opening_hours_text)
        arena.google_maps_url = data.get('google_maps_url', arena.google_maps_url)
        arena.save()

        return JsonResponse({
            "status": True,
            "message": "Arena updated successfully!"
        }, status=200)
    except Arena.DoesNotExist:
        return JsonResponse({
            "status": False,
            "message": "Arena not found."
        }, status=404)

@login_required
@csrf_exempt
def get_bookings_admin(request):
    """Get list of all bookings for admin"""
    if not request.user.is_superuser:
        return JsonResponse({
            "status": False,
            "message": "Access denied. Admin privileges required."
        }, status=403)

    bookings = Booking.objects.all().select_related('user', 'arena').order_by('-booked_at')
    data = []
    for booking in bookings:
        data.append({
            "id": str(booking.id),
            "arena_name": booking.arena.name,
            "user_username": booking.user.username,
            "user_full_name": booking.user.userprofile.full_name if hasattr(booking.user, 'userprofile') and booking.user.userprofile.full_name else booking.user.username,
            "date": str(booking.date),
            "start_hour": booking.start_hour,
            "status": booking.status,
            "activity": booking.activity,
            "booked_at": booking.booked_at.isoformat(),
        })

    return JsonResponse({
        "bookings": data,
        "status": True,
        "message": "Bookings list retrieved successfully!"
    }, status=200)

@login_required
@csrf_exempt
def update_booking_admin(request, booking_id):
    """Update booking status for admin"""
    if not request.user.is_superuser:
        return JsonResponse({
            "status": False,
            "message": "Access denied. Admin privileges required."
        }, status=403)

    if request.method != 'POST':
        return JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=405)

    try:
        booking = Booking.objects.get(id=booking_id)
        data = json.loads(request.body)

        booking.status = data.get('status', booking.status)
        booking.save()

        return JsonResponse({
            "status": True,
            "message": "Booking updated successfully!"
        }, status=200)
    except Booking.DoesNotExist:
        return JsonResponse({
            "status": False,
            "message": "Booking not found."
        }, status=404)
    except Exception as e:
        return JsonResponse({
            "status": False,
            "message": f"Failed to update booking: {str(e)}"
        }, status=400)

@login_required
@csrf_exempt
def get_events_admin(request):
    """Get list of all events for admin"""
    if not request.user.is_superuser:
        return JsonResponse({
            "status": False,
            "message": "Access denied. Admin privileges required."
        }, status=403)

    events = Event.objects.all().order_by('-created_at')
    data = []
    for event in events:
        data.append({
            "id": event.id,
            "name": event.name,
            "category": event.category,
            "level": event.level,
            "description": event.description,
            "date": str(event.date),
            "start_time": str(event.start_time),
            "end_time": str(event.end_time),
            "location": event.location,
            "price": str(event.price),
            "max_participants": event.max_participants,
            "current_participants": event.current_participants,
            "organizer": event.organizer,
            "instructor": event.instructor,
            "is_active": event.is_active,
            "created_at": event.created_at.isoformat(),
        })

    return JsonResponse({
        "events": data,
        "status": True,
        "message": "Events list retrieved successfully!"
    }, status=200)

@login_required
@csrf_exempt
def create_event_admin(request):
    """Create new event for admin"""
    if not request.user.is_superuser:
        return JsonResponse({
            "status": False,
            "message": "Access denied. Admin privileges required."
        }, status=403)

    if request.method != 'POST':
        return JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=405)

    try:
        data = json.loads(request.body)
        from django.utils.text import slugify
        event = Event.objects.create(
            name=data['name'],
            slug=slugify(data['name']),
            category=data.get('category', 'social'),
            level=data.get('level', 'all'),
            description=data['description'],
            requirements=data.get('requirements', ''),
            date=data['date'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            location=data.get('location', 'Main Arena'),
            price=data.get('price', 0),
            max_participants=data.get('max_participants', 30),
            organizer=data.get('organizer', ''),
            instructor=data.get('instructor', ''),
            is_active=data.get('is_active', True),
        )
        return JsonResponse({
            "status": True,
            "message": "Event created successfully!",
            "event_id": event.id
        }, status=201)
    except Exception as e:
        return JsonResponse({
            "status": False,
            "message": f"Failed to create event: {str(e)}"
        }, status=400)

@login_required
@csrf_exempt
def update_event_admin(request, event_id):
    """Update event for admin"""
    if not request.user.is_superuser:
        return JsonResponse({
            "status": False,
            "message": "Access denied. Admin privileges required."
        }, status=403)

    if request.method != 'POST':
        return JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=405)

    try:
        event = Event.objects.get(id=event_id)
        data = json.loads(request.body)

        event.name = data.get('name', event.name)
        event.category = data.get('category', event.category)
        event.level = data.get('level', event.level)
        event.description = data.get('description', event.description)
        event.requirements = data.get('requirements', event.requirements)
        event.date = data.get('date', event.date)
        event.start_time = data.get('start_time', event.start_time)
        event.end_time = data.get('end_time', event.end_time)
        event.location = data.get('location', event.location)
        event.price = data.get('price', event.price)
        event.max_participants = data.get('max_participants', event.max_participants)
        event.organizer = data.get('organizer', event.organizer)
        event.instructor = data.get('instructor', event.instructor)
        event.is_active = data.get('is_active', event.is_active)
        event.save()

        return JsonResponse({
            "status": True,
            "message": "Event updated successfully!"
        }, status=200)
    except Event.DoesNotExist:
        return JsonResponse({
            "status": False,
            "message": "Event not found."
        }, status=404)

@login_required
@csrf_exempt
def get_posts_admin(request):
    """Get list of all posts for admin"""
    if not request.user.is_superuser:
        return JsonResponse({
            "status": False,
            "message": "Access denied. Admin privileges required."
        }, status=403)

    posts = Post.objects.all().select_related('author').order_by('-created_at')
    data = []
    for post in posts:
        data.append({
            "id": post.id,
            "author_username": post.author.username if post.author else "Anonymous",
            "title": post.title,
            "content": post.content[:200] + "..." if len(post.content) > 200 else post.content,
            "thumbnail_url": post.thumbnail_url,
            "total_upvotes": post.total_upvotes(),
            "total_downvotes": post.total_downvotes(),
            "replies_count": post.replies.count(),
            "created_at": post.created_at.isoformat(),
        })

    return JsonResponse({
        "posts": data,
        "status": True,
        "message": "Posts list retrieved successfully!"
    }, status=200)

@login_required
@csrf_exempt
def delete_post_admin(request, post_id):
    """Delete post for admin"""
    if not request.user.is_superuser:
        return JsonResponse({
            "status": False,
            "message": "Access denied. Admin privileges required."
        }, status=403)

    if request.method not in ['DELETE', 'POST']:
        return JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=405)

    try:
        post = Post.objects.get(id=post_id)
        post.delete()
        return JsonResponse({
            "status": True,
            "message": "Post deleted successfully!"
        }, status=200)
    except Post.DoesNotExist:
        return JsonResponse({
            "status": False,
            "message": "Post not found."
        }, status=404)

@login_required
@csrf_exempt
def get_replies_admin(request):
    """Get list of all replies for admin"""
    if not request.user.is_superuser:
        return JsonResponse({
            "status": False,
            "message": "Access denied. Admin privileges required."
        }, status=403)

    replies = Reply.objects.all().select_related('author', 'post').order_by('-created_at')
    data = []
    for reply in replies:
        data.append({
            "id": reply.id,
            "post_title": reply.post.title,
            "author_username": reply.author.username,
            "content": reply.content[:200] + "..." if len(reply.content) > 200 else reply.content,
            "total_upvotes": reply.total_upvotes(),
            "total_downvotes": reply.total_downvotes(),
            "created_at": reply.created_at.isoformat(),
        })

    return JsonResponse({
        "replies": data,
        "status": True,
        "message": "Replies list retrieved successfully!"
    }, status=200)

@login_required
@csrf_exempt
def delete_reply_admin(request, reply_id):
    """Delete reply for admin"""
    if not request.user.is_superuser:
        return JsonResponse({
            "status": False,
            "message": "Access denied. Admin privileges required."
        }, status=403)

    if request.method not in ['DELETE', 'POST']:
        return JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=405)

    try:
        reply = Reply.objects.get(id=reply_id)
        reply.delete()
        return JsonResponse({
            "status": True,
            "message": "Reply deleted successfully!"
        }, status=200)
    except Reply.DoesNotExist:
        return JsonResponse({
            "status": False,
            "message": "Reply not found."
        }, status=404)

@login_required
@csrf_exempt
def get_gears_admin(request):
    """Get list of all gears for admin"""
    if not request.user.is_superuser:
        return JsonResponse({
            "status": False,
            "message": "Access denied. Admin privileges required."
        }, status=403)

    gears = Gear.objects.all().select_related('seller').order_by('-id')
    data = []
    for gear in gears:
        data.append({
            "id": gear.id,
            "name": gear.name,
            "category": gear.category,
            "price_per_day": str(gear.price_per_day),
            "image_url": gear.image_url,
            "description": gear.description,
            "stock": gear.stock,
            "seller_username": gear.seller.username,
            "is_featured": gear.is_featured,
        })

    return JsonResponse({
        "gears": data,
        "status": True,
        "message": "Gears list retrieved successfully!"
    }, status=200)

@login_required
@csrf_exempt
def delete_gear_admin(request, gear_id):
    """Delete gear for admin"""
    if not request.user.is_superuser:
        return JsonResponse({
            "status": False,
            "message": "Access denied. Admin privileges required."
        }, status=403)

    if request.method != 'DELETE':
        return JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=405)

    try:
        gear = Gear.objects.get(id=gear_id)
        gear.delete()
        return JsonResponse({
            "status": True,
            "message": "Gear deleted successfully!"
        }, status=200)
    except Gear.DoesNotExist:
        return JsonResponse({
            "status": False,
            "message": "Gear not found."
        }, status=404)
    except Exception as e:
        return JsonResponse({
            "status": False,
            "message": f"Failed to update event: {str(e)}"
        }, status=400)

@login_required
@csrf_exempt
def delete_event_admin(request, event_id):
    """Delete event for admin"""
    if not request.user.is_superuser:
        return JsonResponse({
            "status": False,
            "message": "Access denied. Admin privileges required."
        }, status=403)

    if request.method != 'DELETE':
        return JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=405)

    try:
        event = Event.objects.get(id=event_id)
        event.delete()
        return JsonResponse({
            "status": True,
            "message": "Event deleted successfully!"
        }, status=200)
    except Event.DoesNotExist:
        return JsonResponse({
            "status": False,
            "message": "Event not found."
        }, status=404)
    except Exception as e:
        return JsonResponse({
            "status": False,
            "message": f"Failed to update arena: {str(e)}"
        }, status=400)

@login_required
@csrf_exempt
def delete_arena_admin(request, arena_id):
    """Delete arena for admin"""
    if not request.user.is_superuser:
        return JsonResponse({
            "status": False,
            "message": "Access denied. Admin privileges required."
        }, status=403)

    if request.method != 'DELETE':
        return JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=405)

    try:
        arena = Arena.objects.get(id=arena_id)
        arena.delete()
        return JsonResponse({
            "status": True,
            "message": "Arena deleted successfully!"
        }, status=200)
    except Arena.DoesNotExist:
        return JsonResponse({
            "status": False,
            "message": "Arena not found."
        }, status=404)

    data = json.loads(request.body)

    # Update basic user info
    user.first_name = data.get('first_name', user.first_name)
    user.last_name = data.get('last_name', user.last_name)
    user.email = data.get('email', user.email)
    user.is_active = data.get('is_active', user.is_active)
    user.save()

    # Update user type
    user_type, created = UserType.objects.get_or_create(user=user)
    user_type.user_type = data.get('user_type', user_type.user_type)
    user_type.save()

    # Update profile
    profile, created = UserProfile.objects.get_or_create(user=user)
    profile.full_name = data.get('full_name', profile.full_name)
    profile.phone_number = data.get('phone_number', profile.phone_number)
    profile.address = data.get('address', profile.address)
    profile.save()

    return JsonResponse({
        "status": True,
        "message": "User updated successfully!"
    }, status=200)

@login_required
@csrf_exempt
def delete_user(request, user_id):
    """Delete user for admin"""
    if not request.user.is_superuser:
        return JsonResponse({
            "status": False,
            "message": "Access denied. Admin privileges required."
        }, status=403)

    if request.method not in ['DELETE', 'POST']:
        return JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=405)

    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return JsonResponse({
            "status": True,
            "message": "User deleted successfully!"
        }, status=200)
    except User.DoesNotExist:
        return JsonResponse({
            "status": False,
            "message": "User not found."
        }, status=404)

@login_required
@csrf_exempt
def get_user_type(request):
    """Get user type (customer or seller) for Flutter"""
    try:
        user_type_obj = UserType.objects.get(user=request.user)
        return JsonResponse({
            "user_type": user_type_obj.user_type,
            "status": True,
            "message": "User type retrieved successfully!"
        }, status=200)
    except UserType.DoesNotExist:
        # Default to customer if no type is set
        return JsonResponse({
            "user_type": "customer",
            "status": True,
            "message": "User type retrieved successfully!"
        }, status=200)
    except Exception as e:
        return JsonResponse({
            "status": False,
            "message": f"Failed to retrieve user type: {str(e)}"
        }, status=400)

@login_required
@csrf_exempt
def get_seller_profile(request):
    """Get seller profile data for Flutter"""
    try:
        profile, created = SellerProfile.objects.get_or_create(user=request.user)
        return JsonResponse({
            "business_name": profile.business_name or "",
            "phone_number": profile.phone_number or "",
            "email": profile.email or request.user.email,
            "business_address": profile.business_address or "",
            "status": True,
            "message": "Seller profile retrieved successfully!"
        }, status=200)
    except Exception as e:
        return JsonResponse({
            "status": False,
            "message": f"Failed to retrieve seller profile: {str(e)}"
        }, status=400)

@login_required
@csrf_exempt
def update_seller_profile(request):
    """Update seller profile for Flutter"""
    if request.method == 'POST':
        try:
            profile, created = SellerProfile.objects.get_or_create(user=request.user)

            # Update profile fields
            profile.business_name = request.POST.get('business_name', profile.business_name)
            profile.phone_number = request.POST.get('phone_number', profile.phone_number)
            profile.email = request.POST.get('email', profile.email)
            profile.business_address = request.POST.get('business_address', profile.business_address)

            profile.save()

            return JsonResponse({
                "status": True,
                "message": "Seller profile updated successfully!"
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": False,
                "message": f"Failed to update seller profile: {str(e)}"
            }, status=400)
    else:
        return JsonResponse({
            "status": False,
            "message": "Invalid request method."
        }, status=405)
