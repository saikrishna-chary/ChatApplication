'''
from django import forms
from django.contrib.auth import authenticate
from .models import CustomUser, ChatRoom, Message

class RegisterForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'age', 'contact', 'gender', 'email']

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6)

class PasswordSetForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password') != cleaned_data.get('confirm_password'):
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

from django.contrib.auth import authenticate

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError("Invalid email or password.")
        return self.cleaned_data


class ChatRoomForm(forms.ModelForm):
    class Meta:
        model = ChatRoom
        fields = ['name', 'room_type', 'members']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['members'].widget.attrs['size'] = 5

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'media']

'''



from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from .models import CustomUser, ChatRoom, Message
import re

class RegisterForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'age', 'contact', 'gender', 'email']

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is None or age < 18:
            raise ValidationError("You must be at least 18 years old to register.")
        return age

    def clean_contact(self):
        contact = self.cleaned_data.get('contact', '').strip()
        if not re.fullmatch(r'\d{10}', contact):
            raise ValidationError("Contact number must be exactly 10 digits.")
        if CustomUser.objects.filter(contact=contact).exists():
            raise ValidationError("This contact number is already registered.")
        return contact


class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6)


class PasswordSetForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        # Strong password check: min 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special char
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', password):
            raise ValidationError("Password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("Password must contain at least one special character.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get('password')
        confirm_pwd = cleaned_data.get('confirm_password')
        if pwd and confirm_pwd and pwd != confirm_pwd:
            raise ValidationError("Passwords do not match.")
        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError("Invalid email or password.")
        return self.cleaned_data


class ChatRoomForm(forms.ModelForm):
    class Meta:
        model = ChatRoom
        fields = ['name', 'room_type', 'members']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['members'].widget.attrs['size'] = 5


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'media']
