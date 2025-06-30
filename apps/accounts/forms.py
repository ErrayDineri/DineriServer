from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        
        # Add Bootstrap classes and placeholders
        for fieldname in ['username', 'email', 'password1', 'password2']:
            self.fields[fieldname].widget.attrs['class'] = 'form-control'
            self.fields[fieldname].widget.attrs['placeholder'] = self.fields[fieldname].label


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        
        # Add Bootstrap classes and placeholders
        for fieldname in ['username', 'password']:
            self.fields[fieldname].widget.attrs['class'] = 'form-control'
            self.fields[fieldname].widget.attrs['placeholder'] = self.fields[fieldname].label
