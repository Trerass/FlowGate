from django.urls import path

from parqueadero import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login_view"),
    path("logout/", views.logout_view, name="logout_view"),
    path("heading/", views.heading, name="heading"),
    path("profile/", views.profile, name="profile"),
    path("history/", views.history, name="history"),
    path("payments/", views.payments, name="payments"),
]

