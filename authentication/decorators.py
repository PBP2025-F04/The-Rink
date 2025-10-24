from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def seller_required(view_func):
    """
    Decorator kustom yang memeriksa apakah pengguna sudah login DAN 
    merupakan seorang 'seller'.
    Jika login tapi bukan seller, redirect ke 'main' dengan pesan error.
    Jika belum login, redirect ke halaman login.
    """
    @wraps(view_func)
    @login_required(login_url='authentication:login') 
    def _wrapped_view(request, *args, **kwargs):        
        is_seller = hasattr(request.user, 'usertype') and request.user.usertype.user_type == 'seller'
        
        if is_seller:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "You do not have permission to access this page. You must be a seller.")
            return redirect('main') 
    return _wrapped_view
