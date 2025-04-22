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



class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'main/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        masked_email = "****" + user.email[4:]
        context.update({
            'user': user,
            'masked_email': masked_email,
        })
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['username', 'email', 'avatar']
    template_name = 'main/edit_profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user