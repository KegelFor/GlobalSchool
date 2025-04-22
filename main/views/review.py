import logging
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView

from main.models import Course,  Review, \
    CenterReview
logger = logging.getLogger(__name__)



class AddReviewView(CreateView):
    model = Review
    fields = ['text']

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.course = get_object_or_404(Course, id=self.kwargs['course_id'])
        messages.success(self.request, "Ваш отзыв добавлен!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('course_detail', kwargs={'pk': self.kwargs['course_id']})



class SchoolReviewListCreateView(CreateView, ListView):
    model = CenterReview
    template_name = "main/center_reviews.html"
    fields = ["text"]
    success_url = reverse_lazy("school_reviews")
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class SchoolReviewDeleteView(LoginRequiredMixin, DeleteView):
    model = CenterReview
    success_url = reverse_lazy("school_reviews")

    def post(self, request, *args, **kwargs):
        review = self.get_object()
        if review.user == request.user:
            review.delete()
        return redirect(self.success_url)