from django.urls import path

from parqueadero import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login_view"),
    path("logout/", views.logout_view, name="logout_view"),
    path("heading/", views.heading, name="heading"),
    path("heading/status/", views.heading_status, name="heading_status"),
    path("profile/", views.profile, name="profile"),
    path("history/", views.history, name="history"),
    path("payments/", views.payments, name="payments"),
    path("payments/recharge/", views.create_recharge, name="create_recharge"),
    path("payments/demo/", views.demo_payment, name="demo_payment"),
    path("payments/wompi/return/", views.wompi_return, name="wompi_return"),
    path("payments/wompi/webhook/", views.wompi_webhook, name="wompi_webhook"),
    path("panel-admin/", views.admin_panel, name="admin_panel"),
]

