from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
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
      form = AuthenticationForm(data=request.POST)

      if form.is_valid():
            user = form.get_user()
            login(request, user)

            return redirect('/rental/')

   else:
      form = AuthenticationForm(request)
   context = {'form': form}
   return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
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
    return render(request, 'userprofile.html', {'form': form, 'profile': user_profile})

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
