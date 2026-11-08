from django.conf import settings
from django.db import models

class UserProfile(models.Model):
    """Consolidated user profile for both customers and employees."""
    ROLES = [("customer", "Customer"), ("employee", "Employee")]
    DEPARTMENTS = [
        ("complaints", "Complaints"), ("new_connection", "New connection"),
        ("dish", "Dish complaints"), ("main_line", "Main line complaints"),
        ("airtel_fiber", "Airtel fiber cuts"), ("renewal", "Renewal / billing"),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLES, default="customer")
    
    # Customer-specific fields
    customer_id = models.CharField(max_length=40, unique=True, null=True, blank=True, help_text="Unique customer ID for customers")
    service_address = models.TextField(blank=True, help_text="Service address for customers")
    
    # Employee-specific fields
    department = models.CharField(max_length=30, choices=DEPARTMENTS, blank=True, help_text="Department for employees")
    
    # Common fields
    mobile_number = models.CharField(max_length=20, blank=True, help_text="Mobile number for contact")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
    
    def __str__(self):
        if self.role == "customer":
            return f"{self.customer_id or self.user.username} (Customer)"
        return f"{self.user.username} ({self.role} - {self.department or 'No Dept'})"

class Complaint(models.Model):
    CATEGORIES = [
        ("fiber_cut", "Red light / fiber cut"), ("speed", "Speed issues"),
        ("website", "Website not working"), ("no_internet", "No red light but no internet"),
        ("renewal", "Renewal issues"), ("dish_ott", "Dish TV / OTT issues"),
        ("new_connection", "New connection request"), ("shifting", "Shifting existing connection"),
        ("other", "Other issue / other concern"),
    ]
    STATUSES = [("open", "Open"), ("assigned", "Assigned"), ("in_progress", "In progress"), ("resolved", "Resolved"), ("closed", "Closed")]
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="complaints")
    category = models.CharField(max_length=30, choices=CATEGORIES)
    description = models.TextField()
    location_text = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    photo = models.ImageField(upload_to="complaint_photos/%Y/%m/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUSES, default="open")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_complaints")
    accessed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return f"Ticket #{self.pk} - {self.get_category_display()}"

class Plan(models.Model):
    name = models.CharField(max_length=100)
    speed = models.CharField(max_length=60)
    price_inr = models.DecimalField(max_digits=8, decimal_places=2)
    validity_days = models.PositiveIntegerField(default=30)
    description = models.CharField(max_length=250, blank=True)
    renewal_url = models.URLField(blank=True, help_text="Optional URL to the existing renewal portal")
    active = models.BooleanField(default=True)
    def __str__(self): return f"{self.name} - ₹{self.price_inr}"

class CallbackRequest(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="callback_requests")
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    mobile_number = models.CharField(max_length=20)
    note = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    contacted = models.BooleanField(default=False)
    def __str__(self): return f"Callback #{self.pk} - {self.mobile_number}"


class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications")
    title = models.CharField(max_length=160)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
    def __str__(self): return f"{self.recipient}: {self.title}"


class TicketActivity(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name="activities")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Ticket Activity"
        verbose_name_plural = "Ticket Activities"
    def __str__(self): return f"Ticket #{self.complaint_id}: {self.action}"
