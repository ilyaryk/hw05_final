from django.views.generic import CreateView
from django.views.generic.base import TemplateView
from django.urls import reverse_lazy
from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class AuthorPage(TemplateView):
    template_name = 'users/author.html'


class TechPage(TemplateView):
    template_name = 'users/tech.html'


class PasswordChange(TemplateView):
    template_name = 'users/password_change_form.html'


class PasswordReset(TemplateView):
    template_name = 'users/password_reset_form.html'
