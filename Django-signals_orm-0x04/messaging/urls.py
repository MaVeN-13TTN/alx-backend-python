from django.urls import path
from . import views

app_name = "messaging"

urlpatterns = [
    # User account deletion endpoints
    path("user/delete/", views.delete_user_account, name="delete_user_account"),
    path(
        "user/delete-with-confirmation/",
        views.delete_user_with_confirmation,
        name="delete_user_with_confirmation",
    ),
    path("user/data-summary/", views.get_user_data_summary, name="user_data_summary"),
]
