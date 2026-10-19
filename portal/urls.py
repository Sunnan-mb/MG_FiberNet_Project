from django.urls import path
from . import views

urlpatterns = [
    # Three distinct portal entry points
    path("", views.customer_dashboard, name="dashboard"),
    path("customer/", views.customer_dashboard, name="customer_dashboard"),
    path("employee/", views.employee_dashboard, name="employee_dashboard"),
    path("employee/ticket/<int:ticket_id>/", views.ticket_detail, name="ticket_detail"),
    path("admin-portal/", views.admin_dashboard, name="admin_dashboard"),
    path("notifications/", views.notifications, name="notifications"),
    path("login/", views.CustomerLoginView.as_view(), name="login"),
    path("employee/login/", views.CustomerLoginView.as_view(template_name="portal/login.html"), name="employee_login"),
    path("admin-portal/login/", views.CustomerLoginView.as_view(template_name="portal/login.html"), name="admin_login"),
    path("logout/", views.logout_view, name="logout"),
    path("login/otp/", views.otp_request, name="otp_request"),
    path("login/otp/verify/", views.otp_verify, name="otp_verify"),
    path("complaints/new/", views.raise_complaint, name="raise_complaint"),
    path("complaints/", views.my_complaints, name="my_complaints"),
    path("plans/", views.plans, name="plans"),
    path("plans/<int:plan_id>/callback/", views.request_callback, name="request_callback"),
]
