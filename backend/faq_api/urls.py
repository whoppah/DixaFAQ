#backend/faq_api/urls.py
from django.urls import path
from .views import cluster_results

urlpatterns = [
    path('clusters/', cluster_results),
    path("api/trigger-pipeline/", views.trigger_pipeline),
]
