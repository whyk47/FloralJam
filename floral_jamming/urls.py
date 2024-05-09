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
    path("create/<int:event_id>", views.create, name="create"),
    path("details/<int:event_id>", views.details, name="details"),
    path("sign_up/<int:event_id>", views.sign_up, name="sign_up"),
    path("cancel_sign_up/<int:event_id>", views.cancel_sign_up, name="cancel_sign_up"),
    path("email_verified/<int:user_id>/<str:token_id>", views.email_verified, name="email_verified"),
    path("verify_email/<int:user_id>/<str:path>/<int:event_id>", views.verify_email, name="verify_email"),
    path("verify_email/<int:user_id>/<str:path>", views.verify_email, name="verify_email"),
    path("forgot_password", views.forgot_password, name="forgot_password"),
    path("forgot_password/<int:event_id>", views.forgot_password, name="forgot_password"),
    path("reset_password/<int:user_id>/<str:token_id>", views.reset_password, name="reset_password"),

]
