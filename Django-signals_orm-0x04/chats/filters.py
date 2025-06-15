"""
Custom filter classes for the messaging app using django-filter
"""

import django_filters
from django.db import models
from django.contrib.auth import get_user_model
from .models import Message, Conversation, User


class MessageFilter(django_filters.FilterSet):
    """
    Filter class for Message model
    Allows filtering messages by various criteria including time ranges and specific users
    """
    
    # Filter by sender
    sender = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        field_name='sender',
        to_field_name='user_id'
    )
    
    # Filter by conversation
    conversation = django_filters.ModelChoiceFilter(
        queryset=Conversation.objects.all(),
        field_name='conversation',
        to_field_name='conversation_id'
    )
    
    # Filter by message content (case-insensitive search)
    message_body = django_filters.CharFilter(
        field_name='message_body',
        lookup_expr='icontains'
    )
    
    # Date range filters for message creation
    sent_at_after = django_filters.DateTimeFilter(
        field_name='sent_at',
        lookup_expr='gte',
        help_text='Filter messages sent after this date/time (YYYY-MM-DD HH:MM:SS)'
    )
    
    sent_at_before = django_filters.DateTimeFilter(
        field_name='sent_at',
        lookup_expr='lte',
        help_text='Filter messages sent before this date/time (YYYY-MM-DD HH:MM:SS)'
    )
    
    # Date range filters (date only)
    sent_date = django_filters.DateFilter(
        field_name='sent_at',
        lookup_expr='date',
        help_text='Filter messages sent on a specific date (YYYY-MM-DD)'
    )
    
    sent_date_after = django_filters.DateFilter(
        field_name='sent_at',
        lookup_expr='date__gte',
        help_text='Filter messages sent after this date (YYYY-MM-DD)'
    )
    
    sent_date_before = django_filters.DateFilter(
        field_name='sent_at',
        lookup_expr='date__lte',
        help_text='Filter messages sent before this date (YYYY-MM-DD)'
    )
    
    # Filter by conversation participants (useful for finding messages with specific users)
    conversation_participant = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        field_name='conversation__participants',
        to_field_name='user_id',
        help_text='Filter messages from conversations that include this user'
    )
    
    # Filter by sender username (case-insensitive)
    sender_username = django_filters.CharFilter(
        field_name='sender__username',
        lookup_expr='icontains',
        help_text='Filter messages by sender username (case-insensitive)'
    )
    
    class Meta:
        model = Message
        fields = [
            'sender',
            'conversation',
            'message_body',
            'sent_at_after',
            'sent_at_before',
            'sent_date',
            'sent_date_after',
            'sent_date_before',
            'conversation_participant',
            'sender_username'
        ]


class ConversationFilter(django_filters.FilterSet):
    """
    Filter class for Conversation model
    Allows filtering conversations by participants and time ranges
    """
    
    # Filter by participant
    participant = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        field_name='participants',
        to_field_name='user_id',
        help_text='Filter conversations that include this user'
    )
    
    # Filter by participant username
    participant_username = django_filters.CharFilter(
        field_name='participants__username',
        lookup_expr='icontains',
        help_text='Filter conversations by participant username (case-insensitive)'
    )
    
    # Date range filters for conversation creation
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text='Filter conversations created after this date/time'
    )
    
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text='Filter conversations created before this date/time'
    )
    
    # Filter by last message time
    last_message_after = django_filters.DateTimeFilter(
        method='filter_last_message_after',
        help_text='Filter conversations with last message after this date/time'
    )
    
    last_message_before = django_filters.DateTimeFilter(
        method='filter_last_message_before',
        help_text='Filter conversations with last message before this date/time'
    )
    
    def filter_last_message_after(self, queryset, name, value):
        """
        Custom filter method for filtering by last message time (after)
        """
        return queryset.filter(messages__sent_at__gte=value).distinct()
    
    def filter_last_message_before(self, queryset, name, value):
        """
        Custom filter method for filtering by last message time (before)
        """
        return queryset.filter(messages__sent_at__lte=value).distinct()
    
    class Meta:
        model = Conversation
        fields = [
            'participant',
            'participant_username',
            'created_after',
            'created_before',
            'last_message_after',
            'last_message_before'
        ]


class UserFilter(django_filters.FilterSet):
    """
    Filter class for User model
    """
    
    # Filter by online status
    is_online = django_filters.BooleanFilter(
        field_name='is_online',
        help_text='Filter users by online status'
    )
    
    # Filter by username (case-insensitive search)
    username = django_filters.CharFilter(
        field_name='username',
        lookup_expr='icontains',
        help_text='Filter users by username (case-insensitive)'
    )
    
    # Filter by email (case-insensitive search)
    email = django_filters.CharFilter(
        field_name='email',
        lookup_expr='icontains',
        help_text='Filter users by email (case-insensitive)'
    )
    
    # Filter by first name
    first_name = django_filters.CharFilter(
        field_name='first_name',
        lookup_expr='icontains',
        help_text='Filter users by first name (case-insensitive)'
    )
    
    # Filter by last name
    last_name = django_filters.CharFilter(
        field_name='last_name',
        lookup_expr='icontains',
        help_text='Filter users by last name (case-insensitive)'
    )
    
    # Date range filters for user registration
    joined_after = django_filters.DateFilter(
        field_name='date_joined',
        lookup_expr='gte',
        help_text='Filter users who joined after this date'
    )
    
    joined_before = django_filters.DateFilter(
        field_name='date_joined',
        lookup_expr='lte',
        help_text='Filter users who joined before this date'
    )
    
    class Meta:
        model = User
        fields = [
            'is_online',
            'username',
            'email',
            'first_name',
            'last_name',
            'joined_after',
            'joined_before'
        ]
