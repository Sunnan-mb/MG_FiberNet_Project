from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Complaint, CallbackRequest

class CustomerLoginForm(AuthenticationForm):
    username = forms.CharField(label="Customer ID / username", widget=forms.TextInput(attrs={"autocomplete": "username", "placeholder": "Enter your customer ID"}))
    password = forms.CharField(label="Password", strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "current-password", "placeholder": "Enter password"}))

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ["category", "description", "location_text", "photo"]
        widgets = {
            "category": forms.Select(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Describe the issue and best time to contact you"}),
            "location_text": forms.Textarea(attrs={"rows": 2, "placeholder": "Address / landmark (optional)"}),
            "photo": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }

class CallbackRequestForm(forms.ModelForm):
    class Meta:
        model = CallbackRequest
        fields = ["mobile_number", "note"]
        widgets = {"mobile_number": forms.TextInput(attrs={"placeholder": "Mobile number"}), "note": forms.TextInput(attrs={"placeholder": "Preferred time or question (optional)"})}
