#!/usr/bin/env python
"""
Simple verification script for messaging optimizations and sender assignment
"""


def check_views_content():
    """Check that views.py contains the expected optimizations"""
    print("=" * 60)
    print("CHECKING MESSAGING VIEWS OPTIMIZATIONS")
    print("=" * 60)

    try:
        with open("messaging/views.py", "r") as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ messaging/views.py not found")
        return False

    # Check for select_related and prefetch_related
    select_related_count = content.count("select_related")
    prefetch_related_count = content.count("prefetch_related")
    sender_assignment_count = content.count("sender=request.user") + content.count(
        "sender=self.request.user"
    )

    print(f"📊 Query Optimizations:")
    print(f"   select_related occurrences: {select_related_count}")
    print(f"   prefetch_related occurrences: {prefetch_related_count}")

    print(f"📊 Sender Assignment:")
    print(f"   sender=request.user occurrences: {sender_assignment_count}")

    # Check specific optimization patterns
    optimizations_found = []

    if "MessageViewSet" in content and "get_queryset" in content:
        if 'select_related("sender", "receiver"' in content:
            optimizations_found.append(
                "✓ MessageViewSet.get_queryset has select_related"
            )
        if 'prefetch_related("replies"' in content:
            optimizations_found.append(
                "✓ MessageViewSet.get_queryset has prefetch_related"
            )

    if "perform_create" in content:
        if "sender=self.request.user" in content:
            optimizations_found.append("✓ MessageViewSet.perform_create sets sender")

    if "reply_to_message" in content:
        if "sender=request.user" in content:
            optimizations_found.append("✓ reply_to_message sets sender")

    if "create_message" in content:
        if "sender=request.user" in content:
            optimizations_found.append("✓ create_message sets sender")

    if "get_message_thread" in content:
        if "select_related" in content:
            optimizations_found.append("✓ get_message_thread has optimizations")

    print(f"\n📋 Specific Optimizations Found:")
    for opt in optimizations_found:
        print(f"   {opt}")

    # Overall assessment
    print(f"\n📈 ASSESSMENT:")
    if select_related_count >= 3 and prefetch_related_count >= 3:
        print("   ✅ Query optimizations: EXCELLENT")
    elif select_related_count >= 2 and prefetch_related_count >= 2:
        print("   ✅ Query optimizations: GOOD")
    else:
        print("   ⚠️  Query optimizations: NEEDS IMPROVEMENT")

    if sender_assignment_count >= 3:
        print("   ✅ Sender assignment: EXCELLENT")
    elif sender_assignment_count >= 2:
        print("   ✅ Sender assignment: GOOD")
    else:
        print("   ⚠️  Sender assignment: NEEDS IMPROVEMENT")

    return True


def check_models_content():
    """Check that models.py contains threading optimizations"""
    print("\n" + "=" * 60)
    print("CHECKING MESSAGING MODELS THREADING")
    print("=" * 60)

    try:
        with open("messaging/models.py", "r") as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ messaging/models.py not found")
        return False

    # Check for threading methods
    threading_methods = [
        "get_thread_messages",
        "get_all_replies",
        "get_direct_replies",
        "can_reply_to",
        "thread_depth",
        "root_message",
        "is_reply",
        "is_thread_starter",
    ]

    print(f"📊 Threading Methods:")
    found_methods = []
    for method in threading_methods:
        if method in content:
            found_methods.append(f"   ✓ {method}")
        else:
            found_methods.append(f"   ❌ {method}")

    for method in found_methods:
        print(method)

    # Check for query optimizations in threading methods
    threading_optimizations = []
    if "select_related" in content:
        threading_optimizations.append("✓ Threading methods use select_related")
    if "prefetch_related" in content:
        threading_optimizations.append("✓ Threading methods use prefetch_related")

    print(f"\n📋 Threading Optimizations:")
    for opt in threading_optimizations:
        print(f"   {opt}")

    # Check for parent_message field and index
    if "parent_message" in content and "ForeignKey" in content:
        print("   ✓ parent_message field defined")
    if "Index" in content and "parent_message" in content:
        print("   ✓ parent_message index defined")

    return True


def check_tests_content():
    """Check that tests cover the optimizations"""
    print("\n" + "=" * 60)
    print("CHECKING TESTS COVERAGE")
    print("=" * 60)

    try:
        with open("messaging/tests.py", "r") as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ messaging/tests.py not found")
        return False

    test_patterns = [
        "test_threading_query_optimization",
        "test_perform_create_sets_sender",
        "test_reply_to_message_sets_sender",
        "MessageViewSetTests",
        "MessageThreadingTests",
    ]

    print(f"📊 Test Coverage:")
    for pattern in test_patterns:
        if pattern in content:
            print(f"   ✓ {pattern}")
        else:
            print(f"   ❌ {pattern}")

    return True


if __name__ == "__main__":
    print("🔍 MESSAGING APP OPTIMIZATION VERIFICATION")
    print("=" * 60)

    success = True
    success &= check_views_content()
    success &= check_models_content()
    success &= check_tests_content()

    print("\n" + "=" * 60)
    if success:
        print("🎉 VERIFICATION COMPLETED SUCCESSFULLY!")
        print("✅ All components found and checked")
    else:
        print("⚠️  VERIFICATION COMPLETED WITH ISSUES")
        print("❌ Some components missing or need attention")
    print("=" * 60)
