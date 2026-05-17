from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("media/", include("apps.common.urls", namespace="common")),
    # Move specific paths ABOVE the generic product paths
    path("users/", include("apps.users.urls", namespace="users")),
    path("cart/", include("apps.cart.urls", namespace="cart")),
    # API URLs
    path("api/v1/users/", include("apps.users.api_urls", namespace="users_api")),
    path(
        "api/v1/products/", include("apps.products.api_urls", namespace="products_api")
    ),
    path("", include("apps.products.urls", namespace="products")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.BASE_DIR / "static"
    )
