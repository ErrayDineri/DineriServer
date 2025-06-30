from django.shortcuts import redirect
from django.contrib import messages

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the path
        path = request.path_info.lstrip('/')
        
        # Check if the path is for password manager and user is not authenticated
        if path.startswith('passwords/') and not request.user.is_authenticated:
            messages.warning(request, "You need to log in to access the Password Manager.")
            return redirect('login')
            
        response = self.get_response(request)
        return response
