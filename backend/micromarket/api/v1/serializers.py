from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from goods.models import Category, Product, ProductCategory


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор данных о категории."""

    class Meta:
        model = Category
        fields = '__all__'


class ProductCategoryReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения категорий продукта."""

    id = serializers.IntegerField(source="category.id")
    name = serializers.CharField(source="category.name")

    class Meta:
        model = ProductCategory
        fields = ('id', 'name',)


class ProductReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения данных о товаре."""

    categories = ProductCategoryReadSerializer(many=True)

    class Meta:
        model = Product
        exclude = ('product_categories',)


class ProductCategoryWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи категорий продукта."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all()
    )

    class Meta:
        model = ProductCategory
        fields = ('id',)


class ProductWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи данных о товаре."""

    categories = ProductCategoryWriteSerializer(many=True)

    def validate_product_categories(self, value):
        if not (2 < len(value) < 10):
            raise serializers.ValidationError(
                'Количество категорий может быть в диапазоне от 2 до 10'
            )
        categories_set = set(value)
        if len(categories_set) != len(value):
            raise serializers.ValidationError(
                'Дублирование категорий не допускается'
            )
        return value

    def _add_product_to_categories(self, categories, product):
        for category in categories:
            ProductCategory.objects.create(
                product=product,
                category=category['id'],
            )

    def create(self, validated_data):
        categories = validated_data.pop('categories')
        product = Product.objects.create(**validated_data)
        self._add_product_to_categories(categories, product)
        return product

    def update(self, instance, validated_data):
        if 'categories' in validated_data:
            categories = validated_data.pop('categories')
            instance.product_categories.clear()
            self._add_product_to_categories(categories, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return ProductReadSerializer(instance, context=self.context).data

    class Meta:
        model = Product
        fields = '__all__'
