import logging
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView

from main.models import Course, SignToCourse, Enrollment
logger = logging.getLogger(__name__)



class SignCourseView(CreateView):
    model = SignToCourse
    fields = []
    success_url = reverse_lazy('courses_list')

    def form_valid(self, form):
        user = self.request.user
        course = get_object_or_404(Course, id=self.kwargs['course_id'])

        if user.role != "student":
            messages.error(self.request, "Только студенты могут записываться на курсы.")
            return redirect('course_detail', pk=course.id)

        if SignToCourse.objects.filter(user=user, course=course).exists():
            messages.warning(self.request, "Вы уже записаны на этот курс!")
            return redirect('course_detail', pk=course.id)

        form.instance.user = user
        form.instance.course = course
        response = super().form_valid(form)

        enrollment, created = Enrollment.objects.get_or_create(student=user, course=course)

        if not created:
            enrollment.is_paid = False
            enrollment.payment_amount = 0
            enrollment.save()

        messages.success(self.request, "Вы успешно записались на курс! Оплата требуется заново.")
        return response



class UnsignCourseView(DeleteView):
    model = SignToCourse
    success_url = reverse_lazy('courses_list')

    def get_object(self, queryset=None):
        user = self.request.user
        course = get_object_or_404(Course, id=self.kwargs['course_id'])
        return get_object_or_404(SignToCourse, user=user, course=course)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        enrollment = Enrollment.objects.filter(student=request.user, course=obj.course).first()

        if enrollment and enrollment.is_paid:
            messages.warning(request, "Если вы отмените курс, заплаченные деньги не вернутся!")
            return redirect('confirm_unsign', course_id=obj.course.id)

        obj.delete()
        if enrollment:
            enrollment.delete()

        messages.success(request, "Вы отменили запись на курс!")
        return redirect('course_detail', pk=self.kwargs['course_id'])





class PayForCourseView(LoginRequiredMixin, View):
    template_name = "main/payment.html"

    def get(self, request, enrollment_id):
        enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=request.user)
        return render(request, self.template_name, {"enrollment": enrollment})

    def post(self, request, enrollment_id):
        enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=request.user)
        amount = request.POST.get("amount")

        if amount and float(amount) == float(enrollment.course.price):
            enrollment.is_paid = True
            enrollment.payment_amount = amount
            enrollment.save()
            return redirect("course_detail", pk=enrollment.course.id)

        return redirect("payment_error", enrollment_id=enrollment.id)


def payment_error_view(request, enrollment_id):
    return render(request, "main/payment_error.html", {"enrollment_id": enrollment_id})


def confirm_unsign_view(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(request, "main/confirm_unsign.html", {"course_id": course_id, "course": course})