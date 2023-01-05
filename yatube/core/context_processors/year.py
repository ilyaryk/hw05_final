from django.utils import timezone


def year(request):
    """Добавляет переменную с текущим годом."""
    return {'current_year': timezone.now().year}
