import logging
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.contrib.messages import Message
from django.core.mail import send_mail
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, DetailView, FormView, TemplateView, UpdateView, CreateView, DeleteView
from main.forms import CourseForm, RegisterForm, VerifyEmailForm, LoginForm, ComplaintForm, ComplaintMessageForm, \
    ReviewForm
from main.mixins import AdminOnlyMixin
from main.models import Course, User, EmailVerificationCode, SignToCourse, Review, Complaint, ComplaintMessage, \
    CenterReview
from main.utils import generate_verification_code
logger = logging.getLogger(__name__)


class RegisterView(FormView):
    template_name = 'main/register.html'
    form_class = RegisterForm

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.avatar = form.cleaned_data['avatar']
        user.role = form.cleaned_data['role']

        user.set_password(form.cleaned_data['password'])
        user.save()

        code = generate_verification_code()
        EmailVerificationCode.objects.create(user=user, code=code)

        send_mail(
            'Код подтверждения',
            f'Ваш код: {code}',
            'bigworldgoodji@gmail.com',
            [user.email]
        )

        return redirect('verify_email', user_id=user.id)



class VerifyEmailView(View):
    template_name = 'main/verify_email.html'

    def get(self, request, user_id):
        form = VerifyEmailForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, user_id):
        form = VerifyEmailForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            user = get_object_or_404(User, id=user_id)
            verification = EmailVerificationCode.objects.filter(user=user, code=code).first()

            if verification:
                user.is_active = True
                user.save()
                login(request, user)
                return redirect('home')

        return render(request, self.template_name, {'form': form, 'error': 'Неверный код'})


class LoginUserView(LoginView):
    template_name = 'main/login.html'
    authentication_form = LoginForm

    def form_valid(self, form):
        user = form.get_user()
        logger.info(f"Попытка входа: {user.username} (Активен: {user.is_active})")

        if user.is_active:
            login(self.request, user)
            return redirect('home')
        return self.form_invalid(form)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('home')


class ChangePasswordView(LoginRequiredMixin, FormView):
    template_name = 'main/change_password.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('profile')

    def get_form(self, form_class=None):
        return self.form_class(self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)
        return super().form_valid(form)

class ForgotPasswordView(View):
    template_name = 'main/forgot_password.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()

        if not user:
            return render(request, self.template_name, {'error': 'Пользователь с таким email не найден'})

        code = generate_verification_code()
        EmailVerificationCode.objects.create(user=user, code=code)

        send_mail(
            'Код для восстановления пароля',
            f'Ваш код: {code}',
            'bigworldgoodji@gmail.com',
            [email]
        )

        return redirect('verify_reset_code', user_id=user.id)


class VerifyResetCodeView(View):
    template_name = 'main/verify_reset_code.html'

    def get(self, request, user_id):
        return render(request, self.template_name, {'user_id': user_id})

    def post(self, request, user_id):
        code = request.POST.get('code')
        user = get_object_or_404(User, id=user_id)
        verification = EmailVerificationCode.objects.filter(user=user, code=code).first()

        if verification:
            return HttpResponseRedirect(f'/profile/reset-password/{user_id}/new/')
        return render(request, self.template_name, {'error': 'Неверный код', 'user_id': user_id})

class NewPasswordView(View):
    template_name = 'main/new_password.html'

    def get(self, request, user_id):
        return render(request, self.template_name, {'user_id': user_id})

    def post(self, request, user_id):
        password = request.POST.get('password')
        user = get_object_or_404(User, id=user_id)
        user.set_password(password)
        user.save()
        return redirect('login')