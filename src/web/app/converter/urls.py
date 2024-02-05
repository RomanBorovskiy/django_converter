from django.urls import path

from . import views

app_name = "converter"
urlpatterns = [
    path("", views.Files.as_view(), name="index"),
    path("delete/<int:pk>/", views.DeleteFile.as_view(), name="delete"),
]
