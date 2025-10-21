from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import transaction  # Impor transaction
from .models import Gear, CartItem


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

def gear_detail(request, id):
    gear = get_object_or_404(Gear, id=id)
    return render(request, 'rental_gear/gear_detail.html', {'gear': gear})


@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    return render(request, 'rental_gear/cart.html', {'cart_items': cart_items})

@login_required
@require_POST
def add_to_cart(request, gear_id):
    gear = get_object_or_404(Gear, id=gear_id)
    item, created = CartItem.objects.get_or_create(user=request.user, gear=gear)
    
    if not created:
        item.quantity += 1
    
    item.save()
    
    cart_items = CartItem.objects.filter(user=request.user)
    return render(request, 'rental_gear/partials/cart_items.html', {
        'cart_items': cart_items
    })

@login_required
@require_POST 
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user) 
    item.delete()
    
    cart_items = CartItem.objects.filter(user=request.user)
    return render(request, 'rental/partials/cart_items.html', {'cart_items': cart_items})

@login_required
@transaction.atomic
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    
    if not cart_items.exists():
        messages.warning(request, "Keranjang kamu masih kosong!")
        return redirect('cart') 

    total = sum(item.get_total_price() for item in cart_items)

    if request.method == "POST":
        
        for item in cart_items:
            if item.gear.stock < item.quantity:
                messages.error(request, f"Stok untuk '{item.gear.name}' tidak mencukupi (tersisa {item.gear.stock}).")
                return render(request, 'rental_gear/checkout.html', {
                    'cart_items': cart_items,
                    'total': total
                })

        for item in cart_items:
            gear = item.gear
            gear.stock -= item.quantity
            gear.save()
            item.delete() 

        messages.success(request, f"Checkout berhasil! Total pembayaran: Rp{total}")
        return render(request, 'rental_gear/checkout_success.html', {'total': total})
    
    return render(request, 'rental_gear/checkout.html', {
        'cart_items': cart_items,
        'total': total
    })