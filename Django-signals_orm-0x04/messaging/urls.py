from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "messaging"

# Create router for ViewSets
router = DefaultRouter()
router.register(r"messages", views.MessageViewSet, basename="message")
router.register(r"notifications", views.NotificationViewSet, basename="notification")

urlpatterns = [
    # ViewSet routes
    path("", include(router.urls)),
    # Custom message creation endpoint
    path("messages/create/", views.create_message, name="create_message"),
    # Custom threading endpoints
    path(
        "messages/<uuid:message_id>/thread/",
        views.get_message_thread,
        name="message_thread",
    ),
    path(
        "messages/<uuid:message_id>/reply/",
        views.reply_to_message,
        name="reply_to_message",
    ),
    # Unread messages endpoints - using different paths to avoid conflicts with ViewSet
    path("unread-messages/", views.get_unread_messages, name="unread_messages"),
    path("user-inbox/", views.get_user_inbox, name="user_inbox"),
    path("unread-count/", views.get_unread_count, name="unread_count"),
    path(
        "messages/<uuid:message_id>/mark-read/",
        views.mark_message_read,
        name="mark_message_read",
    ),
    path("mark-all-read/", views.mark_all_messages_read, name="mark_all_messages_read"),
    # User account deletion endpoints
    path("user/delete/", views.delete_user_account, name="delete_user_account"),
    path(
        "user/delete-with-confirmation/",
        views.delete_user_with_confirmation,
        name="delete_user_with_confirmation",
    ),
    path("user/data-summary/", views.get_user_data_summary, name="user_data_summary"),
]
