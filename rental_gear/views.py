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
from django.core import serializers


# ============ Flutter JSON Endpoints ============

@csrf_exempt
def get_gears_json(request):
    """Get all gears for Flutter - JSON format with proper data types"""
    gears = Gear.objects.all()
    data = []
    for gear in gears:
        data.append({
            'id': gear.id,
            'name': gear.name,
            'category': gear.category,
            'price_per_day': float(gear.price_per_day),  # Decimal to float
            'stock': gear.stock,  # int
            'description': gear.description or '',  # Ensure string, not null
            'image_url': gear.image_url or '',  # Ensure string, not null
            'seller_id': gear.seller.id,  # int
            'seller_username': gear.seller.username,  # string
            'is_featured': gear.is_featured,  # bool
        })
    return JsonResponse(data, safe=False)


@csrf_exempt
def get_gear_detail_json(request, id):
    """Get single gear detail for Flutter - JSON format"""
    try:
        gear = get_object_or_404(Gear, id=id)
        data = {
            'id': gear.id,
            'name': gear.name,
            'category': gear.category,
            'price_per_day': float(gear.price_per_day),
            'stock': gear.stock,
            'description': gear.description or '',
            'image_url': gear.image_url or '',
            'seller_id': gear.seller.id,
            'seller_username': gear.seller.username,
            'is_featured': gear.is_featured,
        }
        return JsonResponse(data)
    except Gear.DoesNotExist:
        return JsonResponse({'error': 'Gear not found'}, status=404)


@csrf_exempt
@login_required
def get_cart_json(request):
    """Get user's cart items for Flutter"""
    cart_items = CartItem.objects.filter(user=request.user).select_related('gear')
    data = []
    total_price = 0
    
    for item in cart_items:
        item_total = float(item.get_total_price())
        total_price += item_total
        data.append({
            'id': item.id,
            'gear_id': item.gear.id,
            'gear_name': item.gear.name,
            'gear_image_url': item.gear.image_url or '',
            'price_per_day': float(item.gear.price_per_day),
            'quantity': item.quantity,
            'days': item.days,
            'subtotal': item_total,
            'stock_available': item.gear.stock,
        })
    
    return JsonResponse({
        'cart_items': data,
        'total_price': total_price,
        'total_items': len(data)
    })


@csrf_exempt
@login_required
def add_to_cart_flutter(request):
    """Add item to cart from Flutter"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        gear_id = int(data.get('gear_id'))
        quantity = int(data.get('quantity', 1))
        days = int(data.get('days', 1))
        
        if quantity < 1:
            return JsonResponse({'success': False, 'message': 'Quantity must be at least 1'}, status=400)
        
        if days < 1 or days > 30:
            return JsonResponse({'success': False, 'message': 'Days must be between 1-30'}, status=400)
        
        gear = get_object_or_404(Gear, id=gear_id)
        
        if quantity > gear.stock:
            return JsonResponse({
                'success': False, 
                'message': f'Stock not available. Only {gear.stock} items left'
            }, status=400)
        
        item, created = CartItem.objects.get_or_create(
            user=request.user, 
            gear=gear,
            defaults={'quantity': quantity, 'days': days}
        )
        
        if not created:
            item.quantity = quantity
            item.days = days
            item.save()
        
        return JsonResponse({
            'success': True,
            'message': f'{gear.name} added to cart',
            'cart_item_id': item.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@csrf_exempt
@login_required
def update_cart_item_flutter(request, item_id):
    """Update cart item quantity/days from Flutter"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        item = get_object_or_404(CartItem, id=item_id, user=request.user)
        
        if 'quantity' in data:
            quantity = int(data['quantity'])
            if quantity < 1:
                return JsonResponse({'success': False, 'message': 'Quantity must be at least 1'}, status=400)
            if quantity > item.gear.stock:
                return JsonResponse({
                    'success': False,
                    'message': f'Stock not available. Only {item.gear.stock} items left'
                }, status=400)
            item.quantity = quantity
        
        if 'days' in data:
            days = int(data['days'])
            if days < 1 or days > 30:
                return JsonResponse({'success': False, 'message': 'Days must be between 1-30'}, status=400)
            item.days = days
        
        item.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Cart updated',
            'subtotal': float(item.get_total_price())
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@csrf_exempt
@login_required
def remove_from_cart_flutter(request, item_id):
    """Remove item from cart for Flutter"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    
    try:
        item = get_object_or_404(CartItem, id=item_id, user=request.user)
        gear_name = item.gear.name
        item.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'{gear_name} removed from cart'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@csrf_exempt
@login_required
@transaction.atomic
def checkout_flutter(request):
    """Checkout cart items for Flutter"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    
    try:
        cart_items = CartItem.objects.filter(user=request.user).select_related('gear')
        
        if not cart_items.exists():
            return JsonResponse({
                'success': False,
                'message': 'Cart is empty'
            }, status=400)
        
        # Calculate total and max days
        total = 0
        max_days = 0
        rental_items_data = []
        
        for item in cart_items:
            if item.quantity > item.gear.stock:
                return JsonResponse({
                    'success': False,
                    'message': f'Insufficient stock for {item.gear.name}'
                }, status=400)
            
            subtotal = float(item.get_total_price())
            total += subtotal
            max_days = max(max_days, item.days)
            
            rental_items_data.append({
                'gear_name': item.gear.name,
                'quantity': item.quantity,
                'days': item.days,
                'price_per_day': float(item.gear.price_per_day),
                'subtotal': subtotal
            })
        
        # Create rental
        from datetime import timedelta
        rental = Rental.objects.create(
            customer_name=request.user.username,
            user=request.user,
            return_date=timezone.now().date() + timedelta(days=max_days),
            total_cost=total
        )
        
        # Create rental items
        for item in cart_items:
            RentalItem.objects.create(
                rental=rental,
                gear_name=item.gear.name,
                quantity=item.quantity,
                price_per_day_at_checkout=item.gear.price_per_day
            )
            
            # Reduce stock
            item.gear.stock -= item.quantity
            item.gear.save()
        
        # Clear cart
        cart_items.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Checkout successful',
            'rental_id': rental.id,
            'total_cost': total,
            'return_date': rental.return_date.isoformat(),
            'items': rental_items_data
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@csrf_exempt
@login_required
def get_rentals_json(request):
    """Get user's rental history for Flutter"""
    rentals = Rental.objects.filter(user=request.user).prefetch_related('items').order_by('-rental_date')
    data = []
    
    for rental in rentals:
        items = []
        for item in rental.items.all():
            items.append({
                'gear_name': item.gear_name,
                'quantity': item.quantity,
                'price_per_day': float(item.price_per_day_at_checkout),
                'subtotal': float(item.get_subtotal())
            })
        
        data.append({
            'id': rental.id,
            'customer_name': rental.customer_name,
            'rental_date': rental.rental_date.isoformat(),
            'return_date': rental.return_date.isoformat(),
            'total_cost': float(rental.total_cost),
            'items': items
        })
    
    return JsonResponse({'rentals': data})


@csrf_exempt
@login_required
@user_passes_test(lambda u: hasattr(u, 'usertype') and u.usertype.user_type == 'seller')
def create_gear_flutter(request):
    """Create gear from Flutter (seller only)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['name', 'category', 'price_per_day', 'stock']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }, status=400)
        
        # Validate category
        valid_categories = ['hockey', 'curling', 'ice_skating', 'apparel', 'accessories', 'protective_gear', 'other']
        if data['category'] not in valid_categories:
            return JsonResponse({
                'success': False,
                'message': f'Invalid category. Must be one of: {", ".join(valid_categories)}'
            }, status=400)
        
        gear = Gear.objects.create(
            name=data['name'],
            category=data['category'],
            price_per_day=float(data['price_per_day']),
            stock=int(data['stock']),
            description=data.get('description', ''),
            image_url=data.get('image_url', ''),
            seller=request.user,
            is_featured=data.get('is_featured', False)
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Gear created successfully',
            'gear_id': gear.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@csrf_exempt
@login_required
@user_passes_test(lambda u: hasattr(u, 'usertype') and u.usertype.user_type == 'seller')
def update_gear_flutter(request, id):
    """Update gear from Flutter (seller only)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    
    try:
        gear = get_object_or_404(Gear, id=id, seller=request.user)
        data = json.loads(request.body)
        
        # Update fields if provided
        if 'name' in data:
            gear.name = data['name']
        if 'category' in data:
            valid_categories = ['hockey', 'curling', 'ice_skating', 'apparel', 'accessories', 'protective_gear', 'other']
            if data['category'] not in valid_categories:
                return JsonResponse({
                    'success': False,
                    'message': f'Invalid category. Must be one of: {", ".join(valid_categories)}'
                }, status=400)
            gear.category = data['category']
        if 'price_per_day' in data:
            gear.price_per_day = float(data['price_per_day'])
        if 'stock' in data:
            gear.stock = int(data['stock'])
        if 'description' in data:
            gear.description = data['description']
        if 'image_url' in data:
            gear.image_url = data['image_url']
        if 'is_featured' in data:
            gear.is_featured = bool(data['is_featured'])
        
        gear.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Gear updated successfully'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@csrf_exempt
@login_required
@user_passes_test(lambda u: hasattr(u, 'usertype') and u.usertype.user_type == 'seller')
def delete_gear_flutter(request, id):
    """Delete gear from Flutter (seller only)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)
    
    try:
        gear = get_object_or_404(Gear, id=id, seller=request.user)
        gear_name = gear.name
        gear.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'{gear_name} deleted successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@csrf_exempt
@login_required
@user_passes_test(lambda u: hasattr(u, 'usertype') and u.usertype.user_type == 'seller')
def get_seller_gears_json(request):
    """Get seller's own gears for Flutter"""
    gears = Gear.objects.filter(seller=request.user)
    data = []
    
    for gear in gears:
        data.append({
            'id': gear.id,
            'name': gear.name,
            'category': gear.category,
            'price_per_day': float(gear.price_per_day),
            'stock': gear.stock,
            'description': gear.description or '',
            'image_url': gear.image_url or '',
            'is_featured': gear.is_featured,
        })
    
    return JsonResponse({'gears': data})


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
            return redirect('authentication:seller_profile')
    else:
        form = GearForm()
    return render(request, 'rental_gear/seller_gear_form.html', {'form': form, 'action': 'Add'})


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
            gear = form.save(commit=False)
            gear.seller = request.user
            gear.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            else:
                messages.success(request, 'Equipment berhasil diupdate!')
                return redirect('authentication:seller_profile')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = GearForm(instance=gear)
    return render(request, 'rental_gear/seller_gear_form.html', {'form': form, 'action': 'Edit'})

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
            return redirect('authentication:seller_profile')
    return render(request, 'rental_gear/seller_gear_confirm_delete.html', {'gear': gear})

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
