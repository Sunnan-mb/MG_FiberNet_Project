import random
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from .forms import CustomerLoginForm, ComplaintForm, CallbackRequestForm
from .models import Complaint, Plan, Notification, TicketActivity, UserProfile, CustomerProfile

User = get_user_model()

class CustomerLoginView(LoginView):
    template_name = "portal/login.html"
    authentication_form = CustomerLoginForm
    redirect_authenticated_user = True
    def get_success_url(self):
        role = profile_role(self.request.user)
        return {"admin": "/admin-portal/", "employee": "/employee/", "customer": "/customer/"}.get(role, "/customer/")

def profile_role(user):
    if user.is_superuser or user.is_staff: return "admin"
    try: return user.mg_profile.role
    except UserProfile.DoesNotExist: return "customer"

def employee_required(view):
    return login_required(user_passes_test(lambda u: profile_role(u) in ("employee", "admin"), login_url="employee_login")(view))
def admin_required(view):
    return login_required(user_passes_test(lambda u: profile_role(u) == "admin", login_url="admin_login")(view))
def customer_required(view):
    return login_required(user_passes_test(lambda u: profile_role(u) == "customer", login_url="login")(view))

def notify_users(users, complaint, title, message):
    seen = set()
    for user in users:
        if user and user.is_active and user.pk not in seen:
            Notification.objects.create(recipient=user, complaint=complaint, title=title, message=message)
            seen.add(user.pk)

def administrators(): return User.objects.filter(Q(is_active=True) & (Q(is_staff=True) | Q(is_superuser=True))).distinct()
def employees_for_department(category):
    # All employee accounts are notified; department routing can be refined by mapping category to department.
    return User.objects.filter(is_active=True, mg_profile__role="employee")

@customer_required
def customer_dashboard(request):
    complaints = Complaint.objects.filter(customer=request.user).select_related("assigned_to").order_by("-created_at")[:8]
    return render(request, "portal/customer_dashboard.html", {"complaints": complaints, "open_count": Complaint.objects.filter(customer=request.user).exclude(status__in=["resolved", "closed"]).count(), "notifications": request.user.mg_notifications.filter(read_at__isnull=True)[:5]})

@customer_required
def raise_complaint(request):
    if request.method == "POST":
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False); complaint.customer = request.user; complaint.save()
            TicketActivity.objects.create(complaint=complaint, actor=request.user, action="Request raised", note=complaint.description)
            recipients = list(administrators()) + list(employees_for_department(complaint.category))
            notify_users(recipients, complaint, f"New ticket #{complaint.pk}", f"{request.user.get_username()} raised: {complaint.get_category_display()}. Please review and assign.")
            messages.success(request, f"Your request was submitted. Ticket number: #{complaint.pk}. Admin and employee teams have been notified.")
            return redirect("my_complaints")
    else: form = ComplaintForm()
    return render(request, "portal/complaint_form.html", {"form": form})

@customer_required
def my_complaints(request):
    return render(request, "portal/my_complaints.html", {"complaints": Complaint.objects.filter(customer=request.user).select_related("assigned_to").order_by("-created_at")})

@customer_required
def plans(request):
    return render(request, "portal/plans.html", {"plans": Plan.objects.filter(active=True).order_by("price_inr"), "callback_form": CallbackRequestForm()})

@customer_required
@require_POST
def request_callback(request, plan_id):
    plan = get_object_or_404(Plan, pk=plan_id, active=True); form = CallbackRequestForm(request.POST)
    if form.is_valid():
        callback = form.save(commit=False); callback.customer = request.user; callback.plan = plan; callback.save()
        notify_users(administrators(), None, f"Plan callback request #{callback.pk}", f"{request.user.get_username()} requested a callback about {plan.name} ({callback.mobile_number}).")
        messages.success(request, "Callback request submitted. Our team has been notified.")
    else: messages.error(request, "Please enter a valid mobile number.")
    return redirect("plans")

@employee_required
def employee_dashboard(request):
    tickets = Complaint.objects.select_related("customer", "assigned_to").order_by("created_at")
    if profile_role(request.user) != "admin": tickets = tickets.filter(Q(assigned_to=request.user) | Q(assigned_to__isnull=True))
    return render(request, "portal/employee_dashboard.html", {"tickets": tickets, "pending_count": tickets.exclude(status__in=["resolved", "closed"]).count(), "notifications": request.user.mg_notifications.filter(read_at__isnull=True)[:10]})

@employee_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Complaint.objects.select_related("customer", "assigned_to"), pk=ticket_id)
    if profile_role(request.user) != "admin" and ticket.assigned_to not in (None, request.user):
        messages.error(request, "This ticket is assigned to another employee."); return redirect("employee_dashboard")
    # Opening a ticket claims it if unassigned and creates an auditable event.
    if request.method == "GET" and profile_role(request.user) == "employee":
        first_access = ticket.accessed_at is None
        if ticket.assigned_to_id is None: ticket.assigned_to = request.user
        ticket.accessed_at = timezone.now()
        if ticket.status == "open": ticket.status = "assigned"
        ticket.save(update_fields=["assigned_to", "accessed_at", "status", "updated_at"])
        TicketActivity.objects.create(complaint=ticket, actor=request.user, action="Employee accessed request")
        if first_access:
            notify_users([ticket.customer], ticket, f"Ticket #{ticket.pk} accessed", f"{request.user.get_full_name() or request.user.get_username()} has accessed your request and is reviewing it.")
            notify_users(administrators(), ticket, f"Employee accessed ticket #{ticket.pk}", f"{request.user.get_username()} accessed the request from {ticket.customer.get_username()}.")
    if request.method == "POST":
        status = request.POST.get("status", ticket.status)
        valid_statuses = dict(Complaint.STATUSES)
        if status not in valid_statuses: status = ticket.status
        old_status = ticket.status; ticket.status = status
        if profile_role(request.user) == "admin" and request.POST.get("assigned_to"):
            assignee = get_object_or_404(User, pk=request.POST["assigned_to"], is_active=True)
            ticket.assigned_to = assignee
            notify_users([assignee], ticket, f"Ticket #{ticket.pk} assigned to you", f"Admin assigned ticket #{ticket.pk}: {ticket.get_category_display()}.")
            notify_users([ticket.customer], ticket, f"Employee assigned to ticket #{ticket.pk}", f"Your request has been assigned to {assignee.get_full_name() or assignee.get_username()}.")
        ticket.save()
        note = request.POST.get("note", "").strip()
        TicketActivity.objects.create(complaint=ticket, actor=request.user, action=f"Status changed: {old_status} → {ticket.status}", note=note)
        notify_users([ticket.customer], ticket, f"Ticket #{ticket.pk} updated", f"Your request status is now: {ticket.get_status_display()}." + (f" Update: {note}" if note else ""))
        notify_users(administrators(), ticket, f"Ticket #{ticket.pk} updated", f"{request.user.get_username()} changed ticket status to {ticket.get_status_display()}.")
        messages.success(request, "Ticket updated and notifications sent.")
        return redirect("ticket_detail", ticket_id=ticket.pk)
    return render(request, "portal/ticket_detail.html", {"ticket": ticket, "employees": User.objects.filter(is_active=True, mg_profile__role="employee").order_by("username"), "activities": ticket.activities.select_related("actor")})

@admin_required
def admin_dashboard(request):
    tickets = Complaint.objects.select_related("customer", "assigned_to").order_by("-created_at")
    return render(request, "portal/admin_dashboard.html", {"tickets": tickets, "total": tickets.count(), "open_count": tickets.exclude(status__in=["resolved", "closed"]).count(), "employees": User.objects.filter(mg_profile__role="employee").count(), "customers": User.objects.filter(mg_profile__role="customer").count(), "notifications": Notification.objects.select_related("recipient", "complaint").order_by("-created_at")[:25]})

@login_required
def notifications(request):
    items = request.user.mg_notifications.select_related("complaint").all()[:100]
    if request.method == "POST":
        request.user.mg_notifications.filter(read_at__isnull=True).update(read_at=timezone.now())
        return redirect("notifications")
    return render(request, "portal/notifications.html", {"items": items})

def logout_view(request):
    logout(request); return redirect("login")

# Local development OTP only: a real SMS gateway must be configured before launch.
def otp_request(request):
    if request.method == "POST":
        mobile = request.POST.get("mobile", "").strip()
        if not mobile: messages.error(request, "Enter your registered mobile number.")
        else:
            code = f"{random.randint(0, 999999):06d}"; request.session["demo_otp"] = code; request.session["demo_otp_mobile"] = mobile
            print(f"[MG FIBERNET DEMO OTP] {mobile}: {code}")
            messages.info(request, "Demo OTP generated in the Django terminal. Configure an SMS gateway for production."); return redirect("otp_verify")
    return render(request, "portal/otp_request.html")
def otp_verify(request):
    if request.method == "POST":
        code = request.POST.get("otp", "").strip()
        if code and code == request.session.get("demo_otp"):
            mobile = request.session.get("demo_otp_mobile"); profile = CustomerProfile.objects.filter(mobile_number=mobile).select_related("user").first()
            user = profile.user if profile else User.objects.filter(username=mobile).first()
            if user and user.is_active:
                login(request, user, backend="django.contrib.auth.backends.ModelBackend"); request.session.pop("demo_otp", None); request.session.pop("demo_otp_mobile", None); return redirect("customer_dashboard")
            messages.error(request, "This mobile number is not linked to an account. Ask support to register it.")
        else: messages.error(request, "Incorrect OTP. Please try again.")
    return render(request, "portal/otp_verify.html")
