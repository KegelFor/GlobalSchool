from django.views.generic import ListView, TemplateView

from main.models import Course


class HomeView(ListView):
    model = Course
    template_name = 'main/home.html'
    context_object_name = 'courses'
    queryset = Course.objects.all()[:3]


class AboutView(TemplateView):
    template_name = 'main/about.html'

class ContactPageView(TemplateView):
    template_name = "main/contacts.html"