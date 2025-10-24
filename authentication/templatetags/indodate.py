from django import template

register = template.Library()

MONTHS = [
    'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
    'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
]


@register.filter(is_safe=True)
def indodate(value):
    """Format a date/datetime/date-like object to 'D Month YYYY' in Indonesian.

    If value is falsy, returns empty string.
    """
    if not value:
        return ''
    try:
        day = getattr(value, 'day', None)
        month = getattr(value, 'month', None)
        year = getattr(value, 'year', None)
        if day and month and year:
            return f"{day} {MONTHS[month - 1]} {year}"
    except Exception:
        pass
    # Fallback to default string conversion
    return str(value)
