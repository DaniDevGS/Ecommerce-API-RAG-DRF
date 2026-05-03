from rest_framework import serializers
from .models import *

class ProductoSerializer(serializers.ModelSerializer):
    # usuario = serializers.ReadOnlyField(source='usuario.username')

    subcategoria = serializers.ReadOnlyField(source='subcategoria.nombre')
    class Meta:
        model = Producto
        # fields = '__all__'
        # #!Por ahora
        fields = ['id','nombre','precio','descripcion','subcategoria','cantidad','imagen', 'caracteristicas']

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'
        fields = ['id','nombre']

class SubcategoriaSerializer(serializers.ModelSerializer):
    # categoria = serializers.ReadOnlyField(source='categoria.nombre')
    class Meta:
        model = Subcategoria
        fields = '__all__'
        #!Por ahora
        # fields = ['id','nombre','categoria',]