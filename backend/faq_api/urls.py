from django.urls import path
from .views import cluster_results

urlpatterns = [
    path('clusters/', cluster_results),
]
