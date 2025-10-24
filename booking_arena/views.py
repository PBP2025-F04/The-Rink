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
    return render(request, 'arena_detail.html', context)

@login_required
def user_booking_list(request):
    user_bookings = Booking.objects.filter(user=request.user).order_by('-date', 'time_slot__start_time')
    context = {
        'bookings': user_bookings
    }
    return render(request, 'user_bookings.html', context)

# CRUD KLO USER ADALAH SUPERUSER
from django.contrib.auth.decorators import user_passes_test
from .forms import ArenaForm

def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser)
def add_arena_ajax(request):
    """Handles creating a new Arena via AJAX POST."""
    if request.method == 'POST':
        form = ArenaForm(request.POST, request.FILES)
        if form.is_valid():
            new_arena = form.save()
            arena_data = {
                'id': new_arena.id, # Kirim UUID sebagai string
                'name': new_arena.name,
                'location': new_arena.location,
                'capacity': new_arena.capacity,
                'description': new_arena.description,
                'img_url': new_arena.img_url if new_arena.img_url else None,
                # URL buat detail view (hardcode, sesuaikan kalo perlu)
                'detail_url': f'/arena/{new_arena.id}/'
            }
            return JsonResponse({'status': 'success', 'message': 'Arena added successfully!', 'arena': arena_data})
        else:
            # Kirim error validasi form
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    form = ArenaForm()
    # Kita bisa render potongan HTML form di sini kalo mau
    # return render(request, 'partials/arena_form.html', {'form': form})
    # Atau return JSON kosong/error jika GET tidak diharapkan
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)


@user_passes_test(is_superuser) # Hanya superuser
def delete_arena_ajax(request, arena_id):
    """Handles deleting an Arena via AJAX POST."""
    if request.method == 'POST':
        try:
            arena = Arena.objects.get(pk=arena_id)
            arena_name = arena.name # Simpen nama buat pesan
            arena.delete()
            return JsonResponse({'status': 'success', 'message': f'Arena "{arena_name}" deleted successfully!'})
        except Arena.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Arena not found.'}, status=404)
        except Exception as e:
             return JsonResponse({'status': 'error', 'message': f'Error deleting arena: {e}'}, status=500)
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)




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