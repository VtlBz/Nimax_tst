from django.db.models import ProtectedError
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status, viewsets
from rest_framework.response import Response

from goods.models import Category, Product
from utils.filters import ProductFilter
from .serializers import (CategorySerializer,
                          ProductReadSerializer,
                          ProductWriteSerializer,)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    Представление `/categories/`.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    ordering = ('-id',)

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError as e:
            error_message = 'Нельзя удалить категорию, имеющую товары'
            response = {'error': error_message,
                        'detail': 'Нельзя удалить не пустую категорию, '
                                  'содержащую товары.  Количество связанных '
                                  f'записей: {len(e.protected_objects)}'}
            return Response(
                response, status=status.HTTP_400_BAD_REQUEST
            )


class GoodsViewSet(viewsets.ModelViewSet):
    """
    Представление `/goods/`.

    Метод `DELETE` не удаляет объект,
    а только изменяет состояние свойства `is_archive`.
    """

    queryset = Product.objects.prefetch_related('categories')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductFilter
    ordering = ('-id',)

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return ProductWriteSerializer
        return ProductReadSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_archive:
            error_message = 'Товар уже архиве'
            return Response(
                {'error': error_message},
                status=status.HTTP_400_BAD_REQUEST
            )
        instance.is_archive = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
