import requests
from django.shortcuts import render, redirect
from django.contrib import messages

API_URL = "http://127.0.0.1:8000"
CART_KEY = "carrito"


def _get_cart(request):
    return request.session.setdefault(CART_KEY, {})


# ---------------- CATÁLOGO ----------------

def index(request):
    productos = []
    error = None
    try:
        r = requests.get(f"{API_URL}/productos", timeout=5)
        r.raise_for_status()
        productos = r.json()
        for p in productos:
            p["id"] = p.pop("_id")
    except requests.exceptions.RequestException:
        error = "No se pudo conectar con la API. Verifica que el backend esté corriendo en el puerto 8000."

    return render(request, "catalogo/index.html", {"productos": productos, "error": error})


def detalle(request, producto_id):
    producto = None
    error = None
    try:
        r = requests.get(f"{API_URL}/productos/{producto_id}", timeout=5)
        r.raise_for_status()
        producto = r.json()
        producto["id"] = producto.pop("_id")
    except requests.exceptions.RequestException:
        error = "No se pudo cargar este producto."

    return render(request, "catalogo/detalle.html", {"producto": producto, "error": error})


# ---------------- CREAR PRODUCTO ----------------

def crear_producto(request):
    error = None
    if request.method == "POST":
        try:
            payload = {
                "nombre": request.POST.get("nombre", "").strip(),
                "material": request.POST.get("material", "").strip(),
                "peso": float(request.POST.get("peso")),
                "valoracion": float(request.POST.get("valoracion")),
            }
            r = requests.post(f"{API_URL}/productos", json=payload, timeout=5)
            r.raise_for_status()
            messages.success(request, f'"{payload["nombre"]}" se añadió al inventario.')
            return redirect("index")
        except (TypeError, ValueError):
            error = "Revisa que peso y valoración sean números válidos."
        except requests.exceptions.RequestException:
            error = "No se pudo crear el producto. Verifica que el Backend esté activo."

    return render(request, "catalogo/producto_form.html", {"error": error})


# ---------------- CARRITO ----------------

def agregar_carrito(request, producto_id):
    cantidad = int(request.POST.get("cantidad", 1))
    carrito = _get_cart(request)
    carrito[producto_id] = carrito.get(producto_id, 0) + max(cantidad, 1)
    request.session.modified = True
    messages.success(request, "Producto añadido al carrito.")
    return redirect("detalle", producto_id=producto_id)


def ver_carrito(request):
    carrito = _get_cart(request)
    items = []
    error = None

    for pid, cantidad in carrito.items():
        try:
            r = requests.get(f"{API_URL}/productos/{pid}", timeout=5)
            r.raise_for_status()
            p = r.json()
            items.append({"id": pid, "nombre": p["nombre"], "material": p["material"], "cantidad": cantidad})
        except requests.exceptions.RequestException:
            error = "Algunos productos del carrito ya no están disponibles."

    return render(request, "catalogo/carrito.html", {"items": items, "error": error})


def actualizar_carrito(request, producto_id):
    accion = request.POST.get("accion")
    carrito = _get_cart(request)

    if accion == "sumar":
        carrito[producto_id] = carrito.get(producto_id, 0) + 1
    elif accion == "restar":
        if carrito.get(producto_id, 0) > 1:
            carrito[producto_id] -= 1
        else:
            carrito.pop(producto_id, None)
    elif accion == "eliminar":
        carrito.pop(producto_id, None)

    request.session.modified = True
    return redirect("carrito")


def checkout(request):
    carrito = _get_cart(request)
    if not carrito:
        return redirect("carrito")

    fallidos = []
    for pid, cantidad in list(carrito.items()):
        try:
            r = requests.post(f"{API_URL}/pedidos", json={"producto_id": pid, "cantidad": cantidad}, timeout=5)
            r.raise_for_status()
        except requests.exceptions.RequestException:
            fallidos.append(pid)

    request.session[CART_KEY] = {}
    request.session.modified = True
    return render(request, "catalogo/confirmacion.html", {"fallidos": fallidos})