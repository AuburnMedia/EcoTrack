from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("onboarding/", views.onboarding, name="onboarding"),
    path("profile/", views.profile, name="profile"),
    path("survey/", views.survey_dashboard, name="survey_dashboard"),
    path("survey/initial/", views.initial_survey, name="initial_survey"),
    path("survey/weekly/", views.weekly_checkup, name="weekly_checkup"),
]
