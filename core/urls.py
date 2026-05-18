from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("media/", include("apps.common.urls", namespace="common")),

    path("users/", include("apps.users.urls", namespace="users")),
    path("cart/", include("apps.cart.urls", namespace="cart")),

    path("api/v1/users/", include("apps.users.api_urls", namespace="users_api")),
    path(
        "api/v1/products/", include("apps.products.api_urls", namespace="products_api")
    ),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("", include("apps.products.urls", namespace="products")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.BASE_DIR / "static"
    )
