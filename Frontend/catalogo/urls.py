from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("producto/nuevo/", views.crear_producto, name="crear_producto"),
    path("producto/<str:producto_id>/", views.detalle, name="detalle"),
    path("carrito/", views.ver_carrito, name="carrito"),
    path("carrito/agregar/<str:producto_id>/", views.agregar_carrito, name="agregar_carrito"),
    path("carrito/actualizar/<str:producto_id>/", views.actualizar_carrito, name="actualizar_carrito"),
    path("carrito/checkout/", views.checkout, name="checkout"),
    path("pedido/confirmacion/", views.confirmacion, name="confirmacion"),
]