from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'home'

urlpatterns = [
    path('', views.index, name='index'),
    path(
        'robots.txt',
        TemplateView.as_view(
            template_name='home/robots.txt',
            content_type='text/plain',
        ),
        name='robots',
    ),
]
