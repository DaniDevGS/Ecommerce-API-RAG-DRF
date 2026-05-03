from rest_framework import serializers
from .models import OrdenCompra, Carrito, ItemCarrito, DetalleOrden


class ItemCarritoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    total_item = serializers.SerializerMethodField()
    
    class Meta:
        model = ItemCarrito
        fields = ('id', 'producto', 'producto_nombre', 'cantidad', 'precio_unidad', 'total_item')
        read_only_fields = ('precio_unidad',)
    
    def get_total_item(self, obj):
        return obj.total_item()

class DetalleOrdenSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.ReadOnlyField(source='producto.nombre')
    total_detalle = serializers.ReadOnlyField()

    class Meta:
        model = DetalleOrden
        fields = ('id', 'producto', 'producto_nombre', 'cantidad', 'precio_unitario', 'total_detalle')

class CarritoSerializer(serializers.ModelSerializer):
    items_carrito = ItemCarritoSerializer(many=True, read_only=True)
    user = serializers.ReadOnlyField(source='user.username')
    total_carrito = serializers.SerializerMethodField()
    
    class Meta:
        model = Carrito
        fields = ('user', 'fecha_creacion', 'items_carrito', 'total_carrito')
    
    def get_total_carrito(self, obj):
        return sum(item.total_item() for item in obj.items_carrito.all())

class OrdenCompraSerializer(serializers.ModelSerializer):
    detalles = DetalleOrdenSerializer(many=True, read_only=True)
    user = serializers.ReadOnlyField(source='user.username')
    nota_admin = serializers.SerializerMethodField()
    
    class Meta:
        model = OrdenCompra
        fields = ('id', 'user', 'fecha_orden', 'subtotal_usd', 'monto_final_pago', 'moneda_pago', 'estado', 'imagen_comprobante', 'nota_admin', 'detalles')
    
    def get_nota_admin(self, obj):
        if obj.estado in ['APROBADA', 'RECHAZADA']:
            return obj.nota_admin
        return None
