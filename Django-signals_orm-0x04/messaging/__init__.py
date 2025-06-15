"""
Messaging App - Django Signals Implementation

This app demonstrates the implementation of Django signals for automatic
user notifications when messages are received.

Key Components:
- Message model: Stores messages between users
- Notification model: Stores notifications for users
- Signals: Automatically create notifications when messages are sent
- Admin interface: Manage messages and notifications
- Tests: Comprehensive test coverage for models and signals

Author: Django Signals Learning Module
Date: June 2025
"""

default_app_config = "messaging.apps.MessagingConfig"
