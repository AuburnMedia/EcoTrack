from django.urls import path

from apps.charts import views

urlpatterns = [
    path("", views.index, name="charts"),
    path("manage-goal/", views.manage_carbon_goal, name="manage_carbon_goal"),
]
