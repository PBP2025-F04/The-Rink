from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from .models import UserProfile, SellerProfile, UserType
from .forms import UserProfileForm, SellerProfileForm, CustomUserCreationForm
from rental_gear.models import Gear

# Create your views here.
@csrf_exempt
def register(request):
    form = CustomUserCreationForm()

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user_type = form.cleaned_data['user_type']
            UserType.objects.create(user=user, user_type=user_type)
            UserProfile.objects.create(user=user, email=user.email)
            if user_type == 'seller':
                SellerProfile.objects.create(user=user)
            messages.success(request, 'Akun Anda telah berhasil dibuat!')
            return redirect('authentication:login')
    context = {'form':form}
    return render(request, 'register.html', context)

@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check for hardcoded admin credentials
        if username == 'cbkadal' and password == 'dikadalin':
            request.session['is_admin'] = True
            # Create a dummy user object for admin
            from django.contrib.auth.models import AnonymousUser
            request.user = AnonymousUser()
            return redirect('authentication:dashadmin')

        # Clear admin session for regular users
        if 'is_admin' in request.session:
            del request.session['is_admin']

        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            next_url = request.GET.get('next') or request.POST.get('next') or '/rental/'
            return redirect(next_url)

    else:
        form = AuthenticationForm(request)

    context = {'form': form}
    return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    request.session.flush()  # Clear all session data including admin session
    return redirect('authentication:login')

@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            else:
                return redirect('authentication:profile')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
            else:
                return render(request, 'userprofile.html', {'form': form, 'profile': user_profile})
    else:
        form = UserProfileForm(instance=user_profile)
    # Add cleaned full_name for display
    full_name_display = user_profile.full_name.strip() if user_profile.full_name else ''
    context = {'form': form, 'profile': user_profile, 'full_name_display': full_name_display}
    return render(request, 'userprofile.html', context)

@login_required
def seller_profile(request):
    seller_profile, created = SellerProfile.objects.get_or_create(user=request.user)
    user_products = Gear.objects.filter(seller=request.user)
    if request.method == 'POST':
        form = SellerProfileForm(request.POST, instance=seller_profile)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            else:
                return redirect('authentication:seller_profile')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
            else:
                return render(request, 'sellerprofile.html', {'form': form, 'profile': seller_profile, 'user_products': user_products})
    else:
        form = SellerProfileForm(instance=seller_profile)
    return render(request, 'sellerprofile.html', {'form': form, 'profile': seller_profile, 'user_products': user_products})

def admin_user_list(request):
    if not request.session.get('is_admin'):
        return redirect('authentication:login')

    users = User.objects.all().order_by('-date_joined')
    user_types = UserType.objects.all()
    user_profiles = UserProfile.objects.all()
    seller_profiles = SellerProfile.objects.all()

    # Create a dictionary to map user to their type and profiles
    user_data = {}
    for user in users:
        user_data[user.id] = {
            'user': user,
            'user_type': user_types.filter(user=user).first(),
            'user_profile': user_profiles.filter(user=user).first(),
            'seller_profile': seller_profiles.filter(user=user).first(),
        }

    context = {
        'user_data': user_data,
    }
    return render(request, 'authentication/admin_user_list.html', context)

def admin_user_update(request, user_id):
    if not request.session.get('is_admin'):
        return redirect('authentication:login')

    user = get_object_or_404(User, id=user_id)
    user_type = UserType.objects.filter(user=user).first()
    user_profile = UserProfile.objects.filter(user=user).first()
    seller_profile = SellerProfile.objects.filter(user=user).first()

    if request.method == 'POST':
        # Handle user basic info
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()

        # Handle user type
        if user_type:
            user_type.user_type = request.POST.get('user_type', 'customer')
            user_type.save()
        else:
            UserType.objects.create(user=user, user_type=request.POST.get('user_type', 'customer'))

        # Handle user profile
        if user_profile:
            user_profile.full_name = request.POST.get('full_name', '')
            user_profile.phone_number = request.POST.get('phone_number', '')
            user_profile.address = request.POST.get('address', '')
            user_profile.save()
        else:
            UserProfile.objects.create(
                user=user,
                email=user.email,
                full_name=request.POST.get('full_name', ''),
                phone_number=request.POST.get('phone_number', ''),
                address=request.POST.get('address', ''),
            )

        # Handle seller profile if user is seller
        if request.POST.get('user_type') == 'seller':
            if seller_profile:
                seller_profile.business_name = request.POST.get('business_name', '')
                seller_profile.phone_number = request.POST.get('phone_number', '')
                seller_profile.business_address = request.POST.get('business_address', '')
                seller_profile.save()
            else:
                SellerProfile.objects.create(
                    user=user,
                    business_name=request.POST.get('business_name', ''),
                    phone_number=request.POST.get('phone_number', ''),
                    business_address=request.POST.get('business_address', ''),
                )

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('authentication:admin_user_list')

    context = {
        'user': user,
        'user_type': user_type,
        'user_profile': user_profile,
        'seller_profile': seller_profile,
    }
    return render(request, 'authentication/admin_user_form.html', context)

def admin_user_delete(request, user_id):
    if not request.session.get('is_admin'):
        return redirect('authentication:login')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('authentication:admin_user_list')

    context = {
        'user': user,
    }
    return render(request, 'authentication/admin_user_confirm_delete.html', context)

def dashadmin(request):
    if not request.session.get('is_admin'):
        return redirect('authentication:login')

    # Get counts for system overview
    from rental_gear.models import Gear
    from events.models import Event
    from forum.models import Post
    from django.contrib.auth.models import User

    gear_count = Gear.objects.count()
    event_count = Event.objects.filter(date__gte=timezone.now().date()).count()
    post_count = Post.objects.count()
    user_count = User.objects.count()

    context = {
        'gear_count': gear_count,
        'event_count': event_count,
        'post_count': post_count,
        'user_count': user_count,
    }

    return render(request, 'dashadmin.html', context)
