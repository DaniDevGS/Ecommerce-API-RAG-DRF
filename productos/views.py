from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from decimal import Decimal
from .utils.conversion import obtener_cambio
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser, IsAuthenticated

# Create your views here.
class InventarioProductos(APIView):
    def get(self, request):
        nombre = self.request.query_params.get("nombre")
        subcategoria = self.request.query_params.get("subcategoria")
        precio = self.request.query_params.get("precio")
        dato = Producto.objects.all()

        cambio_bolivar = obtener_cambio()
        if cambio_bolivar is not None:
            cambio_bolivar = Decimal(str(cambio_bolivar))

        if nombre:
            dato = dato.filter(nombre__icontains=nombre)

        if subcategoria:
            dato = dato.filter(subcategoria__nombre__icontains=subcategoria)

        if precio:
            dato = dato.filter(precio__icontains=precio)

        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(dato, request)
        serializer = ProductoSerializer(page, many=True)

        data = serializer.data

        for item in data:
            precio_usd = Decimal(str(item.get('precio', 0)))

            if cambio_bolivar is not None:
                conversion = precio_usd * cambio_bolivar
                item['precio_bs'] = "{:.2f}".format(conversion)

            else:
                item['precio_bs'] = None

        return paginator.get_paginated_response(data)

class InventarioProductosDetail(APIView):
    def get(self, request, pk=None):
        try:
            producto = Producto.objects.get(id=pk)
            serializer = ProductoSerializer(producto)
            
            cambio_bolivar = obtener_cambio()
            data = serializer.data

            precio_usd = Decimal(str(data.get('precio', 0)))
            if cambio_bolivar is not None:
                cambio_bolivar = Decimal(str(cambio_bolivar))
                conversion = precio_usd * cambio_bolivar
                data['precio_bs'] = "{:.2f}".format(conversion)
            else:
                data['precio_bs'] = None

            return Response(data, status=status.HTTP_200_OK)
        
        except Producto.DoesNotExist:
            return Response(data={'mensaje': 'No existe'}, status=status.HTTP_404_NOT_FOUND)


class InventarioCategoria(APIView):
    def get(self, request):
        data = Categoria.objects.all()
        serializer = CategoriaSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class InventarioSubcategoria(APIView):
    def get(self, request):
        data = Subcategoria.objects.all()
        serializer = SubcategoriaSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    