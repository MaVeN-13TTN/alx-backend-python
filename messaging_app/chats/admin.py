from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Conversation, Message


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom admin configuration for User model"""

    list_display = (
        "username",
        "email",
        "phone_number",
        "is_online",
        "last_seen",
        "date_joined",
    )
    list_filter = ("is_online", "is_staff", "is_active", "date_joined")
    search_fields = ("username", "email", "phone_number")
    ordering = ("-date_joined",)

    fieldsets = UserAdmin.fieldsets + (
        (
            "Additional Info",
            {"fields": ("phone_number", "profile_picture", "is_online")},
        ),
    )


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Admin configuration for Conversation model"""

    list_display = ("conversation_id", "get_participants", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("participants__username", "participants__email")
    filter_horizontal = ("participants",)
    readonly_fields = ("conversation_id", "created_at", "updated_at")
    ordering = ("-updated_at",)

    def get_participants(self, obj):
        """Display participants in the admin list view"""
        return ", ".join([user.username for user in obj.participants.all()[:3]])

    get_participants.short_description = "Participants"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin configuration for Message model"""

    list_display = (
        "message_id",
        "sender",
        "get_conversation_participants",
        "message_body_preview",
        "created_at",
    )
    list_filter = ("created_at", "updated_at")
    search_fields = (
        "sender__username",
        "message_body",
        "conversation__participants__username",
    )
    readonly_fields = ("message_id", "created_at", "updated_at")
    ordering = ("-created_at",)

    def message_body_preview(self, obj):
        """Show a preview of the message body"""
        return (
            obj.message_body[:100] + "..."
            if len(obj.message_body) > 100
            else obj.message_body
        )

    message_body_preview.short_description = "Message Preview"

    def get_conversation_participants(self, obj):
        """Display conversation participants"""
        return ", ".join(
            [user.username for user in obj.conversation.participants.all()[:2]]
        )

    get_conversation_participants.short_description = "Conversation"
