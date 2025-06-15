from django.contrib import admin
from .models import Message, Notification, MessageHistory


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
        "edited",
        "edit_count",
    )
    list_filter = ("is_read", "edited", "timestamp", "sender", "receiver")
    search_fields = (
        "content",
        "sender__username",
        "receiver__username",
        "sender__email",
        "receiver__email",
    )
    readonly_fields = ("message_id", "edited", "edit_count", "created_at", "updated_at")
    ordering = ("-timestamp",)
    date_hierarchy = "timestamp"

    fieldsets = (
        (
            "Message Information",
            {"fields": ("message_id", "sender", "receiver", "content")},
        ),
        ("Status", {"fields": ("is_read", "timestamp")}),
        ("Edit Information", {"fields": ("edited", "edit_count")}),
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


@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    """
    Admin interface for MessageHistory model
    """

    list_display = (
        "history_id",
        "message_preview",
        "edited_by",
        "edited_at",
        "edit_summary",
        "content_changed",
    )
    list_filter = ("edited_at", "edited_by", "message__sender", "message__receiver")
    search_fields = (
        "old_content",
        "new_content",
        "edit_reason",
        "edited_by__username",
        "message__content",
    )
    readonly_fields = (
        "history_id",
        "edited_at",
        "content_changed",
        "edit_summary",
    )
    ordering = ("-edited_at",)
    date_hierarchy = "edited_at"

    fieldsets = (
        (
            "History Information",
            {"fields": ("history_id", "message", "edited_by", "edited_at")},
        ),
        (
            "Content Changes",
            {"fields": ("old_content", "new_content", "edit_reason")},
        ),
        (
            "Metadata",
            {"fields": ("content_changed", "edit_summary"), "classes": ("collapse",)},
        ),
    )

    def message_preview(self, obj):
        """
        Display a preview of the message being edited
        """
        return f"Message from {obj.message.sender.username} to {obj.message.receiver.username}"

    message_preview.short_description = "Message"

    def get_queryset(self, request):
        """
        Optimize the queryset to avoid N+1 queries
        """
        return super().get_queryset(request).select_related(
            "message",
            "message__sender",
            "message__receiver",
            "edited_by",
        )

    def has_add_permission(self, request):
        """
        Prevent manual creation of history records through admin
        """
        return False

    def has_change_permission(self, request, obj=None):
        """
        Make history records read-only
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Allow deletion for cleanup purposes
        """
        return request.user.is_superuser


# Inline admin for showing message history within message admin
class MessageHistoryInline(admin.TabularInline):
    """
    Inline admin to show message history within message admin
    """

    model = MessageHistory
    extra = 0
    readonly_fields = (
        "old_content",
        "new_content",
        "edit_reason",
        "edited_by",
        "edited_at",
        "edit_summary",
    )
    fields = (
        "edited_at",
        "edited_by",
        "old_content",
        "new_content",
        "edit_reason",
        "edit_summary",
    )

    def has_add_permission(self, request, obj=None):
        """
        Prevent manual creation of history records
        """
        return False

    def has_change_permission(self, request, obj=None):
        """
        Make history records read-only
        """
        return False


# Update MessageAdmin to include history inline
MessageAdmin.inlines = [MessageHistoryInline]
