from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.conf import settings

User = get_user_model()

class CheckUsersExistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip check for admin URLs, static files, no-users page, and create-user page
        if request.path.startswith('/admin/') or request.path.startswith('/static/') or request.path == '/no-users/' or request.path == '/create-user/':
            return self.get_response(request)
        
        # Check if any users exist in the database
        has_users = User.objects.exists()
        
        if not has_users:
            return redirect('no_users')
        
        return self.get_response(request)
