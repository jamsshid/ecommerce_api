import django_filters

from .models import Product


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    category = django_filters.CharFilter(field_name="category__slug")
    search = django_filters.CharFilter(method="filter_search")
    in_stock = django_filters.BooleanFilter(method="filter_in_stock")

    class Meta:
        model = Product
        fields = [
            "category",
            "is_featured",
            "min_price",
            "max_price",
            "search",
            "in_stock",
        ]

    def filter_search(self, queryset, name, value):
        return queryset.filter(name__icontains=value) | queryset.filter(
            description__icontains=value
        )

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(inventory__quantity__gt=0)
        return queryset
