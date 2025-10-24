# events/admin.py
from django.contrib import admin
from .models import Event, EventRegistration

class EventRegistrationInline(admin.TabularInline):
    """
    Memungkinkan admin melihat & mengedit pendaftar
    langsung di halaman detail Event.
    """
    model = EventRegistration
    extra = 0  
    readonly_fields = ('user', 'registered_at') 
    fields = ('user', 'registered_at', 'attended', 'notes')
    can_delete = True

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """
    Kustomisasi tampilan Admin untuk Event.
    """
    inlines = [EventRegistrationInline] 
    list_display = (
        'name', 
        'date', 
        'start_time', 
        'category', 
        'level', 
        'price',
        'current_participants',
        'max_participants',
        'is_full',
        'is_active'
    )
    list_filter = ('category', 'level', 'date', 'is_active')
    search_fields = ('name', 'description', 'instructor')
    prepopulated_fields = {'slug': ('name',)} 
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'image', 'description', 'requirements')
        }),
        ('Schedule & Location', {
            'fields': ('date', 'start_time', 'end_time', 'location')
        }),
        ('Details', {
            'fields': ('category', 'level', 'price', 'max_participants', 'is_active')
        }),
        ('Personnel', {
            'fields': ('organizer', 'instructor')
        }),
    )

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    """
    Tampilan admin terpisah untuk melihat semua pendaftaran.
    """
    list_display = ('event', 'user', 'registered_at', 'attended')
    list_filter = ('event__category', 'attended', 'registered_at')
    search_fields = ('event__name', 'user__username', 'user__email')
    list_editable = ('attended',)