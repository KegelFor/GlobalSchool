import logging
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
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



class ComplaintCreateView(LoginRequiredMixin, CreateView):
    model = Complaint
    form_class = ComplaintForm
    template_name = 'main/complaint_form.html'

    def form_valid(self, form):
        if self.request.user.role != 'student':
            return JsonResponse({'error': 'Только ученики могут подать жалобу'}, status=403)

        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('complaint_list')


class ComplaintMessageCreateView(LoginRequiredMixin, CreateView):
    model = ComplaintMessage
    form_class = ComplaintMessageForm
    template_name = 'message_form.html'

    def form_valid(self, form):
        complaint = get_object_or_404(Complaint, id=self.kwargs['complaint_id'])

        if self.request.user != complaint.user and not self.request.user.is_staff:
            return JsonResponse({'error': 'Нет доступа'}, status=403)

        form.instance.complaint = complaint
        form.instance.sender = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('complaint_detail', kwargs={'pk': self.kwargs['complaint_id']})



class ComplaintListView(LoginRequiredMixin, ListView):
    model = Complaint
    template_name = 'complaint_list.html'
    context_object_name = 'complaints'

    def get_queryset(self):
        return Complaint.objects.filter(user=self.request.user)


class ComplaintDetailView(LoginRequiredMixin, View):
    template_name = 'main/complaint_detail.html'

    def get(self, request, pk):
        complaint = get_object_or_404(Complaint, pk=pk)
        chat_messages = complaint.messages.all()
        return render(request, self.template_name, {'complaint': complaint, 'chat_messages': chat_messages})

    def post(self, request, pk):
        complaint = get_object_or_404(Complaint, pk=pk)

        if 'text' in request.POST:
            ComplaintMessage.objects.create(
                complaint=complaint,
                sender=request.user,
                text=request.POST['text']
            )
            return redirect('complaint_detail', pk=pk)

        if 'close_complaint' in request.POST:
            complaint.is_closed = True
            complaint.save()
            return redirect('complaint_detail', pk=pk)

        return redirect('complaint_detail', pk=pk)

class SendMessageView(View):
    def post(self, request, complaint_id):
        complaint = get_object_or_404(Complaint, id=complaint_id)

        if request.user != complaint.user and not request.user.is_staff:
            return JsonResponse({'error': 'Нет доступа'}, status=403)

        form = ComplaintMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.complaint = complaint
            message.sender = request.user
            message.save()
            return HttpResponseRedirect(reverse('complaint_detail', args=[complaint_id]))

        return JsonResponse({'error': 'Неверные данные'}, status=400)


class CloseComplaintView(View):
    def post(self, request, complaint_id):
        complaint = get_object_or_404(Complaint, id=complaint_id)

        if request.user != complaint.user and not request.user.is_staff:
            return JsonResponse({'error': 'Нет доступа'}, status=403)

        complaint.is_closed = True
        complaint.save()
        return HttpResponseRedirect(reverse('complaint_detail', args=[complaint_id]))



class AdminComplaintListView(AdminOnlyMixin, ListView):
    model = Complaint
    template_name = 'admin_complaint_list.html'
    context_object_name = 'complaints'

class AdminComplaintDetailView(AdminOnlyMixin, DetailView):
    model = Complaint
    template_name = 'admin_complaint_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chat_messages'] = self.object.messages.all()
        context['form'] = ComplaintMessageForm()
        return context

class AdminSendMessageView(AdminOnlyMixin, View):
    def post(self, request, pk):
        complaint = get_object_or_404(Complaint, pk=pk)
        form = ComplaintMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.complaint = complaint
            message.sender = request.user
            message.save()
        return redirect('admin_complaint_detail', pk=pk)

class AdminCloseComplaintView(AdminOnlyMixin, View):
    def post(self, request, pk):
        complaint = get_object_or_404(Complaint, pk=pk)
        complaint.is_closed = True
        complaint.save()
        return redirect('admin_complaint_detail', pk=pk)

