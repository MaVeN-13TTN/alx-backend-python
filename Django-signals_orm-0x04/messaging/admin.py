from django.contrib import admin
from .models import Message, Notification


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Admin interface for Message model
    """

    list_display = (
        "message_id",
        "sender",
        "receiver",
        "content_preview",
        "timestamp",
        "is_read",
    )
    list_filter = ("is_read", "timestamp", "sender", "receiver")
    search_fields = (
        "content",
        "sender__username",
        "receiver__username",
        "sender__email",
        "receiver__email",
    )
    readonly_fields = ("message_id", "created_at", "updated_at")
    ordering = ("-timestamp",)
    date_hierarchy = "timestamp"

    fieldsets = (
        (
            "Message Information",
            {"fields": ("message_id", "sender", "receiver", "content")},
        ),
        ("Status", {"fields": ("is_read", "timestamp")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def content_preview(self, obj):
        """
        Display a preview of the message content in the admin list view
        """
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "Content Preview"

    def get_queryset(self, request):
        """
        Optimize the queryset to avoid N+1 queries
        """
        return super().get_queryset(request).select_related("sender", "receiver")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin interface for Notification model
    """

    list_display = (
        "notification_id",
        "user",
        "notification_type",
        "title",
        "created_at",
        "is_read",
    )
    list_filter = ("is_read", "notification_type", "created_at", "user")
    search_fields = ("title", "content", "user__username", "user__email")
    readonly_fields = ("notification_id", "created_at", "updated_at")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Notification Information",
            {"fields": ("notification_id", "user", "message", "notification_type")},
        ),
        ("Content", {"fields": ("title", "content")}),
        ("Status", {"fields": ("is_read",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        """
        Optimize the queryset to avoid N+1 queries
        """
        return (
            super()
            .get_queryset(request)
            .select_related("user", "message", "message__sender")
        )

    actions = ["mark_as_read", "mark_as_unread"]

    def mark_as_read(self, request, queryset):
        """
        Admin action to mark selected notifications as read
        """
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} notifications marked as read.")

    mark_as_read.short_description = "Mark selected notifications as read"

    def mark_as_unread(self, request, queryset):
        """
        Admin action to mark selected notifications as unread
        """
        updated = queryset.update(is_read=False)
        self.message_user(request, f"{updated} notifications marked as unread.")

    mark_as_unread.short_description = "Mark selected notifications as unread"
