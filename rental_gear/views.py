from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from .models import Gear, CartItem, Rental, RentalItem
from .forms import GearForm, AddToCartForm, CheckoutForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.template.loader import render_to_string


def gear_json(request, id):
    gear = get_object_or_404(Gear, id=id, seller=request.user)
    data = {
        'id': gear.id,
        'name': gear.name,
        'category': gear.category,
        'price_per_day': str(gear.price_per_day),
        'stock': gear.stock,
        'description': gear.description,
        'image_url': gear.image_url,
        'image': gear.image_url,
    }
    return JsonResponse(data)

# Create
@login_required
@user_passes_test(lambda u: hasattr(u, 'usertype') and u.usertype.user_type == 'seller')
def create_gear(request):
    if request.method == 'POST':
        form = GearForm(request.POST, request.FILES)
        if form.is_valid():
            gear = form.save(commit=False)
            gear.seller = request.user
            gear.save()
            messages.success(request, 'Equipment berhasil ditambahkan!')
            return redirect('rental_gear:catalog')
    else:
        form = GearForm()
    return render(request, 'rental_gear/gear_form.html', {'form': form, 'action': 'Add'})


def catalog(request):
    gears = Gear.objects.all()
    return render(request, 'catalog.html', {
        'gears': gears
    })


# Update
@login_required
@user_passes_test(lambda u: hasattr(u, 'usertype') and u.usertype.user_type == 'seller')
def update_gear(request, id):
    gear = get_object_or_404(Gear, id=id, seller=request.user)
    if request.method == 'POST':
        form = GearForm(request.POST, request.FILES, instance=gear)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            else:
                messages.success(request, 'Equipment berhasil diupdate!')
                return redirect('rental_gear:catalog')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = GearForm(instance=gear)
    return render(request, 'rental_gear/gear_form.html', {'form': form, 'action': 'Edit'})

# Delete
@login_required
@user_passes_test(lambda u: hasattr(u, 'usertype') and u.usertype.user_type == 'seller')
def delete_gear(request, id):
    gear = get_object_or_404(Gear, id=id, seller=request.user)
    if request.method == 'POST':
        gear.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        else:
            messages.success(request, 'Equipment berhasil dihapus!')
            return redirect('rental_gear:catalog')
    return render(request, 'rental_gear/gear_confirm_delete.html', {'gear': gear})

def filter_gear(request):
    category = request.GET.get('category')
    print("DEBUG CATEGORY:", category) 
    search = request.GET.get('search')
    gears = Gear.objects.all()

    if category:
        gears = gears.filter(category=category)
    if search:
        gears = gears.filter(name__icontains=search)

    return render(request, 'partials/gear_items.html', {'gears': gears})


def gear_detail(request, id):
    gear = get_object_or_404(Gear, id=id)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'id': gear.id,
            'name': gear.name,
            'category': gear.category,
            'price_per_day': str(gear.price_per_day),
            'stock': gear.stock,
            'image_url': gear.image_url,
            'description': gear.description,
        })
    return render(request, 'gear_detail.html', {'gear': gear})


@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.get_total_price() for item in cart_items)

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })



@require_POST
def add_to_cart(request, gear_id):
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'login_required': True,
                'message': 'Silakan login terlebih dahulu untuk menambahkan ke keranjang.'
            }, status=401)
        else:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())

    gear = get_object_or_404(Gear, id=gear_id)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        qty = int(request.POST.get('quantity', 1))
        days = int(request.POST.get('days', 1))
    else:
        try:
            body = json.loads(request.body.decode() or '{}')
            qty = int(body.get('quantity', 1))
            days = int(body.get('days', 1))
        except:
            qty = days = 1

    if days < 1 or days > 30:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': "Durasi rental harus antara 1–30 hari."
            }, status=400)
        else:
            messages.error(request, "Durasi rental harus antara 1–30 hari.")
            return redirect('rental_gear:gear_detail', id=gear_id)

    item, created = CartItem.objects.get_or_create(user=request.user, gear=gear)

    if created:
        item.quantity = qty
        item.days = days
    else:
        item.quantity = qty  # Set to qty instead of adding

    item.save()

    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.get_total_price() for item in cart_items)

    # Jika request AJAX, kirim JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{gear.name} added to cart!',
            'total_items': cart_items.count(),
            'total_price': total_price
        })
    else:
        # fallback untuk normal POST
        messages.success(request, f'{gear.name} added to cart!')
        return redirect('rental_gear:view_cart')

@login_required
@require_POST
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()

    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.get_total_price() for item in cart_items)
    return render(request, 'partials/cart_items.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

@login_required
@transaction.atomic
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)

    if not cart_items.exists():
        messages.warning(request, "Keranjang kamu masih kosong!")
        return redirect('rental_gear:view_cart')

    total = sum(item.get_total_price() for item in cart_items)

    if request.method == "POST":

        for item in cart_items:
            item.delete()

        messages.success(request, f"Checkout berhasil! Total pembayaran: Rp{total}")
        return render(request, 'checkout_success.html', {'total': total})

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total': total
    })

@require_POST
def add_to_cart_ajax(request, gear_id):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'login_required': True,
            'message': 'Silakan login terlebih dahulu untuk menambahkan ke keranjang.'
        }, status=401)

    gear = get_object_or_404(Gear, id=gear_id)

    qty = days = 1
    try:
        qty = int(request.POST.get('quantity', 1))
        days = int(request.POST.get('days', 1))
    except Exception:
        qty = days = 1

    if days < 1 or days > 30:
        return JsonResponse({
            'success': False,
            'message': "Durasi rental harus antara 1–30 hari."
        }, status=400)

    item, created = CartItem.objects.get_or_create(user=request.user, gear=gear)
    if created:
        item.quantity = qty
        item.days = days
    else:
        item.quantity = qty  # Set to qty instead of adding
    item.save()

    cart_items = CartItem.objects.filter(user=request.user)
    html = render_to_string('partials/cart_items.html', {'cart_items': cart_items}, request=request)

    return JsonResponse({
        'success': True,
        'message': f"{gear.name} ditambahkan ke keranjang untuk {days} hari!",
        'cart_html': html,
    })

@csrf_exempt
def remove_from_cart_ajax(request, item_id):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'login_required': True,
            'message': 'Silakan login terlebih dahulu untuk menghapus item dari keranjang.'
        }, status=401)

    from .models import CartItem
    try:
        item = CartItem.objects.get(id=item_id, user=request.user)
        item.delete()
        return JsonResponse({'success': True})
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not found'})


@require_POST
@transaction.atomic
def checkout_ajax(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'login_required': True,
            'message': 'Silakan login terlebih dahulu untuk checkout.'
        }, status=401)

    cart_items = CartItem.objects.filter(user=request.user)

    if not cart_items.exists():
        return JsonResponse({
            'success': False,
            'message': "Keranjang kamu masih kosong!"
        })

    total = sum(item.get_total_price() for item in cart_items)

    # Buat rental baru
    from django.utils import timezone
    rental = Rental.objects.create(
        customer_name=request.user.username,
        user=request.user,
        return_date=timezone.now().date() + timezone.timedelta(days=max(item.days for item in cart_items)),
        total_cost=total
    )

    # Convert cart items ke rental items
    for item in cart_items:
        RentalItem.objects.create(
            rental=rental,
            gear_name=item.gear.name,
            quantity=item.quantity,
            price_per_day_at_checkout=item.gear.price_per_day
        )

        item.delete()

    return JsonResponse({
        'success': True,
        'message': f"Checkout berhasil! Total pembayaran: Rp{total}",
        'total': total,
        'rental_id': rental.id
    })

# Admin views for rental gear
def admin_gear_list(request):
    if not request.session.get('is_admin'):
        return redirect('authentication:login')
    gears = Gear.objects.all()
    return render(request, 'rental_gear/admin_gear_list.html', {'gears': gears})

def admin_gear_create(request):
    if not request.session.get('is_admin'):
        return redirect('authentication:login')
    if request.method == 'POST':
        form = GearForm(request.POST, request.FILES)
        if form.is_valid():
            gear = form.save(commit=False)
            # If no seller selected, create system admin user
            if not gear.seller:
                from django.contrib.auth.models import User
                from authentication.models import UserType
                system_user, created = User.objects.get_or_create(
                    username='system_admin',
                    defaults={'email': 'admin@therink.com', 'first_name': 'System', 'last_name': 'Admin'}
                )
                if created:
                    UserType.objects.create(user=system_user, user_type='seller')
                gear.seller = system_user
            gear.save()
            messages.success(request, 'Gear created successfully!')
            return redirect('rental_gear:admin_gear_list')
    else:
        form = GearForm()
    return render(request, 'rental_gear/admin_gear_form.html', {'form': form, 'action': 'Create'})

def admin_gear_update(request, id):
    if not request.session.get('is_admin'):
        return redirect('authentication:login')
    gear = get_object_or_404(Gear, id=id)
    if request.method == 'POST':
        form = GearForm(request.POST, request.FILES, instance=gear)
        if form.is_valid():
            form.save()
            messages.success(request, 'Gear updated successfully!')
            return redirect('rental_gear:admin_gear_list')
    else:
        form = GearForm(instance=gear)
    return render(request, 'rental_gear/admin_gear_form.html', {'form': form, 'action': 'Update'})

def admin_gear_delete(request, id):
    if not request.session.get('is_admin'):
        return redirect('authentication:login')
    gear = get_object_or_404(Gear, id=id)
    if request.method == 'POST':
        gear.delete()
        messages.success(request, 'Gear deleted successfully!')
        return redirect('rental_gear:admin_gear_list')
    return render(request, 'rental_gear/admin_gear_confirm_delete.html', {'gear': gear})
