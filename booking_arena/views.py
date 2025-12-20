# File: booking_arena/views.py
import json  # <--- INI PENTING
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponse, HttpRequest, Http404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.dateparse import parse_date
from django.utils import timezone
from django.db.models import Q
from django.db import transaction
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import Arena, Booking, ArenaOpeningHours
from .forms import ArenaForm, ArenaOpeningHoursFormSet
import traceback

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
# VIEWS WEB / HTMX
# ============================================

@login_required
def show_arena(request):
    location_query = request.GET.get('location', '').strip()
    arenas = Arena.objects.all()
    if location_query:
        arenas = arenas.filter(Q(location__icontains=location_query) | Q(name__icontains=location_query))

    arena_form = ArenaForm()
    initial_days = [{'day': i} for i in range(7)]
    hours_formset = ArenaOpeningHoursFormSet(instance=Arena(), initial=initial_days, prefix='hours')
    
    context = {'arenas': arenas, 'location_query': location_query, 'form': arena_form, 'formset': hours_formset}
    return render(request, 'show_arena.html', context)

def arena_detail(request, arena_id):
    arena = get_object_or_404(Arena, pk=arena_id)
    today_date_str = timezone.now().strftime('%Y-%m-%d')
    context = {'arena': arena, 'today_date_str': today_date_str}
    return render(request, 'arena_detail.html', context)

@login_required
def user_booking_list(request):
    now = timezone.now()
    current_date = now.date()
    current_hour = now.hour

    user_bookings = Booking.objects.filter(
        user=request.user, 
        status='Booked'
    ).filter(
        Q(date__gt=current_date) | 
        Q(date=current_date, start_hour__gt=current_hour)
    ).order_by('date', 'start_hour')

    return render(request, 'user_bookings.html', {
        'bookings': user_bookings, 
        'today': current_date
    })

def get_available_slots(request, arena_id):
    date_str = request.GET.get('date')
    if not date_str: return HttpResponseBadRequest("Date parameter is required.")
    try:
        context = _get_arena_slots_context(request, arena_id, date_str)
    except HttpResponse as e: return e
    return render(request, 'partials/slot_list.html', context)

@login_required
def get_sport_modal_partial(request, arena_id, hour):
    arena = get_object_or_404(Arena, pk=arena_id)
    date_str = request.GET.get('date')
    if not date_str: return HttpResponseBadRequest("Date query parameter is required.")
    selected_date = parse_date(date_str)
    
    booking_model_meta = {'activity': {'field': {'choices': Booking.ACTIVITY_CHOICES}}}
    context = {'arena': arena, 'hour': hour, 'selected_date': selected_date, 'booking_model_meta': booking_model_meta}
    return render(request, 'partials/select_sport_modal.html', context)

@login_required
def create_booking_hourly(request, arena_id):
    if request.method != 'POST': return HttpResponseBadRequest("Invalid request method.")
    date_str = request.POST.get('date')
    hour_str = request.POST.get('hour')
    activity = request.POST.get('activity')
    
    if not date_str or not hour_str or not activity: return HttpResponse("Data incomplete", status=400)
    
    selected_date = parse_date(date_str)
    selected_hour = int(hour_str)
    
    try:
        with transaction.atomic():
            arena = get_object_or_404(Arena, pk=arena_id)
            existing_booking = Booking.objects.filter(arena=arena, date=selected_date, start_hour=selected_hour).select_for_update().first()

            if existing_booking:
                if existing_booking.status == 'Booked':
                    return HttpResponse(f"Slot at {selected_hour}:00 is taken.", status=409)
                else:
                    existing_booking.status = 'Booked'
                    existing_booking.user = request.user
                    existing_booking.activity = activity
                    existing_booking.booked_at = timezone.now()
                    existing_booking.save()
            else:
                Booking.objects.create(user=request.user, arena=arena, date=selected_date, start_hour=selected_hour, status='Booked', activity=activity)
    except Exception as e: return HttpResponse(f"Failed: {e}", status=500)

    # === BAGIAN INI YANG GW UPDATE ===
    context = _get_arena_slots_context(request, arena_id, date_str)
    response = render(request, 'partials/slot_list.html', context)
    
    # Kirim sinyal JSON biar Modal nutup
    trigger_data = {
        "showToast": {
            "message": "Booking sukses!", 
            "type": "success"
        },
        "closeModal": True 
    }
    response['HX-Trigger'] = json.dumps(trigger_data)
    
    return response

@login_required
def cancel_booking(request, booking_id):
    if request.method != 'POST': return HttpResponseBadRequest("Invalid request method.")
    source_page = request.GET.get('from', 'arena') 
    
    try:
        with transaction.atomic():
            booking = get_object_or_404(Booking.objects.select_for_update(), pk=booking_id, user=request.user)
            if booking.status == 'Booked':
                booking.status = 'Cancelled'
                booking.save()
    except Exception as e: return HttpResponse(f"Failed: {e}", status=500)
    
    headers = {'HX-Trigger': '{"showToast": {"message": "Booking dibatalkan.", "type": "success"}}'}
    if source_page == 'my_bookings':
        return HttpResponse("", headers=headers)
    else:
        context = _get_arena_slots_context(request, booking.arena.id, booking.date.strftime('%Y-%m-%d'))
        response = render(request, 'partials/slot_list.html', context)
        response['HX-Trigger'] = headers['HX-Trigger']
        return response

@user_passes_test(is_superuser)
def add_arena_ajax(request):
    if request.method == 'POST':
        form = ArenaForm(request.POST, request.FILES)
        formset = ArenaOpeningHoursFormSet(request.POST, instance=Arena(), prefix='hours')
        if form.is_valid() and formset.is_valid():
            new_arena = form.save()
            formset.instance = new_arena
            formset.save()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error'}, status=400)
    return JsonResponse({"status": "error"}, status=405)

@user_passes_test(is_superuser)
def delete_arena_ajax(request, arena_id):
    if request.method == 'POST':
        try:
            Arena.objects.get(pk=arena_id).delete()
            return JsonResponse({'status': 'success'})
        except: return JsonResponse({'status': 'error'}, status=500)
    return JsonResponse({"status": "error"}, status=405)

# =================================================================
# FLUTTER API SECTION 
# =================================================================

@csrf_exempt
def get_arenas_flutter(request):
    arenas = Arena.objects.all()
    data = []
    for arena in arenas:
        data.append({
            "id": str(arena.id),
            "name": arena.name,
            "location": arena.location,
            "img_url": arena.img_url,
            "capacity": arena.capacity,
            "description": arena.description,
        })
    return JsonResponse(data, safe=False)

@csrf_exempt
def get_bookings_flutter(request):
    arena_id = request.GET.get('arena')
    date_str = request.GET.get('date')
    
    if not arena_id or not date_str:
        return JsonResponse({"error": "Param 'arena' & 'date' wajib ada"}, status=400)
        
    bookings = Booking.objects.filter(arena_id=arena_id, date=date_str, status='Booked')
    data = []
    for b in bookings:
        data.append({
            "start_hour": b.start_hour,
            "status": b.status,
            "is_mine": (request.user.is_authenticated and b.user == request.user)
        })
    return JsonResponse(data, safe=False)

@csrf_exempt
def create_booking_flutter(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": False, "message": "Anda belum login. Silakan login ulang."}, status=401)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            arena_id = data.get('arena_id') or data.get('arena') 
            date_str = data.get('date')
            start_hour_raw = data.get('start_hour')
            activity = data.get('activity', 'Badminton')

            if not arena_id: return JsonResponse({"status": False, "message": "Arena ID tidak ditemukan!"}, status=400)
            if not date_str: return JsonResponse({"status": False, "message": "Tanggal kosong!"}, status=400)
            if start_hour_raw is None: return JsonResponse({"status": False, "message": "Jam kosong!"}, status=400)

            start_hour = int(start_hour_raw)
            booking_date = parse_date(date_str)
            if not booking_date: return JsonResponse({"status": False, "message": "Format tanggal salah!"}, status=400)

            arena = get_object_or_404(Arena, pk=arena_id)
            existing = Booking.objects.filter(arena=arena, date=booking_date, start_hour=start_hour, status='Booked').exists()

            if existing: return JsonResponse({"status": False, "message": "Slot penuh!"}, status=409)

            booking = Booking.objects.create(
                user=request.user, arena=arena, date=booking_date, start_hour=start_hour, activity=activity, status='Booked'
            )
            return JsonResponse({"status": True, "message": "Booking Berhasil!", "booking_id": str(booking.id)})

        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"status": False, "message": f"Server Error: {str(e)}"}, status=500)
            
    return JsonResponse({"status": False, "message": "Method not allowed"}, status=405)

@csrf_exempt
@login_required
def cancel_booking_flutter(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            booking_id = data.get('booking_id')
            booking = get_object_or_404(Booking, pk=booking_id)
            if booking.user != request.user: return JsonResponse({"status": False, "message": "Bukan punya lu!"}, status=403)
            booking.status = 'Cancelled'
            booking.save()
            return JsonResponse({"status": True, "message": "Booking dibatalkan"})
        except Exception as e:
            return JsonResponse({"status": False, "message": str(e)}, status=500)
    return JsonResponse({"status": False, "message": "Method not allowed"}, status=405)

@csrf_exempt
@login_required
def my_history_flutter(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-date')
    data = []
    for b in bookings:
        data.append({
            "id": str(b.id),
            "arena_name": b.arena.name,
            "date": str(b.date),
            "start_hour": b.start_hour,
            "status": b.status,
            "activity": b.activity
        })
    return JsonResponse(data, safe=False)