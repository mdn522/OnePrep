from django.urls import path

from .views import chart_view

app_name = 'charts'

urlpatterns = [
    path("user/charts/", chart_view, name="chart")
]
