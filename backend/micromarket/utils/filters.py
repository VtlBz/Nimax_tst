from django_filters.rest_framework import (
    CharFilter, BooleanFilter, FilterSet, NumberFilter,
)

from goods.models import Product


class ProductFilter(FilterSet):
    name = CharFilter(lookup_expr='icontains')
    category_id = NumberFilter(
        field_name='categories__category__id'
    )
    category_name = CharFilter(
        field_name='categories__category__name',
        lookup_expr='icontains'
    )
    price_min = NumberFilter(field_name='price', lookup_expr='gte')
    price_max = NumberFilter(field_name='price', lookup_expr='lte')
    is_public = BooleanFilter(field_name='is_public')
    is_archive = BooleanFilter(field_name='is_archive')

    class Meta:
        model = Product
        fields = (
            'name',
            'categories__category__id',
            'categories__category__name',
            'price_min',
            'price_max',
            'is_public',
            'is_archive',
        )
