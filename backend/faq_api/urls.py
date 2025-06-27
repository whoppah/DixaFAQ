#backend/faq_api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from django.contrib.auth import views as auth_views

router = DefaultRouter()
router.register(r"messages", views.MessageViewSet, basename="message")
router.register(r"faqs", views.FAQViewSet, basename="faq")
router.register(r"cluster-runs", views.ClusterRunViewSet, basename="clusterrun")
router.register(r"cluster-results", views.ClusterResultViewSet, basename="clusterresult")

urlpatterns = [
    path("", include(router.urls)),
    path("clusters/", views.cluster_results),
    path("dashboard-clusters-with-messages/", views.dashboard_clusters_with_messages),
    path("trending-leaderboard/", views.trending_questions_leaderboard),  
    path("deflection-metrics/", views.faq_performance_trends),
    path("top-process-gaps/", views.top_process_gaps),
    path("trigger-pipeline/", views.trigger_pipeline),
    path("current-user-info/", views.current_user_info),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
]
