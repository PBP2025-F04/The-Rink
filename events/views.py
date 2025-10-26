# events/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone
from .models import Event, EventRegistration
from django.template.loader import render_to_string

def event_list(request):
    """Display all events with optional filtering"""
    category = request.GET.get('category', request.session.get('event_category', 'all'))
    level = request.GET.get('level', request.session.get('event_level', 'all'))
    
    # Simpan filter di session
    request.session['event_category'] = category
    request.session['event_level'] = level

    # Get upcoming events only
    events = Event.objects.filter(
        is_active=True,
        date__gte=timezone.now().date()
    )
    
    # Apply filters
    if category and category != 'all':
        events = events.filter(category=category)
    
    if level and level != 'all':
        events = events.filter(level=level)
    
    # Check if it's an HTMX request
    if request.headers.get('HX-Request'):
        return render(request, 'events/partials/event_list_items.html', {
            'events': events,
        })
     
    return render(request, 'events/list.html', {
        'events': events,
        'selected_category': category,
        'selected_level': level,
        'categories': Event.CATEGORY_CHOICES,
        'levels': Event.LEVEL_CHOICES
    })


def event_detail(request, slug):
    """Display detailed event information"""
    event = get_object_or_404(Event, slug=slug, is_active=True)
    
    # Get related events (same category, different event)
    related_events = Event.objects.filter(
        category=event.category,
        is_active=True,
        date__gte=timezone.now().date()
    ).exclude(id=event.id)[:3]
    
    context = {
        'event': event,
        'related_events': related_events,
        'is_registered': event.is_registered(request.user)
    }
    
    return render(request, 'events/detail.html', context)


@login_required
def get_registration_modal(request, slug):
    """
    Mengembalikan konten HTML untuk modal pendaftaran.
    Dipanggil via HTMX GET.
    """
    event = get_object_or_404(Event, slug=slug, is_active=True)
    return render(request, 'events/partials/registration_modal.html', {
        'event': event
    })


@login_required
@require_http_methods(["POST"])
def register_event(request, slug):
    """
    Memproses pendaftaran event (dari modal HTMX).
    Mengembalikan partial button baru dan trigger untuk menutup modal.
    """
    event = get_object_or_404(Event, slug=slug, is_active=True)
    
    # Cek jika event penuh
    if event.is_full:
        messages.error(request, 'Sorry, this event is fully booked.')
        return render(request, 'events/partials/registration_modal.html', {'event': event})

    # Cek jika sudah terdaftar
    if event.is_registered(request.user):
        messages.error(request, 'You are already registered for this event.')
        return render(request, 'events/partials/registration_modal.html', {'event': event})

    # Cek jika event sudah lewat
    if event.is_past:
        messages.error(request, 'Cannot register for past events.')
        return render(request, 'events/partials/registration_modal.html', {'event': event})

    # Daftarkan user
    # HANYA BUAT EventRegistration, 'participants.add' sudah dihapus
    EventRegistration.objects.create(event=event, user=request.user)
    
    # Siapkan partial button baru
    html = render_to_string('events/partials/event_book_button.html', {
        'event': event,
        'is_registered': True,
        'user': request.user
    })
    
    # Kirim response HTMX
    response = HttpResponse(html)
    response['HX-Trigger'] = 'closeModal' # Trigger custom event 'closeModal'
    messages.success(request, f'Successfully registered for {event.name}!')
    return response


@login_required
@require_http_methods(["POST"])
def cancel_registration(request, slug):
    """
    Membatalkan pendaftaran (HTMX endpoint).
    Mengembalikan partial button baru.
    """
    event = get_object_or_404(Event, slug=slug, is_active=True)
    
    # Hapus pendaftaran
    registration = EventRegistration.objects.filter(event=event, user=request.user)
    
    if registration.exists():
        registration.delete()
        messages.success(request, 'Registration cancelled successfully.')
    else:
        messages.error(request, 'You were not registered for this event.')

    # Kembalikan partial button baru
    return render(request, 'events/partials/event_book_button.html', {
        'event': event,
        'is_registered': False,
        'user': request.user
    })


@login_required
def my_events(request):
    """Display user's registered events"""
    registrations = request.user.event_registrations.select_related('event').all()

    upcoming_regs = registrations.filter(
        event__date__gte=timezone.now().date()
    ).order_by('event__date', 'event__start_time')

    past_regs = registrations.filter(
        event__date__lt=timezone.now().date()
    ).order_by('-event__date', '-event__start_time')

    return render(request, 'events/my_events.html', {
        'upcoming_registrations': upcoming_regs,
        'past_registrations': past_regs
    })

# Admin views for events
def admin_event_list(request):
    if not request.session.get('is_admin'):
        return redirect('authentication:login')
    events = Event.objects.all()
    return render(request, 'events/admin_event_list.html', {'events': events})

def admin_event_create(request):
    if not request.session.get('is_admin'):
        return redirect('authentication:login')
    from .forms import EventForm
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.slug = slugify(event.name)
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('events:admin_event_list')
    else:
        form = EventForm()
    return render(request, 'events/admin_event_form.html', {'form': form, 'action': 'Create'})

def admin_event_update(request, id):
    if not request.session.get('is_admin'):
        return redirect('authentication:login')
    from .forms import EventForm
    event = get_object_or_404(Event, id=id)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            event = form.save(commit=False)
            event.slug = slugify(event.name)
            event.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('events:admin_event_list')
    else:
        form = EventForm(instance=event)
    return render(request, 'events/admin_event_form.html', {'form': form, 'action': 'Update'})

def admin_event_delete(request, id):
    if not request.session.get('is_admin'):
        return redirect('authentication:login')
    event = get_object_or_404(Event, id=id)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('events:admin_event_list')
    return render(request, 'events/admin_event_confirm_delete.html', {'event': event})
