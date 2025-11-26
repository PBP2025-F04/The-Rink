# File: booking_arena/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponse, HttpRequest, Http404
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponse, HttpRequest, Http404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.dateparse import parse_date
from django.utils import timezone
from django.db.models import Q
from django.db import transaction, IntegrityError
from django.urls import reverse

from .models import Arena, Booking, ArenaOpeningHours
from .forms import ArenaForm, ArenaOpeningHoursFormSet

# ============================================
# HELPER FUNCTIONS
# ============================================

def is_superuser(user):
    return user.is_superuser

def _get_arena_slots_context(request, arena_id, date_str):
    try:
        selected_date = parse_date(date_str)
        if not selected_date: raise ValueError
    except ValueError:
        raise HttpResponseBadRequest("Invalid date format (YYYY-MM-DD).")

    arena = get_object_or_404(Arena, pk=arena_id)
    day_of_week = selected_date.weekday()

    open_time_today, close_time_today, is_closed_today = None, None, True
    try:
        opening_rule = ArenaOpeningHours.objects.get(arena=arena, day=day_of_week)
        open_time_today = opening_rule.open_time
        close_time_today = opening_rule.close_time
        if open_time_today and close_time_today:
            is_closed_today = False
    except ArenaOpeningHours.DoesNotExist:
        is_closed_today = True

    is_bookable = selected_date >= timezone.now().date()
    
    context = {
        'arena': arena,
        'selected_date': selected_date,
        'is_bookable_date': is_bookable,
        'is_closed_today': is_closed_today,
        'hourly_slots_data': []
    }

    if is_closed_today:
        return context

    bookings_today = Booking.objects.filter(
        arena=arena,
        date=selected_date,
        status='Booked'
    ).select_related('user')
    booked_hours = {b.start_hour: b for b in bookings_today}

    hourly_slots_data = []
    current_hour = open_time_today.hour
    while current_hour < close_time_today.hour:
        booking_info = booked_hours.get(current_hour)
        status = 'Booked' if booking_info else 'Available'
        price_info = "Rp 350.000"
        
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

    context['hourly_slots_data'] = hourly_slots_data
    return context

# ============================================
# VIEWS RENDERING FULL PAGES
# ============================================

@login_required
def show_arena(request):
    location_query = request.GET.get('location', '').strip()
    arenas = Arena.objects.all()
    if location_query:
        arenas = arenas.filter(Q(location__icontains=location_query) | Q(name__icontains=location_query))

    arena_form = ArenaForm()
    initial_days = [{'day': i} for i in range(7)]
    hours_formset = ArenaOpeningHoursFormSet(
        instance=Arena(), 
        initial=initial_days,
        prefix='hours' 
    )
    
    context = {
        'arenas': arenas, 
        'location_query': location_query,
        'form': arena_form,        
        'formset': hours_formset,
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
    if not date_str: 
        return HttpResponseBadRequest("Date parameter is required.")
    
    try:
        context = _get_arena_slots_context(request, arena_id, date_str)
    except HttpResponse as e:
        return e
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
def create_booking_hourly(request, arena_id):
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method.")

    date_str = request.POST.get('date')
    hour_str = request.POST.get('hour')
    activity = request.POST.get('activity')
    
    if not date_str or not hour_str or not activity:
        return HttpResponse("Date, hour, and activity are required.", status=400)

    try:
        selected_date = parse_date(date_str)
        selected_hour = int(hour_str)
        if not selected_date: raise ValueError("Invalid Date")
        if selected_date < timezone.now().date():
            return HttpResponse("Cannot book past dates.", status=400)
    except ValueError as e:
        return HttpResponse(f"Invalid data: {e}", status=400)

    try:
        with transaction.atomic():
            arena = get_object_or_404(Arena, pk=arena_id)
            
            # === LOGIC BARU: CARI DULU, JANGAN LANGSUNG CREATE ===
            existing_booking = Booking.objects.filter(
                arena=arena, 
                date=selected_date, 
                start_hour=selected_hour
            ).select_for_update().first() # Lock row-nya

            if existing_booking:
                # Kalo ada...
                if existing_booking.status == 'Booked':
                    # Udah di-book orang lain (atau kita sendiri)
                    print(f"[DEBUG] GAGAL: Slot jam {selected_hour} udah 'Booked'")
                    return HttpResponse(f"Slot at {selected_hour}:00 is no longer available.", status=409)
                else:
                    # Kalo statusnya 'Cancelled' atau 'Completed', kita "daur ulang" row-nya
                    print(f"[DEBUG] SUKSES: Daur ulang row 'Cancelled' untuk jam {selected_hour}")
                    existing_booking.status = 'Booked'
                    existing_booking.user = request.user
                    existing_booking.activity = activity
                    existing_booking.booked_at = timezone.now() # Update timestamp
                    existing_booking.save()
            else:
                # Kalo beneran gak ada, baru CREATE
                print(f"[DEBUG] SUKSES: Bikin row baru untuk jam {selected_hour}")
                Booking.objects.create(
                    user=request.user,
                    arena=arena,
                    date=selected_date,
                    start_hour=selected_hour,
                    status='Booked',
                    activity=activity
                )
            # === AKHIR LOGIC BARU ===

    except Exception as e:
        print(f"[DEBUG] GAGAL: Error di transaksi create: {e}")
        return HttpResponse(f"Failed to save booking: {e}", status=500)

    # === SUKSES ===
    context = _get_arena_slots_context(request, arena_id, date_str)
    response = render(request, 'partials/slot_list.html', context)
    response['HX-Trigger'] = '{"showToast": {"message": "Booking sukses!", "type": "success"}}'
    return response

@login_required
def cancel_booking(request, booking_id):
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method.")
        
    source_page = request.GET.get('from', 'arena') 
    booking_to_cancel = None
    today = timezone.now().date() 

    try:
        with transaction.atomic():
            booking_to_cancel = get_object_or_404(
                Booking.objects.select_for_update(),
                pk=booking_id, 
                user=request.user
            )
            
            if booking_to_cancel.date < today:
                return HttpResponse("Cannot cancel past bookings.", status=400)
            
            if booking_to_cancel.status == 'Booked':
                booking_to_cancel.status = 'Cancelled'
                booking_to_cancel.save()
            # Kalo udah 'Cancelled', kita biarin aja (anggep sukses)

    except (Booking.DoesNotExist, Http404):
         return HttpResponseForbidden("Unauthorized (Booking not found or not owned).")
    except Exception as e:
         return HttpResponse(f"Failed to cancel booking: {e}", status=500)
    
    # === SUKSES ===
    headers = {'HX-Trigger': '{"showToast": {"message": "Booking dibatalkan.", "type": "success"}}'}
    
    if source_page == 'my_bookings':
        # Kirim balik 1 baris <tr>
        context = { 'booking': booking_to_cancel, 'today': today }
        # PENTING: Render pake 'request' ASLI
        return render(request, 'partials/_booking_row.html', context, headers=headers)
        
    else: # Default-nya 'arena'
        # Kirim balik SEMUA slot list
        arena_id = booking_to_cancel.arena.id
        date_str = booking_to_cancel.date.strftime('%Y-%m-%d')
        
        # Panggil helper buat dapet context BARU
        context = _get_arena_slots_context(request, arena_id, date_str)
        
        # PENTING: Render pake 'request' ASLI
        response = render(request, 'partials/slot_list.html', context)
        response['HX-Trigger'] = headers['HX-Trigger']
        return response

@user_passes_test(is_superuser)
@transaction.atomic
def add_arena_ajax(request):
    if request.method == 'POST':
        form = ArenaForm(request.POST, request.FILES)
        formset = ArenaOpeningHoursFormSet(request.POST, instance=Arena(), prefix='hours')

        if form.is_valid() and formset.is_valid():
            new_arena = form.save()
            formset.instance = new_arena
            formset.save()
            arena_data = {
                'id': str(new_arena.id),
                'name': new_arena.name,
                'location': new_arena.location,
                'img_url': new_arena.img_url if new_arena.img_url else None,
                'detail_url': reverse('booking_arena:arena_detail', args=[new_arena.id]),
                'delete_url': reverse('booking_arena:delete_arena_ajax', args=[new_arena.id])
            }
            return JsonResponse({'status': 'success', 'message': 'Arena berhasil ditambah!', 'arena': arena_data})
        
        else:
            errors = form.errors.as_json()
            errors_formset = [f.errors.as_json() for f in formset if f.errors]
            print("Form errors:", errors)
            print("Formset errors:", errors_formset)
            return JsonResponse({'status': 'error', 'message': 'Validasi gagal. Cek input Anda.', 'errors': errors, 'formset_errors': errors_formset}, status=400)
    
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)

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

# ======================================================
# ADMIN CRUD VIEWS
# ======================================================
@user_passes_test(is_superuser)
@transaction.atomic
def add_arena_ajax(request):
    if request.method == 'POST':
        form = ArenaForm(request.POST, request.FILES)
        formset = ArenaOpeningHoursFormSet(request.POST, instance=Arena(), prefix='hours')

        if form.is_valid() and formset.is_valid():
            new_arena = form.save()
            formset.instance = new_arena
            formset.save()
            arena_data = {
                'id': str(new_arena.id),
                'name': new_arena.name,
                'location': new_arena.location,
                'img_url': new_arena.img_url if new_arena.img_url else None,
                'detail_url': reverse('booking_arena:arena_detail', args=[new_arena.id]),
                'delete_url': reverse('booking_arena:delete_arena_ajax', args=[new_arena.id])
            }
            return JsonResponse({'status': 'success', 'message': 'Arena berhasil ditambah!', 'arena': arena_data})
        
        else:
            errors = form.errors.as_json()
            errors_formset = [f.errors.as_json() for f in formset if f.errors]
            print("Form errors:", errors)
            print("Formset errors:", errors_formset)
            return JsonResponse({'status': 'error', 'message': 'Validasi gagal. Cek input Anda.', 'errors': errors, 'formset_errors': errors_formset}, status=400)
    
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)

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
