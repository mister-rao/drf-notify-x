from django.urls import path

from notify.api import notifications, notification_update, mark, mark_all, delete

app_name = 'notifications'

"""
app: notifications
prefix: v1/notifications/

1. v1/notifications/all/ - show all notifications
2. v1/notifications/update/ - update notification
3. v1/notifications/mark/ - 
4. v1/notifications/mark-all/
5. v1/notifications/delete/<int:notification_id>
"""

urlpatterns = [
    path('all/', notifications, name='all-notifications'),
    path('update/', notification_update, name="update"),
    path('mark/', mark, name='mark'),
    path('mark-all/', mark_all, name='mark_all'),
    path('delete/<int:notification_id>/', delete, name='delete'),
]