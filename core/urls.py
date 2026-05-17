from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Template URLs
    path("users/", include("apps.users.urls", namespace="users")),
    # API URLs
    path("api/v1/users/", include("apps.users.api_urls", namespace="users_api")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.BASE_DIR / "static"
    )
