from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'users/author.html'


class AboutTechView(TemplateView):
    template_name = 'users/tech.html'
