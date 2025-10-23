from django.shortcuts import render, get_object_or_404, redirect
from .models import Arena, Booking
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.views.decorators.http import require_POST


def arena_list(request):
	arenas = Arena.objects.all()
	return render(request, 'booking_arena/arena_list.html', {'arenas': arenas})


def arena_detail(request, pk):
	arena = get_object_or_404(Arena, pk=pk)
	return render(request, 'booking_arena/arena_detail.html', {'arena': arena})


@login_required
def my_bookings(request):
	bookings = Booking.objects.filter(user=request.user).order_by('-date', '-start_time')
	return render(request, 'booking_arena/my_bookings.html', {'bookings': bookings})


@require_POST
def ajax_book_arena(request, pk):
	if not request.user.is_authenticated:
		return JsonResponse({'success': False, 'login_required': True, 'message': 'Please login to book.'}, status=401)

	arena = get_object_or_404(Arena, pk=pk)
	try:
		body = json.loads(request.body.decode() or '{}')
		date = body.get('date')
		start_time = body.get('start_time')
		end_time = body.get('end_time')
	except Exception:
		return JsonResponse({'success': False, 'message': 'Invalid data'}, status=400)

	# Basic availability check: no overlapping confirmed bookings
	overlapping = Booking.objects.filter(arena=arena, date=date, status__in=['pending','confirmed']).filter(
		start_time__lt=end_time, end_time__gt=start_time
	)
	if overlapping.exists():
		return JsonResponse({'success': False, 'message': 'Time slot not available.'})

	b = Booking.objects.create(
		user=request.user,
		arena=arena,
		date=date,
		start_time=start_time,
		end_time=end_time,
		status='pending'
	)
	return JsonResponse({'success': True, 'message': 'Booking requested', 'booking_id': b.id})


@require_POST
def ajax_cancel_booking(request, pk):
	if not request.user.is_authenticated:
		return JsonResponse({'success': False, 'login_required': True, 'message': 'Please login.'}, status=401)
	b = get_object_or_404(Booking, pk=pk, user=request.user)
	b.status = 'cancelled'
	b.save()
	return JsonResponse({'success': True, 'message': 'Booking cancelled'})
