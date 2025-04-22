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
from django.views.generic import ListView, DetailView
from main.forms import CourseForm
from main.models import Course, User, SignToCourse, Review, Enrollment
logger = logging.getLogger(__name__)

class CourseListView(ListView):
    model = Course
    template_name = 'main/courses.html'
    context_object_name = 'courses'
    paginate_by = 6
    def get_queryset(self):
        queryset = super().get_queryset()
        teacher_id = self.request.GET.get("teacher")
        if teacher_id:
            queryset = queryset.filter(teacher_id=teacher_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["teachers"] = User.objects.filter(course__isnull=False).distinct()
        context["selected_teacher"] = self.request.GET.get("teacher", "")
        return context
def create_course(request):
    if not request.user.is_superuser:
        return redirect('home')
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = CourseForm()
    return render(request, 'main/create_course.html', {'form': form})


class CourseDetailView(DetailView):
    model = Course
    template_name = 'main/course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        course = self.object

        sign_to_course = SignToCourse.objects.filter(user=user, course=course).first()
        enrollment = Enrollment.objects.filter(student=user, course=course).first()

        context['is_enrolled'] = sign_to_course is not None
        context['sign_to_course'] = sign_to_course
        context['enrollment'] = enrollment
        context['reviews'] = Review.objects.filter(course=course)
        context['is_admin'] = user.is_superuser

        return context






class CourseDeleteView(View):
    def post(self, request, course_id):
        if not request.user.is_superuser:
            return redirect("courses_list")

        course = get_object_or_404(Course, id=course_id)
        course.delete()
        return redirect("courses_list")


