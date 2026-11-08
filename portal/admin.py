from django.contrib import admin
from .models import Complaint, Plan, CallbackRequest, UserProfile, Notification, TicketActivity

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "category", "status", "assigned_to", "created_at", "accessed_at")
    list_filter = ("status", "category", "created_at")
    search_fields = ("customer__username", "description", "assigned_to__username")
    readonly_fields = ("created_at", "updated_at", "accessed_at")

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "customer_id", "department", "mobile_number")
    list_filter = ("role", "department")
    search_fields = ("user__username", "customer_id", "mobile_number")
    readonly_fields = ("created_at", "updated_at")
    exclude = ("customer_id",)
    
    def save_model(self, request, obj, form, change):
        if not change and obj.role == "customer" and not obj.customer_id:
            # Auto-generate customer_id for new customers
            base_id = f"MG-{obj.user.username}"
            count = UserProfile.objects.filter(customer_id__startswith=base_id).count()
            obj.customer_id = f"{base_id}-{str(count + 1).zfill(3)}"
        super().save_model(request, obj, form, change)

admin.site.register(Plan)
admin.site.register(CallbackRequest)
admin.site.register(Notification)
admin.site.register(TicketActivity)
