from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from quiz.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # super ni to‘g‘ri chaqirish
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Enter your username',
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': 'Enter your email',
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Enter your password',
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm your password',
        })



class AvatarUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['avatar']