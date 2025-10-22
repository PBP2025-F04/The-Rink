from django.db import models
from django.conf import settings # Cara terbaik untuk merujuk ke model User

# Asumsi:
# 1. Model User kustom Anda ada di settings.AUTH_USER_MODEL
# 2. Anda punya app 'booking' dengan model 'Arena' (untuk lokasi event)
# from booking.models import Arena 

class Package(models.Model):
    """
    Model untuk 'Paket' (e.g., Belajar Curling, Sesi Latihan).
    Ini adalah TEMPLATE layanan yang bisa dipesan kapan saja.
    """
    name = models.CharField(max_length=100, verbose_name="Nama Paket")
    description = models.TextField(verbose_name="Deskripsi")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Harga")
    duration_hours = models.FloatField(default=2.0, verbose_name="Durasi (Jam)")
    is_active = models.BooleanField(default=True, verbose_name="Aktif Ditampilkan")

    def __str__(self):
        return self.name

class PackageBooking(models.Model):
    """
    Model untuk 'Transaksi' pemesanan Paket.
    Mencatat SIAPA memesan PAKET APA untuk KAPAN.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="package_bookings"
    )
    package = models.ForeignKey(
        Package, 
        on_delete=models.PROTECT, # Jangan hapus paket jika sudah ada yg booking
        related_name="bookings"
    )
    scheduled_datetime = models.DateTimeField(verbose_name="Jadwal Penggunaan")
    booking_time = models.DateTimeField(auto_now_add=True, verbose_name="Waktu Pemesanan")
    status = models.CharField(
        max_length=20, 
        default="Confirmed", 
        choices=[("Confirmed", "Terkonfirmasi"), ("Cancelled", "Dibatalkan")]
    )

    def __str__(self):
        return f"{self.user.username} - {self.package.name}"

class Event(models.Model):
    """
    Model untuk 'Event' (e.g., Liga, Workshop, Open Skate Night).
    Ini adalah ACARA SPESIFIK dengan jadwal tetap.
    """
    name = models.CharField(max_length=150, verbose_name="Nama Event")
    description = models.TextField(verbose_name="Deskripsi Event")
    start_datetime = models.DateTimeField(verbose_name="Waktu Mulai")
    end_datetime = models.DateTimeField(verbose_name="Waktu Selesai")
    
    # Relasi opsional ke modul Arena
    # location = models.ForeignKey(Arena, on_delete=models.SET_NULL, null=True, blank=True)
    
    registration_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name="Biaya Registrasi"
    )
    max_participants = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Kapasitas Maksimal"
    )
    is_published = models.BooleanField(default=True, verbose_name="Publikasikan")

    def __str__(self):
        return self.name

class EventRegistration(models.Model):
    """
    Model untuk 'Pendaftaran' Event (RSVP).
    Ini adalah Jembatan (Junction Table) antara User dan Event.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="event_registrations"
    )
    event = models.ForeignKey(
        Event, 
        on_delete=models.CASCADE, 
        related_name="registrations" # Memudahkan menghitung: event.registrations.count()
    )
    registration_date = models.DateTimeField(auto_now_add=True, verbose_name="Tanggal Daftar")

    class Meta:
        # Kunci utama: Satu user hanya bisa daftar 1x untuk 1 event
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} terdaftar di {self.event.name}"