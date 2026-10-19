from django.contrib import admin
from .models import CustomerProfile, Complaint, Plan, CallbackRequest, UserProfile, Notification, TicketActivity

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "category", "status", "assigned_to", "created_at", "accessed_at")
    list_filter = ("status", "category", "created_at")
    search_fields = ("customer__username", "description", "assigned_to__username")
    readonly_fields = ("created_at", "updated_at", "accessed_at")

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "department", "mobile_number")
    list_filter = ("role", "department")
    search_fields = ("user__username", "mobile_number")

admin.site.register(CustomerProfile)
admin.site.register(Plan)
admin.site.register(CallbackRequest)
admin.site.register(Notification)
admin.site.register(TicketActivity)
