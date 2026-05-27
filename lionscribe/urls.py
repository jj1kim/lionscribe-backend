from django.urls import path

from .views import (
    SignupView,
    LoginView,
    MeView,
    JobView,
    JobDetailView,
    ChaosRestartView,
)

urlpatterns = [
    path('auth/signup/', SignupView.as_view()),
    path('auth/login/', LoginView.as_view()),
    path('users/me/', MeView.as_view()),
    path('jobs/', JobView.as_view()),
    path('jobs/<int:pk>/', JobDetailView.as_view()),
    path('_chaos/restart/', ChaosRestartView.as_view()),
]
