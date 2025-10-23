# File: booking_arena/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
from django.utils import timezone
# Import model sesuai nama di models.py lu
from .models import Arena, TimeSlot, Booking
import datetime

# ============================================
# VIEWS THAT RENDER FULL HTML TEMPLATES
# ============================================

def list_arenas(request):
    """
    Tujuan: Menampilkan halaman utama modul: daftar semua arena.
    Butuh Template Utuh: Ya (`arena_list.html`).
    """
    arenas = Arena.objects.all()
    context = {
        'arenas': arenas,
    }
    # Asumsi template ada di booking_arena/templates/arena_list.html
    return render(request, 'booking_arena/arena_list.html', context)

def arena_detail(request, arena_id):
    """
    Tujuan: Menampilkan halaman detail satu arena, termasuk kalender
             dasar untuk memilih tanggal.
    Butuh Template Utuh: Ya (`arena_detail.html`). Daftar slot akan
    di-load secara dinamis pakai HTMX.
    """
    arena = get_object_or_404(Arena, pk=arena_id)
    context = {
        'arena': arena,
    }
    # Asumsi template ada di booking_arena/templates/arena_detail.html
    return render(request, 'booking_arena/arena_detail.html', context)

@login_required
def user_booking_list(request):
    """
    Tujuan: Menampilkan halaman riwayat booking milik user.
    Butuh Template Utuh: Ya (`user_bookings.html`).
    """
    # Menggunakan nama field dari model lu: 'date', 'time_slot__start_time'
    user_bookings = Booking.objects.filter(user=request.user).order_by('-date', 'time_slot__start_time')
    context = {
        'bookings': user_bookings
    }
    # Asumsi template ada di booking_arena/templates/user_bookings.html
    return render(request, 'booking_arena/user_bookings.html', context)

# ====================================================
# VIEWS FOR HTMX/AJAX - RETURNING HTML PARTIALS
# ====================================================

def get_available_slots(request, arena_id):
    """
    Tujuan: Dipanggil oleh HTMX saat user memilih tanggal. Mengambil
             daftar slot yang available pada tanggal itu.
    Butuh Template Utuh?: Tidak. Hanya butuh potongan HTML (`partials/slot_list.html`).
    """
    date_str = request.GET.get('date') # Menggunakan 'date' agar konsisten
    if not date_str:
        return HttpResponseBadRequest("Date parameter is required.")

    try:
        selected_date = parse_date(date_str) # Field di Booking: 'date'
        if not selected_date: raise ValueError
        # Validasi tanggal lampau dihapus, ditangani di frontend/template
    except ValueError:
        return HttpResponseBadRequest("Invalid date format (YYYY-MM-DD).")

    arena = get_object_or_404(Arena, pk=arena_id)
    day_of_week = selected_date.weekday() # Field di TimeSlot: 'day' (0=Monday)

    # Menggunakan nama field dari model lu: 'day', 'is_avalaible', 'start_time'
    base_slots = TimeSlot.objects.filter(
        arena=arena,
        day=day_of_week,
        is_avalaible=True
    ).order_by('start_time')

    # Menggunakan nama field dari model lu: 'time_slot', 'date'
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
            'booking_info': booking_info # Kirim object booking jika ada
        })

    is_bookable_date = selected_date >= timezone.now().date() # Flag untuk template

    context = {
        'arena': arena,
        'selected_date': selected_date,
        'slots_data': available_slots_data,
        'is_bookable_date': is_bookable_date,
    }
    # Mengembalikan HANYA potongan HTML
    # Path disesuaikan: partials langsung di dalam templates/
    return render(request, 'partials/slot_list.html', context)

# ======================================================
# VIEWS FOR HTMX/AJAX - RETURNING JSON
# ======================================================

@login_required
def create_booking(request, slot_id):
    """
    Tujuan: Dipanggil oleh HTMX saat user submit form booking (dari modal).
             Memproses dan menyimpan booking baru. Mengembalikan JSON.
    """
    if request.method == 'POST':
        date_str = request.POST.get('date') # Ambil tanggal dari data POST
        if not date_str:
            return JsonResponse({"status": "error", "message": "Date is required."}, status=400)

        try:
            selected_date = parse_date(date_str) # Field di Booking: 'date'
            if not selected_date: raise ValueError
            if selected_date < timezone.now().date():
                 return JsonResponse({"status": "error", "message": "Cannot book past dates."}, status=400)
        except ValueError:
            return JsonResponse({"status": "error", "message": "Invalid date format."}, status=400)

        slot = get_object_or_404(TimeSlot, pk=slot_id) # Nama model: TimeSlot

        # Menggunakan nama field dari model lu: 'time_slot', 'date'
        if Booking.objects.filter(time_slot=slot, date=selected_date, status='Booked').exists():
            return JsonResponse({"status": "error", "message": "This slot is already booked on the selected date."}, status=400)

        try:
            # Menggunakan nama field dari model lu: 'time_slot', 'date'
            Booking.objects.create(
                user=request.user,
                time_slot=slot,
                date=selected_date,
                status='Booked'
            )
            # Response sukses
            return JsonResponse({"status": "success", "message": "Booking successful!"})
        except Exception as e:
            # Tangani error database jika ada
            return JsonResponse({"status": "error", "message": f"Failed to create booking: {e}"}, status=500)

    # Hanya izinkan metode POST
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)

@login_required
def cancel_booking(request, booking_id):
    """
    Tujuan: Dipanggil oleh HTMX saat user klik tombol cancel booking.
             Memproses pembatalan. Mengembalikan JSON.
    """
    if request.method == 'POST':
        booking = get_object_or_404(Booking, pk=booking_id)

        # Pastikan user hanya bisa batalin bookingannya sendiri
        if booking.user != request.user:
            return JsonResponse({"status": "error", "message": "Unauthorized."}, status=403) # 403 Forbidden

        # Logika pembatalan
        booking.status = 'Cancelled'
        booking.save()

        # Response sukses
        return JsonResponse({"status": "success", "message": "Booking successfully cancelled."})

    # Hanya izinkan metode POST
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)