"""
URL configuration for flowgate project.
"""

from django.contrib import admin
from django.urls import path
from parqueadero import views as pViews

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", pViews.home, name="home"),
    path("login/", pViews.login_view, name="login_view"),
    path("logout/", pViews.logout_view, name="logout_view"),
    path("profile/", pViews.profile, name="profile"),
    path("history/", pViews.history, name="history"),
    path("payments/", pViews.payments, name="payments"),
]