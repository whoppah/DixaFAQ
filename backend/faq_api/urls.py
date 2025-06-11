#backend/faq_api/urls.py
from django.urls import path
from .views import cluster_results
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('clusters/', cluster_results),
    path("api/trigger-pipeline/", views.trigger_pipeline),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
]
