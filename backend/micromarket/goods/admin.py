from django.contrib import admin

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

    def products_in_category(self, obj):
        return obj.products.count()

    products_in_category.admin_order_field = 'products_in_category'
    products_in_category.short_description = 'Количество продуктов в категории'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'name', 'categories', 'price', 'is_public', 'is_archive',
    )
    list_editable = ('name', 'price', 'is_public', 'is_archive',)
    search_fields = ('name', 'categories__category__name',)
    list_filter = ('categories__category',)
    inlines = (CategoryInline,)

    def categories(self, obj):
        return obj.categories.count()

    categories.admin_order_field = 'categories'
    categories.short_description = 'Количество категорий'


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'product', 'category',)
    search_fields = ('product__name', 'category__name',)
