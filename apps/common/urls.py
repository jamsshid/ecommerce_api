from django.urls import re_path

from . import views

app_name = "common"

urlpatterns = [
    # Matches any path: /media/avatars/foo.jpg, /media/products/bar.png, etc.
    re_path(r"^(?P<name>.+)$", views.serve_file, name="serve_file"),
]
