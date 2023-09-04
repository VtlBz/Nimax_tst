from django.db import models


class Category(models.Model):
    """
    Модель категории товаров.
    """

    name = models.CharField(
        max_length=200,
        verbose_name='Название категории',
        help_text='Уникальное имя категории товаров',
        unique=True,
        db_index=True,
        error_messages={
            'unique': 'Такое название категории уже используется',
        },
    )

    class Meta:
        db_table = 'categories'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return f'{self.name}'


class Product(models.Model):
    """
    Модель товара.
    """

    name = models.CharField(
        max_length=200,
        verbose_name='Название товара',
        help_text='Уникальное название товара',
        unique=True,
        db_index=True,
        error_messages={
            'unique': 'Товар с таким названием уже существует',
        },
    )
    categories = models.ManyToManyField(
        Category, through='ProductCategory',
        verbose_name='Категории',
        help_text='Категории к которым отнисится товар',
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
        verbose_name='Цена товара',
        help_text='Цена за единицу товара',
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name='Опубликован',
        help_text='Отметка об опубликовании товара.',
    )
    is_archive = models.BooleanField(
        default=False,
        verbose_name='В архиве',
        help_text='Отметка о перемещении товара в архив.',
    )

    class Meta:
        db_table = 'products'
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def save(self, *args, **kwargs):
        if self.is_archive:
            self.is_public = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name}'


class ProductCategory(models.Model):
    """
    Модель принадлежности товаров к категориям.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_categories'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='category_products',
    )

    class Meta:
        db_table = 'products_categories'
        verbose_name = 'Товары в категориях'
        verbose_name_plural = 'Товары в категориях'

    def __str__(self):
        return f'{self.product} -> {self.category}'
