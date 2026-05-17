from django.urls import path

from . import views

app_name = "products_api"

urlpatterns = [
    path("categories/", views.CategoryListAPIView.as_view(), name="category-list"),
    path(
        "categories/<slug:slug>/",
        views.CategoryDetailAPIView.as_view(),
        name="category-detail",
    ),
    path("", views.ProductListAPIView.as_view(), name="list"),
    path("<slug:slug>/", views.ProductDetailAPIView.as_view(), name="detail"),
]
