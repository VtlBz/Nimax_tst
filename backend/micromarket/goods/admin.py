from django.contrib import admin
from django.db.models import Count

from .models import Category, Product, ProductCategory


class ProductInline(admin.TabularInline):
    model = ProductCategory
    min_num = 0
    extra = 0

    def get_queryset(self, request):
        queryset = super().get_queryset(request).prefetch_related('product')
        return queryset


class CategoryInline(admin.TabularInline):
    model = ProductCategory
    min_num = 2
    extra = 0

    def get_queryset(self, request):
        queryset = super().get_queryset(request).prefetch_related('category')
        return queryset


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'products_in_category',)
    list_editable = ('name',)
    search_fields = ('name', 'products__product__name',)
    inlines = (ProductInline,)

    def get_queryset(self, request):
        queryset = super().get_queryset(request).annotate(
            products_in_category=Count('products'),
        )
        return queryset

    def products_in_category(self, obj):
        return obj.products_in_category

    products_in_category.admin_order_field = 'products_in_category'
    products_in_category.short_description = 'Количество продуктов в категории'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'categories_of_product',
        'price',
        'is_public',
        'is_archive',
    )
    list_editable = ('name', 'price', 'is_public', 'is_archive',)
    search_fields = ('name', 'categories__category__name',)
    list_filter = ('categories__category',)
    inlines = (CategoryInline,)

    def get_queryset(self, request):
        queryset = super().get_queryset(request).annotate(
            categories_of_product=Count('categories'),
        )
        return queryset

    def categories_of_product(self, obj):
        return obj.categories_of_product

    categories_of_product.admin_order_field = 'categories_of_product'
    categories_of_product.short_description = 'Количество категорий'


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'product', 'category',)
    search_fields = ('product__name', 'category__name',)
