from django.db import models
from productos.models import BaseModel, Producto, Categoria, Subcategoria
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone

# Create your models here.
class OrdenCompra(models.Model):
    ESTADO_CHOICES = (
        ('PENDIENTE', 'Pendiente'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
    )
    nota_admin = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    fecha_orden = models.DateTimeField(default=timezone.now)
    subtotal_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True) # type: ignore
    monto_final_pago = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True)  # type: ignore
    moneda_pago = models.CharField(max_length=10, default='USD')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    imagen_comprobante = models.ImageField(upload_to='comprobantes/', null=True, blank=True)

    def __str__(self):
        username = self.user.username if self.user else "Desconocido"
        return f"Orden {self.id} de {username}"

class DetalleOrden(models.Model):
    orden = models.ForeignKey(OrdenCompra, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def total_detalle(self):
        return self.precio_unitario * self.cantidad

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Orden {self.orden.id}"

@receiver(post_save, sender=OrdenCompra)
def update_stock_on_approval(sender, instance, **kwargs):
    if instance.estado == 'APROBADA':
        for detalle in instance.detalles.all():
            producto = detalle.producto
            if producto.cantidad >= detalle.cantidad:
                producto.cantidad -= detalle.cantidad
                producto.save()


class ItemCarrito(models.Model):
    carrito = models.ForeignKey('Carrito', on_delete=models.CASCADE, related_name='items_carrito', null=True, blank=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unidad = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.producto and (self.precio_unidad is None or self.precio_unidad == 0):
            self.precio_unidad = self.producto.precio
        super().save(*args, **kwargs)

    def total_item(self):
        return (self.precio_unidad or 0) * self.cantidad

    def __str__(self):
        if self.carrito and self.carrito.user:
            return f"{self.cantidad} x {self.producto.nombre} en Carrito de {self.carrito.user.username}"
        return f"{self.cantidad} x {self.producto.nombre} (Sin carrito)"

class Carrito(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Carrito de {self.user.username}"



@receiver(post_save, sender=User)
def create_user_carrito_post_save(sender, instance, created, **kwargs):
    if created:
        Carrito.objects.get_or_create(user=instance)
