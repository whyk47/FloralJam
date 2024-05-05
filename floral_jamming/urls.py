from django.urls import path
from . import views

app_name = "floral_jamming"
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("login/<int:event_id>", views.login_view, name="login"),
    path("register/<int:event_id>", views.register, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("create", views.create, name="create"),
    path("details/<int:event_id>", views.details, name="details"),
    path("cancel_sign_up/<int:event_id>", views.cancel_sign_up, name="cancel_sign_up"),
]
