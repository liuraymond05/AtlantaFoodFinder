from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, label='Username')
    password = forms.CharField(widget=forms.PasswordInput)

class CustomUserForm(UserCreationForm):
    email = forms.EmailField(max_length=100, help_text='Enter a valid email address.', required=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')