from django.urls import path

from . import views

app_name = 'pages'

urlpatterns = [
    path('about/', views.AboutView.as_view(template_name='pages/about.html'), name='about'),
    path('rules/', views.RulesView.as_view(template_name='pages/rules.html'), name='rules'),
]
