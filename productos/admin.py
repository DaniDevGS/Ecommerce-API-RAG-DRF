from django.contrib import admin
from .models import *
from tienda.models import OrdenCompra, Carrito, ItemCarrito, DetalleOrden
from chatbot.models import Conversacion

# Register your models here.
admin.site.register(Categoria)
admin.site.register(Producto)
admin.site.register(Subcategoria)

admin.site.register(OrdenCompra)
admin.site.register(Carrito)
admin.site.register(ItemCarrito)
admin.site.register(DetalleOrden)

admin.site.register(Conversacion)