from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from .models import Complaint, CallbackRequest, UserProfile

User = get_user_model()

class UserCreationForm(forms.ModelForm):
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={"placeholder": "Enter password"}), required=True)
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(attrs={"placeholder": "Confirm password"}), required=True)
    
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Username"}),
            "first_name": forms.TextInput(attrs={"placeholder": "First name"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last name"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email (optional)"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = False
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken")
        return username
    
    def clean_password(self):
        password = self.cleaned_data.get("password")
        if len(password) < 6:
            raise forms.ValidationError("Password must be at least 6 characters long")
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

class UserProfileCreationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].required = True
        self.fields['mobile_number'].required = True
        # Customer-specific fields
        self.fields['service_address'].required = False
        # Employee-specific fields
        self.fields['department'].required = False
    
    class Meta:
        model = UserProfile
        fields = ["role", "service_address", "department", "mobile_number"]
        widgets = {
            "role": forms.Select(attrs={"class": "form-control"}),
            "service_address": forms.Textarea(attrs={"rows": 3, "placeholder": "Service address"}),
            "department": forms.Select(attrs={"class": "form-control"}),
            "mobile_number": forms.TextInput(attrs={"placeholder": "Mobile number"}),
        }
    
    def clean_mobile_number(self):
        mobile = self.cleaned_data.get('mobile_number')
        if not mobile or len(mobile) < 10:
            raise forms.ValidationError("Please enter a valid mobile number (at least 10 digits)")
        return mobile

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
