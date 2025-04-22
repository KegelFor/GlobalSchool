from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import Course, User, Complaint, ComplaintMessage, Review


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'price', 'teacher', 'category']
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["text"]
class VerifyEmailForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        label="Введите код подтверждения",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '6-значный код'}),
    )
class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Подтвердите пароль")

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'avatar', 'role']
class LoginForm(AuthenticationForm):
    pass



class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['course']

class ComplaintMessageForm(forms.ModelForm):
    class Meta:
        model = ComplaintMessage
        fields = ['text']