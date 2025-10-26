# File: booking_arena/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.dateparse import parse_date
from django.utils import timezone
from django.db.models import Q
from django.db import transaction, IntegrityError
from django.http import HttpRequest
from .models import Arena, Booking, ArenaOpeningHours
from .forms import ArenaForm 
import datetime
import re

# ============================================
# HELPER FUNCTIONS
# ============================================

def is_superuser(user):
    return user.is_superuser

# ============================================
# VIEWS RENDERING FULL PAGES
# ============================================

def show_arena(request):
    location_query = request.GET.get('location', '').strip()
    arenas = Arena.objects.all()
    if location_query:
        arenas = arenas.filter(Q(location__icontains=location_query) | Q(name__icontains=location_query))
    context = {
        'arenas': arenas, 
        'location_query': location_query
    }
    return render(request, 'show_arena.html', context)

def arena_detail(request, arena_id):
    arena = get_object_or_404(Arena, pk=arena_id)
    today_date_str = timezone.now().strftime('%Y-%m-%d')
    context = {
        'arena': arena,
        'today_date_str': today_date_str,
    }
    return render(request, 'arena_detail.html', context)

@login_required
def user_booking_list(request):
    user_bookings = Booking.objects.filter(user=request.user).order_by('-date', 'start_hour')
    context = {
        'bookings': user_bookings,
        'today': timezone.now().date()
    }
    return render(request, 'user_bookings.html', context)


# ====================================================
# VIEWS FOR HTMX - RETURNING HTML PARTIALS
# ====================================================

def get_available_slots(request, arena_id):
    date_str = request.GET.get('date')
    if not date_str: return HttpResponseBadRequest("Date parameter is required.")
    try:
        selected_date = parse_date(date_str)
        if not selected_date: raise ValueError
    except ValueError:
        return HttpResponseBadRequest("Invalid date format (YYYY-MM-DD).")

    arena = get_object_or_404(Arena, pk=arena_id)
    day_of_week = selected_date.weekday()

    open_time_today = None
    close_time_today = None
    is_closed_today = True
    try:
        opening_rule = ArenaOpeningHours.objects.get(arena=arena, day=day_of_week)
        open_time_today = opening_rule.open_time
        close_time_today = opening_rule.close_time
        if open_time_today and close_time_today:
            is_closed_today = False
    except ArenaOpeningHours.DoesNotExist:
        is_closed_today = True # defaultnya tutup klo ga ada jadwal opt hours

    is_bookable = selected_date >= timezone.now().date()
    context_base = {
        'arena': arena,
        'selected_date': selected_date,
        'is_bookable_date': is_bookable,
        'is_closed_today': is_closed_today,
    }

    if is_closed_today:
        context_base['hourly_slots_data'] = []
        return render(request, 'partials/slot_list.html', context_base)

    bookings_today = Booking.objects.filter(arena=arena, date=selected_date, status='Booked').select_related('user')
    booked_hours = {b.start_hour: b for b in bookings_today}

    hourly_slots_data = []
    
    current_hour = open_time_today.hour
    while current_hour < close_time_today.hour:
        booking_info = booked_hours.get(current_hour)
        status = 'Booked' if booking_info else 'Available'
        #TODO next cari info harga
        price_info = "Rp 350.000"
        
        # cek apakah user yg login adalah yg booking (untuk bisa cancel booking)
        is_user_booking = False
        if booking_info and request.user.is_authenticated:
            is_user_booking = (booking_info.user == request.user)

        hourly_slots_data.append({
            'hour': current_hour,
            'status': status,
            'booking_info': booking_info,
            'price_info': price_info,
            'is_user_booking': is_user_booking,
        })
        current_hour += 1

    context = context_base
    context['hourly_slots_data'] = hourly_slots_data
    
    return render(request, 'partials/slot_list.html', context)



@login_required
def get_sport_modal_partial(request, arena_id, hour):
    arena = get_object_or_404(Arena, pk=arena_id)
    date_str = request.GET.get('date')
    if not date_str:
        return HttpResponseBadRequest("Date query parameter is required.")
    try:
        selected_date = parse_date(date_str)
        if not selected_date: raise ValueError
    except ValueError:
        return HttpResponseBadRequest("Invalid date format.")
    
    booking_model_meta = {'activity': {'field': {'choices': Booking.ACTIVITY_CHOICES}}}

    context = {
        'arena': arena,
        'hour': hour,
        'selected_date': selected_date,
        'booking_model_meta': booking_model_meta,
    }
    return render(request, 'partials/select_sport_modal.html', context)


@login_required
@transaction.atomic
def create_booking_hourly(request, arena_id):
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method.")

    arena = get_object_or_404(Arena, pk=arena_id)
    date_str = request.POST.get('date')
    hour_str = request.POST.get('hour')
    activity = request.POST.get('activity')

    if not date_str or not hour_str or not activity:
        return HttpResponse("Date, hour, and activity are required.", status=400)
    try:
        selected_date = parse_date(date_str)
        selected_hour = int(hour_str)
        if not selected_date: raise ValueError("Invalid Date")
    except ValueError as e:
        return HttpResponse(f"Invalid data: {e}", status=400)

    try:
        with transaction.atomic():
            if Booking.objects.filter(arena=arena, date=selected_date, start_hour=selected_hour, status='Booked').exists():
                return HttpResponse(f"Slot at {selected_hour}:00 is no longer available.", status=409)
            
            Booking.objects.create(
                user=request.user,
                arena=arena,
                date=selected_date,
                start_hour=selected_hour,
                status='Booked',
                activity=activity
            )
    except IntegrityError:
        return HttpResponse(f"Slot at {selected_hour}:is no longer available", status=409)
    except Exception as e:
        return HttpResponse(f"Failed to save booking: {e}", status=500)

    fake_request = HttpRequest()
    fake_request.method = 'GET'
    fake_request.GET = {'date': date_str}
    fake_request.user = request.user

    try:
        response = get_available_slots(fake_request, arena_id=arena_id)
    except Exception as e:
        return HttpResponse(f"Booking SUKSES, tapi gagal refresh list: {e}. Coba refresh manual.", status=500)
    
    response['HX-Trigger'] = '{"showToast": {"message": "Booking sukses!", "type": "success"}}'
    return response

@login_required
@transaction.atomic
def cancel_booking(request, booking_id):
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method.")

    booking = get_object_or_404(Booking, pk=booking_id)
    
    if booking.user != request.user:
        return HttpResponseForbidden("Unauthorized.")
    today = timezone.now().date()
    if booking.date < today:
        return HttpResponse("Cannot cancel past bookings.", status=400)
    
    arena_id = booking.arena.id
    date_str = booking.date.strftime('%Y-%m-%d')

    booking.status = 'Cancelled'
    booking.save()
    
    context = {
        'booking': booking,
        'today': today,
    }
    
    response = render(request, 'partials/booking_row.html', context)
    response['HX-Trigger'] = '{"showToast": {"message": "Booking dibatalkan.", "type": "success"}}'
    return response

# ======================================================
# ADMIN CRUD VIEWS
# ======================================================

def admin_arena_list(request):
    if not request.session.get('is_admin'):
        return redirect('authentication:login')
    arenas = Arena.objects.all()
    return render(request, 'booking_arena/admin_arena_list.html', {'arenas': arenas})

@user_passes_test(is_superuser)
def admin_arena_create(request):
    if request.method == 'POST':
        form = ArenaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('booking_arena:admin_arena_list')
    else:
        form = ArenaForm()
    return render(request, 'booking_arena/admin_arena_form.html', {'form': form, 'action': 'Create'})

@user_passes_test(is_superuser)
def admin_arena_update(request, id):
    arena = get_object_or_404(Arena, id=id)
    if request.method == 'POST':
        form = ArenaForm(request.POST, request.FILES, instance=arena)
        if form.is_valid():
            form.save()
            return redirect('booking_arena:admin_arena_list')
    else:
        form = ArenaForm(instance=arena)
    return render(request, 'booking_arena/admin_arena_form.html', {'form': form, 'action': 'Update'})

@user_passes_test(is_superuser)
def admin_arena_delete(request, id):
    arena = get_object_or_404(Arena, id=id)
    if request.method == 'POST':
        arena.delete()
        return redirect('booking_arena:admin_arena_list')
    return render(request, 'booking_arena/admin_arena_confirm_delete.html', {'arena': arena})

def admin_booking_list(request):
    if not request.session.get('is_admin'):
        return redirect('authentication:login')
    bookings = Booking.objects.all().select_related('user', 'arena')
    return render(request, 'booking_arena/admin_booking_list.html', {'bookings': bookings})

@user_passes_test(is_superuser)
def admin_booking_delete(request, id):
    booking = get_object_or_404(Booking, id=id)
    if request.method == 'POST':
        booking.delete()
        return redirect('booking_arena:admin_booking_list')
    return render(request, 'booking_arena/admin_booking_confirm_delete.html', {'booking': booking})

@user_passes_test(is_superuser)
def add_arena_ajax(request):
    if request.method == 'POST':
        form = ArenaForm(request.POST, request.FILES)
        if form.is_valid():
            new_arena = form.save()
            arena_data = {
                'id': str(new_arena.id),
                'name': new_arena.name,
                'location': new_arena.location,
                'capacity': new_arena.capacity,
                'description': new_arena.description,
                'img_url': new_arena.img_url if new_arena.img_url else None,
                'detail_url': f'/arena/{new_arena.id}/'
            }
            return JsonResponse({'status': 'success', 'message': 'Arena added successfully!', 'arena': arena_data})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    return JsonResponse({"status": "error", "message": "GET request not supported or Form invalid"}, status=405)


@user_passes_test(is_superuser)
def delete_arena_ajax(request, arena_id):
    if request.method == 'POST':
        try:
            arena = Arena.objects.get(pk=arena_id)
            arena_name = arena.name
            arena.delete()
            return JsonResponse({'status': 'success', 'message': f'Arena "{arena_name}" deleted successfully!'})
        except Arena.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Arena not found.'}, status=404)
        except Exception as e:
             return JsonResponse({'status': 'error', 'message': f'Error deleting arena: {e}'}, status=500)
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)

# View lama lu, bisa dihapus kalo gak dipake lagi
# def create_multiple_bookings(request, arena_id): ...
