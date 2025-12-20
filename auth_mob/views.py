from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.models import User
from django.contrib.auth import logout as auth_logout
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from authentication.models import UserProfile, SellerProfile, UserType

@csrf_exempt
def login(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            auth_login(request, user)
            # Login status successful.
            return JsonResponse({
                "username": user.username,
                "status": True,
                "message": "Login successful!"
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
