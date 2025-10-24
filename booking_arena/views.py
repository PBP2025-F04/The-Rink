from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
from django.utils import timezone
from booking_arena.models import Arena, TimeSlot, Booking
import datetime

def show_arena(request):
    arenas = Arena.objects.all()
    context = {
        'arenas': arenas,
    }
    return render(request, 'show_arena.html', context)

def arena_detail(request, arena_id):
    arena = get_object_or_404(Arena, pk=arena_id)
    context = {
        'arena': arena,
    }
    return render(request, 'booking_arena/arena_detail.html', context)

@login_required
def user_booking_list(request):
    user_bookings = Booking.objects.filter(user=request.user).order_by('-date', 'time_slot__start_time')
    context = {
        'bookings': user_bookings
    }
    return render(request, 'booking_arena/user_bookings.html', context)



# VIEWS HTMX AJAX, RETURN HTML PARTIALS
def get_available_slots(request, arena_id):
    date_str = request.GET.get('date')
    if not date_str:
        return HttpResponseBadRequest("Date parameter is required.")

    try:
        selected_date = parse_date(date_str)
        if not selected_date: raise ValueError
    except ValueError:
        return HttpResponseBadRequest("Invalid date format (YYYY-MM-DD).")

    arena = get_object_or_404(Arena, pk=arena_id)
    day_of_week = selected_date.weekday()

    base_slots = TimeSlot.objects.filter(
        arena=arena,
        day=day_of_week,
        is_avalaible=True
    ).order_by('start_time')

    booked_slot_ids = Booking.objects.filter(
        time_slot__arena=arena,
        date=selected_date,
        status='Booked'
    ).values_list('time_slot_id', flat=True)

    available_slots_data = []
    for slot in base_slots:
        booking_info = Booking.objects.filter(time_slot=slot, date=selected_date, status='Booked').select_related('user').first()
        available_slots_data.append({
            'slot': slot,
            'is_booked': slot.id in booked_slot_ids,
            'booking_info': booking_info
        })

    is_bookable_date = selected_date >= timezone.now().date() # Flag untuk template

    context = {
        'arena': arena,
        'selected_date': selected_date,
        'slots_data': available_slots_data,
        'is_bookable_date': is_bookable_date,
    }
    return render(request, 'partials/slot_list.html', context)



# VIEWS HTMX AJAX, RETURN JSON
@login_required
def create_booking(request, slot_id):
    if request.method == 'POST':
        date_str = request.POST.get('date')
        if not date_str:
            return JsonResponse({"status": "error", "message": "Date is required."}, status=400)

        try:
            selected_date = parse_date(date_str)
            if not selected_date: raise ValueError
        except ValueError:
            return JsonResponse({"status": "error", "message": "Invalid date format."}, status=400)

        slot = get_object_or_404(TimeSlot, pk=slot_id)

        if Booking.objects.filter(time_slot=slot, date=selected_date, status='Booked').exists():
            return JsonResponse({"status": "error", "message": "This slot is already booked on the selected date."}, status=400)

        try:
            Booking.objects.create(
                user=request.user,
                time_slot=slot,
                date=selected_date,
                status='Booked'
            )
            return JsonResponse({"status": "success", "message": "Booking successful!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Failed to create booking: {e}"}, status=500)
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)

@login_required
def cancel_booking(request, booking_id):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, pk=booking_id)
        if booking.user != request.user:
            return JsonResponse({"status": "error", "message": "Cannot cancel others booking."}, status=403)
        booking.status = 'Cancelled'
        booking.save()
        return JsonResponse({"status": "success", "message": "Booking successfully cancelled."})
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)

# Admin views for booking arena
def admin_arena_list(request):
    if not request.session.get('is_admin'):
        return redirect('authentication:login')
    arenas = Arena.objects.all()
    return render(request, 'booking_arena/admin_arena_list.html', {'arenas': arenas})

def admin_arena_create(request):
    if not request.session.get('is_admin'):
        return redirect('authentication:login')
    from .forms import ArenaForm
    if request.method == 'POST':
        form = ArenaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Arena created successfully!')
            return redirect('booking_arena:admin_arena_list')
    else:
        form = ArenaForm()
    return render(request, 'booking_arena/admin_arena_form.html', {'form': form, 'action': 'Create'})

def admin_arena_update(request, arena_id):
    if not request.session.get('is_admin'):
        return redirect('authentication:login')
    from .forms import ArenaForm
    arena = get_object_or_404(Arena, id=arena_id)
    if request.method == 'POST':
        form = ArenaForm(request.POST, request.FILES, instance=arena)
        if form.is_valid():
            form.save()
            messages.success(request, 'Arena updated successfully!')
            return redirect('booking_arena:admin_arena_list')
    else:
        form = ArenaForm(instance=arena)
    return render(request, 'booking_arena/admin_arena_form.html', {'form': form, 'action': 'Update'})

def admin_arena_delete(request, arena_id):
    if not request.session.get('is_admin'):
        return redirect('authentication:login')
    arena = get_object_or_404(Arena, id=arena_id)
    if request.method == 'POST':
        arena.delete()
        messages.success(request, 'Arena deleted successfully!')
        return redirect('booking_arena:admin_arena_list')
    return render(request, 'booking_arena/admin_arena_confirm_delete.html', {'arena': arena})

def admin_booking_list(request):
    if not request.session.get('is_admin'):
        return redirect('authentication:login')
    bookings = Booking.objects.all().order_by('-booked_at')
    return render(request, 'booking_arena/admin_booking_list.html', {'bookings': bookings})

def admin_booking_delete(request, booking_id):
    if not request.session.get('is_admin'):
        return redirect('authentication:login')
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'Booking deleted successfully!')
        return redirect('booking_arena:admin_booking_list')
    return render(request, 'booking_arena/admin_booking_confirm_delete.html', {'booking': booking})
