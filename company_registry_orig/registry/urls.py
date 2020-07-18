from django.urls import path

from . import views

urlpatterns = [
    path('add-company/', views.AddCompanyView.as_view(), name='registry-add-company'),
]
