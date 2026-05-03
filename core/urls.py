"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from productos.views import *
from productos import views
from django.conf.urls.static import static
from django.conf import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView 
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from usuarios.views import UsuarioViewSet
from tienda.views import OrdenCompraViewSet, CarritoViewSet, ItemCarritoViewSet
from rest_framework.routers import DefaultRouter
from django.urls import include
from chatbot.views import ChatbotView

router = DefaultRouter()
router.register('usuario', UsuarioViewSet, basename='usuario')
router.register('ordenes-compra', OrdenCompraViewSet, basename='ordenes-compra')
router.register('carritos', CarritoViewSet, basename='carritos')
router.register('items-carrito', ItemCarritoViewSet, basename='items-carrito')

urlpatterns = [
    path('api/', include(router.urls)),

    path('admin/', admin.site.urls),
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='refresh token'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/productos/', InventarioProductos.as_view(), name='productos'),
    path('api/productos/<int:pk>/', InventarioProductosDetail.as_view(), name='productos_detail'),
    path('api/categorias/', InventarioCategoria.as_view(), name='categorias'),
    path('api/subcategorias/', InventarioSubcategoria.as_view(), name='subcategorias'),
    path('api/chatbot/', ChatbotView.as_view(), name='chatbot'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
