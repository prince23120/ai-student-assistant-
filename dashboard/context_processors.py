from notifications.models import Notification

def global_context(request):
    if not request.user.is_authenticated:
        return {
            'unread_notifications_count': 0,
            'recent_notifications': [],
        }

    notifications_qs = Notification.objects.filter(user=request.user)
    unread_count = notifications_qs.filter(is_read=False).count()
    recent = notifications_qs[:5]

    return {
        'unread_notifications_count': unread_count,
        'recent_notifications': recent,
    }
