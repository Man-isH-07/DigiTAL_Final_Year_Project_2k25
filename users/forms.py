from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

# Regular User Creation Form
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customizing the help_text for fields
        self.fields['username'].help_text = 'Your username must be unique with letters, numbers, and @/./+/-/_'
        self.fields['email'].help_text = 'Enter a valid email address, used for account recovery and notifications.'
        self.fields['password1'].help_text = 'Password should be at least 8 characters long with letters and numbers.'
        self.fields['password2'].help_text =None



    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'user'  # Force role to 'user' for self-registration
        if commit:
            user.save()
        return user
