from django.urls import re_path

from . import views

app_name = "common"

urlpatterns = [
    re_path(r"^(?P<name>.+)$", views.serve_file, name="serve_file"),
]
