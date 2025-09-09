from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from register.models import Comment


class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class DateInput(forms.DateInput):
    input_type = 'date'

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['full_name', 'currency', 'date_of_birth']
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Full Name"}),
            "date_of_birth": DateInput(attrs={"placeholder": "Date of Birth"})
        }