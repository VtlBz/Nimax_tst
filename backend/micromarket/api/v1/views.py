from django.db.models import ProtectedError

from rest_framework import status, viewsets
from rest_framework.response import Response

from goods.models import Category, Product
from .serializers import (CategorySerializer,
                          ProductReadSerializer,
                          ProductWriteSerializer,)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    ordering = ('-id',)
 
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, many=isinstance(request.data, list)
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED, headers=headers)

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
    queryset = Product.objects.all()
    # filter_backends = (DjangoFilterBackend,)
    # filterset_class = ProductFilter
    ordering = ('-id',)

    def get_queryset(self):
        queryset = self.queryset
        if self.action == 'list':
            queryset = queryset.filter(
                is_archive=False
            ).prefetch_related('categories')
        return queryset

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return ProductWriteSerializer
        return ProductReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, many=isinstance(request.data, list)
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED, headers=headers)

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
