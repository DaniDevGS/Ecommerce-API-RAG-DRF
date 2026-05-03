from django.core.management.base import BaseCommand
from productos.models import Producto
from chatbot.vectors import indexar_productos

class Command(BaseCommand):
    help = 'Sincroniza todos los productos con el índice de Upstash Vector'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Obteniendo productos...'))
        productos = Producto.objects.all()
        total = productos.count()
        
        if total == 0:
            self.stdout.write(self.style.WARNING('No se encontraron productos para indexar.'))
            return

        self.stdout.write(f'Enviando {total} productos a Upstash...')
        
        try:
            indexar_productos(productos)
            self.stdout.write(self.style.SUCCESS(f'¡Éxito! {total} productos sincronizados correctamente.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error durante la sincronización: {str(e)}'))
