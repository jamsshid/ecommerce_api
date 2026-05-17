from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Serve files from DB at /media/<path>
    path("media/", include("apps.common.urls", namespace="common")),
    # Template URLs
    path("", include("apps.products.urls", namespace="products")),
    path("users/", include("apps.users.urls", namespace="users")),
    # API URLs
    path("api/v1/users/", include("apps.users.api_urls", namespace="users_api")),
    path("api/v1/products/", include("apps.products.api_urls", namespace="products_api")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.BASE_DIR / "static"
    )
