from django.shortcuts import render
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import OrdenCompra, Carrito, ItemCarrito, DetalleOrden
from .serializers import OrdenCompraSerializer, CarritoSerializer, ItemCarritoSerializer
from django.db import transaction
import uuid

# Create your views here.

class OrdenCompraViewSet(viewsets.ModelViewSet):
    serializer_class = OrdenCompraSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # N+1 Optimization: prefetch details and their products
        return OrdenCompra.objects.filter(user=self.request.user).prefetch_related(
            'detalles__producto'
        ).select_related('user')

    def perform_create(self, serializer):
        user = self.request.user
        
        # We use transaction.atomic to ensure data integrity
        with transaction.atomic():
            try:
                # Explicitly select_for_update to handle concurrency if needed
                carrito = Carrito.objects.select_related('user').get(user=user)
            except Carrito.DoesNotExist:
                raise serializers.ValidationError({"error": "No tienes un carrito"})
                
            items_carrito = carrito.items_carrito.all()
            if not items_carrito.exists():
                raise serializers.ValidationError({"error": "Tu carrito está vacío"})
                
            subtotal = sum(item.total_item() for item in items_carrito)
            
            # Save the order
            orden = serializer.save(
                user=user, 
                subtotal_usd=subtotal, 
                monto_final_pago=subtotal,
                estado='PENDIENTE'
            )
            
            # Create Detalles (frozen items)
            detalles = []
            for item in items_carrito:
                detalles.append(DetalleOrden(
                    orden=orden,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.precio_unidad or item.producto.precio
                ))
            
            DetalleOrden.objects.bulk_create(detalles)
            
            # Empty the cart
            items_carrito.delete()

    # Generic "crear_desde_carrito" is no longer needed 
    # as the standard POST /create/ now handles it.


class ItemCarritoViewSet(viewsets.ModelViewSet):
    serializer_class = ItemCarritoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # ItemCarrito no longer has "orden", only "carrito"
        return ItemCarrito.objects.filter(
            carrito__user=self.request.user
        ).select_related('producto', 'carrito__user')

    def perform_create(self, serializer):
        carrito, created = Carrito.objects.get_or_create(user=self.request.user)
        producto = serializer.validated_data['producto']
        precio_unidad = producto.precio
        serializer.save(carrito=carrito, precio_unidad=precio_unidad)

class CarritoViewSet(viewsets.ModelViewSet):
    serializer_class = CarritoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Optimization: prefetch items and their products
        return Carrito.objects.filter(user=self.request.user).prefetch_related(
            'items_carrito__producto'
        ).select_related('user')

    # mi_carrito endpoint removed as it was redundant.
    # Frontend can use List or Retrieve.
