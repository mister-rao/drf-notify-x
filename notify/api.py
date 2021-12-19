"""
All Apis for notifications are modifications notify's views to comply with REST.
"""
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from notify.models import Notification
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .serializers import NotificationSerializer


class SmallPagesPagination(PageNumberPagination):
    page_size = 10


@api_view(['GET'])
def notifications(request):
    """
    Returns all notifications for the logged-in user.

    :param request: HTTP request context.
    :return: json notification list
    """
    paginator = SmallPagesPagination()
    if request.method == 'GET':
        notification_list = request.user.notifications.active().prefetch()
        _notifications = paginator.paginate_queryset(notification_list, request)
        serializer = NotificationSerializer(_notifications, many=True)
        return paginator.get_paginated_response(serializer.data)


# TODO: add pagination
@api_view(['POST'])
@login_required
def mark(request):
    """
    Mark a notification as read or unread.
    """
    notification_id = request.data.get('id', None)
    action = request.data.get('action', None)
    success = True

    if notification_id:
        try:
            notification = Notification.objects.get(pk=notification_id,
                                                    recipient=request.user)
            if action == 'read':
                notification.mark_as_read()
                msg = _("Marked as read")
            elif action == 'unread':
                notification.mark_as_unread()
                msg = _("Marked as unread")
            else:
                success = False
                msg = _("Invalid mark action.")
        except Notification.DoesNotExist:
            success = False
            msg = _("Notification does not exists.")
    else:
        success = False
        msg = _("Invalid Notification ID")

    ctx = {'msg': msg, 'success': success, 'action': action}

    return Response(ctx, status.HTTP_200_OK)


@api_view(['POST'])
@login_required
def mark_all(request):
    """
    Mark all notification as read or unread.
    """
    action = request.data.get('action', None)
    success = True

    if action == 'read':
        request.user.notifications.read_all()
        msg = _("Marked all notifications as read")
    elif action == 'unread':
        request.user.notifications.unread_all()
        msg = _("Marked all notifications as unread")
    else:
        msg = _("Invalid mark action")
        success = False

    ctx = {'msg': msg, 'success': success, 'action': action}

    return Response(ctx, status.HTTP_200_OK)


@api_view(['GET'])
@login_required
def delete(request, *args, **kwargs):
    """
    Mark a notification as deleted. Notification is soft-deleted by default.
    """
    notification_id = kwargs.pop('notification_id', None)
    success = True

    if notification_id:
        try:
            notification = Notification.objects.get(pk=notification_id,
                                                    recipient=request.user, deleted=False)
            soft_delete = getattr(settings, 'NOTIFY_SOFT_DELETE', True)
            if soft_delete:
                notification.deleted = True
                notification.save()
            else:
                notification.delete()
            msg = _("Deleted notification successfully")
        except Notification.DoesNotExist:
            success = False
            msg = _("Notification does not exists.")
    else:
        success = False
        msg = _("Invalid Notification ID")

    ctx = {'msg': msg, 'success': success, }

    return Response(ctx, status.HTTP_200_OK)


@api_view(['GET'])
@login_required
def notification_update(request):
    """
    live notification updates using ajax-polling.

    Read more: https://stackoverflow.com/a/12855533/4726598

    Required URL parameters: ``flag``: last notification id received by user.
    """
    flag = request.GET.get('flag', None)
    target = request.GET.get('target', 'box')
    last_notification = None
    if flag is not None:
        last_notification = int(flag) if flag.isdigit() else None

    if last_notification:

        new_notifications = request.user.notifications.filter(
            id__gt=last_notification).active().prefetch()

        msg = _("Notifications successfully retrieved.") \
            if new_notifications else _("No new notifications.")

        serializer = NotificationSerializer(new_notifications, many=True)

        ctx = {
            "retrieved": len(new_notifications),
            "unread_count": request.user.notifications.unread().count(),
            "notifications": serializer.data,
            "success": True,
            "msg": msg,
        }

        return Response(ctx, status.HTTP_200_OK)

    else:
        msg = _("Notification flag not sent.")

    ctx = {"success": False, "msg": msg}
    return Response(ctx, status.HTTP_200_OK)
