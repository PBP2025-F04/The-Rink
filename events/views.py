from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Package, PackageBooking, Event, EventRegistration
# Anda juga perlu membuat file forms.py untuk PackageBookingForm
# from .forms import PackageBookingForm 

# === Views untuk PAKET ===

def package_list_view(request):
    """
    Menampilkan semua paket yang aktif.
    (CRUD: Read)
    """
    packages = Package.objects.filter(is_active=True)
    context = {
        'packages': packages
    }
    return render(request, 'events/package_list.html', context)

@login_required
def book_package_modal_view(request, package_id):
    """
    View ini dipanggil HTMX untuk mengisi modal.
    (CRUD: Create - Step 1: Show Form)
    """
    package = get_object_or_404(Package, id=package_id)
    
    # Asumsi Anda punya form di events/forms.py
    # form = PackageBookingForm() 
    
    context = {
        'package': package,
        # 'form': form
    }
    # Merender HANYA bagian form-nya saja (partial HTML)
    return render(request, 'events/partials/book_package_form.html', context)

@login_required
def book_package_submit_view(request, package_id):
    """
    View ini dipanggil HTMX saat form di dalam modal di-submit.
    (CRUD: Create - Step 2: Process Data)
    """
    if request.method != "POST":
        return HttpResponseForbidden() # Hanya izinkan POST

    package = get_object_or_404(Package, id=package_id)
    
    # Ambil data dari form (misal: tanggal)
    # form = PackageBookingForm(request.POST)
    # if form.is_valid():
    #     booking = form.save(commit=False)
    #     booking.user = request.user
    #     booking.package = package
    #     booking.save()
    
    #     # Respon HTMX: Kirim pesan sukses
    #     return HttpResponse("<p>Booking berhasil! Cek halaman profil Anda.</p>")
    # else:
    #     # Kirim balik form dengan error (masih di dalam modal)
    #     context = {'package': package, 'form': form}
    #     return render(request, 'events/partials/book_package_form.html', context)
    
    # --- Versi simplified jika tanpa form ---
    # (Ini hanya contoh, sebaiknya pakai form)
    scheduled_date_str = request.POST.get('scheduled_date') # '2025-12-01T10:00'
    if scheduled_date_str:
        PackageBooking.objects.create(
            user=request.user,
            package=package,
            scheduled_datetime=scheduled_date_str
        )
        # Respon HTMX: Kirim pesan sukses, modal akan ditutup oleh HTMX
        return HttpResponse("<p>Booking berhasil! Cek halaman profil Anda.</p>")
    else:
        # Respon HTMX: Kirim pesan error
        return HttpResponse("<p class='text-danger'>Tanggal harus diisi!</p>")


# === Views untuk EVENT ===

def event_list_view(request):
    """
    Menampilkan daftar semua event yang akan datang.
    View ini menangani request biasa DAN request HTMX untuk filtering.
    (CRUD: Read)
    """
    # Ambil filter dari query params (e.g., /events/?type=hockey)
    event_type_filter = request.GET.get('type')
    
    # Query dasar: semua event yang akan datang & sudah publish
    events = Event.objects.filter(
        is_published=True, 
        start_datetime__gte=timezone.now()
    ).order_by('start_datetime')
    
    # Terapkan filter jika ada
    if event_type_filter:
        # Asumsi ada field 'type' di model Event (e.g., 'hockey', 'curling')
        events = events.filter(type=event_type_filter) 
        
    context = {
        'events': events
    }
    
    # === Logika Kunci HTMX ===
    # Jika request ini berasal dari HTMX (ada header HX-Request),
    # kita kirim balik HANYA bagian/partial dari HTML, bukan seluruh halaman.
    if request.htmx:
        # 'hx-target' di HTML harus menunjuk ke kontainer list event ini
        return render(request, 'events/partials/event_list_items.html', context)
        
    # Jika ini request biasa (load halaman penuh), kirim template lengkapnya
    return render(request, 'events/event_list.html', context)

def event_detail_view(request, event_id):
    """
    Menampilkan detail satu event spesifik.
    (CRUD: Read)
    """
    event = get_object_or_404(Event, id=event_id, is_published=True)
    
    # Cek apakah user yang login sudah terdaftar
    is_registered = False
    if request.user.is_authenticated:
        is_registered = EventRegistration.objects.filter(
            user=request.user, 
            event=event
        ).exists()
        
    context = {
        'event': event,
        'is_registered': is_registered
    }
    return render(request, 'events/event_detail.html', context)

@login_required
def register_event_view(request, event_id):
    """
    View ini HANYA untuk HTMX (dipanggil via hx-post).
    Mendaftarkan user ke event.
    (CRUD: Create)
    """
    if request.method != "POST":
        return HttpResponseForbidden() # Error 403 jika bukan POST

    event = get_object_or_404(Event, id=event_id)
    user = request.user
    
    # 1. Cek kuota (jika ada)
    current_participants = event.registrations.count()
    if event.max_participants and current_participants >= event.max_participants:
        # Kirim respon HTML partial yang berisi pesan error
        return HttpResponse("<span class='text-danger'>Event Penuh!</span>")

    # 2. Cek apakah sudah terdaftar
    already_registered, created = EventRegistration.objects.get_or_create(
        user=user, 
        event=event
    )
    
    # Jika 'created' == True, berarti pendaftaran berhasil
    if not created and not already_registered: # Seharusnya tidak terjadi, tapi sbg pengaman
         return HttpResponse("<span class='text-warning'>Gagal mendaftar.</span>")

    # 4. Kirim balik HTML partial untuk tombol "Booked" yang baru
    # Ini akan menggantikan tombol "RSVP" di browser user (`hx-target="this"`)
    context = {'event': event}
    return render(request, 'events/partials/button_registered.html', context)

@login_required
def unregister_event_view(request, event_id):
    """
    View HTMX untuk membatalkan pendaftaran.
    (CRUD: Delete)
    """
    if request.method != "POST":
        return HttpResponseForbidden()

    event = get_object_or_404(Event, id=event_id)
    user = request.user

    # Cari pendaftarannya dan hapus
    registration = EventRegistration.objects.filter(user=user, event=event)
    if registration.exists():
        registration.delete() # (CRUD: Delete)

    # Kirim balik HTML partial untuk tombol "RSVP" yang original
    context = {'event': event}
    return render(request, 'events/partials/button_rsvp.html', context)

# events/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages # Untuk notifikasi
from .models import Package, PackageBooking, Event, EventRegistration, EventCategory
from .forms import PackageBookingForm

# === VIEWS PAKET ===

def package_list_view(request):
    """Menampilkan semua paket yang aktif."""
    packages = Package.objects.filter(is_active=True)
    context = {'packages': packages}
    return render(request, 'events/package_list.html', context)

@login_required
def book_package_view(request, package_id):
    """
    Menangani GET (tampilkan form modal) dan POST (submit form).
    Dipanggil oleh HTMX.
    """
    package = get_object_or_404(Package, id=package_id)
    
    if request.method == 'POST':
        form = PackageBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.package = package
            booking.save()
            
            messages.success(request, f'Paket "{package.name}" berhasil dibooking!')
            
            # Kirim header HTMX untuk me-redirect halaman penuh
            response = HttpResponse(status=204) # 204 No Content
            response['HX-Redirect'] = request.META.get('HTTP_REFERER', '/')
            return response
        # Jika form tidak valid, kirim balik form dengan error (masih di modal)
    else:
        form = PackageBookingForm()
        
    context = {
        'package': package,
        'form': form
    }
    # Merender HANYA partial form untuk modal
    return render(request, 'events/partials/_book_package_form.html', context)


# === VIEWS EVENT ===

def event_list_view(request):
    """
    Menampilkan daftar event + menangani filter HTMX.
    """
    category_id = request.GET.get('category')
    
    events = Event.objects.filter(
        is_published=True, 
        start_datetime__gte=timezone.now()
    ).order_by('start_datetime')
    
    if category_id:
        events = events.filter(category_id=category_id)
        
    categories = EventCategory.objects.all()
    context = {
        'events': events,
        'categories': categories,
        'selected_category': int(category_id) if category_id else None
    }
    
    # === Logika Kunci HTMX ===
    if request.htmx:
        # Jika request dari HTMX, kirim partial HTML-nya saja
        return render(request, 'events/partials/_event_list_items.html', context)
        
    # Jika request biasa, kirim halaman penuh
    return render(request, 'events/event_list.html', context)

def event_detail_view(request, event_id):
    """Menampilkan detail satu event."""
    event = get_object_or_404(Event, id=event_id, is_published=True)
    is_registered = False
    
    if request.user.is_authenticated:
        is_registered = EventRegistration.objects.filter(
            user=request.user, 
            event=event
        ).exists()
        
    context = {
        'event': event,
        'is_registered': is_registered
    }
    return render(request, 'events/event_detail.html', context)

@login_required
def register_event_view(request, event_id):
    """(HTMX POST) Mendaftarkan user ke event."""
    if request.method != "POST":
        return HttpResponseForbidden()

    event = get_object_or_404(Event, id=event_id)
    
    # Buat pendaftaran (get_or_create aman dari duplikasi)
    EventRegistration.objects.get_or_create(user=request.user, event=event)
    
    # Kirim balik partial HTML untuk tombol "Sudah Terdaftar"
    context = {'event': event, 'is_registered': True}
    return render(request, 'events/partials/_rsvp_button_container.html', context)

@login_required
def unregister_event_view(request, event_id):
    """(HTMX POST) Membatalkan pendaftaran user."""
    if request.method != "POST":
        return HttpResponseForbidden()

    event = get_object_or_404(Event, id=event_id)
    
    # Hapus pendaftaran
    EventRegistration.objects.filter(user=request.user, event=event).delete()
    
    # Kirim balik partial HTML untuk tombol "RSVP"
    context = {'event': event, 'is_registered': False}
    return render(request, 'events/partials/_rsvp_button_container.html', context)