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
    path("api/", include(router.urls)),
    # Custom threading endpoints
    path(
        "api/messages/<uuid:message_id>/thread/",
        views.get_message_thread,
        name="message_thread",
    ),
    path(
        "api/messages/<uuid:message_id>/reply/",
        views.reply_to_message,
        name="reply_to_message",
    ),
    # User account deletion endpoints
    path("user/delete/", views.delete_user_account, name="delete_user_account"),
    path(
        "user/delete-with-confirmation/",
        views.delete_user_with_confirmation,
        name="delete_user_with_confirmation",
    ),
    path("user/data-summary/", views.get_user_data_summary, name="user_data_summary"),
]
