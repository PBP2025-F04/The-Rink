from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from .models import Gear, CartItem
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CartItem


def catalog(request):
    gears = Gear.objects.all()
    return render(request, 'rental/catalog.html', {'gears': gears})

def filter_gear(request):
    category = request.GET.get('category')
    if category:
        gears = Gear.objects.filter(category=category)
    else:
        gears = Gear.objects.all()
    return render(request, 'rental/partials/gear_items.html', {'gears': gears})

# cart
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    return render(request, 'rental_gear/cart.html', {'cart_items': cart_items})

def add_to_cart(request, gear_id):
    gear = get_object_or_404(Gear, id=gear_id)
    item, created = CartItem.objects.get_or_create(user=request.user, gear=gear)
    item.quantity += 1
    item.save()
    return render(request, 'rental_gear/partials/cart_items.html', {
        'cart_items': CartItem.objects.filter(user=request.user)
    })


def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    return render(request, 'rental/partials/cart_items.html', {'cart_items': CartItem.objects.all()})

def gear_detail(request, id):
    gear = get_object_or_404(Gear, id=id)
    return render(request, 'rental_gear/gear_detail.html', {'gear': gear})

@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    
    if not cart_items.exists():
        messages.warning(request, "Keranjang kamu masih kosong!")
        return redirect('cart')  
    
    total = sum(item.get_total_price() for item in cart_items)

    if request.method == "POST":
        for item in cart_items:
            gear = item.gear
            if gear.stock >= item.quantity:
                gear.stock -= item.quantity
                gear.save()
            item.delete() 

        messages.success(request, f"Checkout berhasil! Total pembayaran: Rp{total}")
        return render(request, 'rental_gear/checkout_success.html', {'total': total})

    return render(request, 'rental_gear/checkout.html', {
        'cart_items': cart_items,
        'total': total
    })
