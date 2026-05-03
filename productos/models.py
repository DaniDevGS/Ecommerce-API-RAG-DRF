from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from chatbot.vectors import indexar_productos, index

# Create your models here.
class BaseModel(models.Model):
    creado = models.DateTimeField(auto_now_add=True,)
    modificado = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Categoria(BaseModel):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

class Subcategoria(BaseModel):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="subcategorias")
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.categoria.nombre} > {self.nombre}"

    class Meta:
        verbose_name = "Subcategoría"
        verbose_name_plural = "Subcategorías"

class Producto(BaseModel):
    nombre = models.CharField(max_length=100)
    caracteristicas = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    descripcion = models.TextField(blank=True)
    subcategoria = models.ForeignKey(Subcategoria, on_delete=models.PROTECT, related_name="productos", null=True, blank=True)
    cantidad = models.IntegerField(default=1)
    imagen = models.ImageField(upload_to=f'producto_portada/', null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

@receiver(post_save, sender=Producto)
def sincronizar_producto_con_upstash(sender, instance, **kwargs):
    try:
        indexar_productos([instance])
    except Exception as e:
        print(f"Error sincronizando con Upstash: {e}")

@receiver(post_delete, sender=Producto)
def eliminar_producto_de_upstash(sender, instance, **kwargs):
    try:
        index.delete(ids=[str(instance.id)])
    except Exception as e:
        print(f"Error eliminando de Upstash: {e}")
