import os
import requests
from django.shortcuts import render, redirect
from django.contrib import messages

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")
CART_KEY = "carrito"



def _get_cart(request):
    return request.session.setdefault(CART_KEY, {})


# ---------------- CATÁLOGO ----------------

def index(request):
    productos = []
    error = None
    try:
        r = requests.get(f"{API_URL}/productos", timeout=4)
        r.raise_for_status()
        productos = r.json()
        for p in productos:
            p["id"] = p.pop("_id")
    except requests.exceptions.ConnectionError:
        error = "No se puede conectar con el Backend (FastAPI). Por favor verifica que el servidor esté activo en el puerto 8000."
    except requests.exceptions.Timeout:
        error = "El servidor Backend tardó demasiado en responder (Tiempo de espera agotado)."
    except requests.exceptions.RequestException as e:
        error = f"Error al consultar el catálogo de productos: {str(e)}"

    return render(request, "catalogo/index.html", {"productos": productos, "error": error})


def detalle(request, producto_id):
    producto = None
    error = None
    try:
        r = requests.get(f"{API_URL}/productos/{producto_id}", timeout=4)
        r.raise_for_status()
        producto = r.json()
        producto["id"] = producto.pop("_id")
    except requests.exceptions.ConnectionError:
        error = "No se pudo conectar con el servidor Backend (FastAPI). Verifica que esté encendido."
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            error = "El producto solicitado no existe o fue eliminado."
        else:
            error = "Error al consultar los detalles del producto."
    except requests.exceptions.RequestException:
        error = "No se pudo cargar este producto en este momento."

    return render(request, "catalogo/detalle.html", {"producto": producto, "error": error})


# ---------------- CREAR PRODUCTO ----------------

def crear_producto(request):
    error = None
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        material = request.POST.get("material", "").strip()
        peso_str = request.POST.get("peso", "").strip()
        valoracion_str = request.POST.get("valoracion", "").strip()

        try:
            peso = float(peso_str)
            valoracion = float(valoracion_str)

            if len(nombre) < 3:
                raise ValueError("El nombre debe tener al menos 3 caracteres.")
            if len(material) < 3:
                raise ValueError("El material debe tener al menos 3 caracteres.")
            if peso <= 0:
                raise ValueError("El peso debe ser un número mayor a 0.")
            if valoracion <= 0 or valoracion > 5:
                raise ValueError("La valoración debe estar entre 0.1 y 5.0.")

            payload = {
                "nombre": nombre,
                "material": material,
                "peso": peso,
                "valoracion": valoracion,
            }
            r = requests.post(f"{API_URL}/productos", json=payload, timeout=5)
            r.raise_for_status()
            messages.success(request, f'"{nombre}" se añadió correctamente al inventario.')
            return redirect("index")
        except ValueError as ve:
            error = str(ve)
        except requests.exceptions.ConnectionError:
            error = "No se pudo conectar con el Backend (FastAPI). Verifica que esté corriendo en el puerto 8000."
        except requests.exceptions.RequestException:
            error = "Ocurrió un problema al registrar el producto en el Backend."

    return render(request, "catalogo/producto_form.html", {"error": error})


# ---------------- CARRITO ----------------

def agregar_carrito(request, producto_id):
    try:
        cantidad = int(request.POST.get("cantidad", 1))
        if cantidad < 1:
            cantidad = 1
    except (TypeError, ValueError):
        cantidad = 1

    carrito = _get_cart(request)
    carrito[producto_id] = carrito.get(producto_id, 0) + cantidad
    request.session.modified = True
    messages.success(request, "Producto añadido al carrito con éxito.")
    return redirect("detalle", producto_id=producto_id)


def ver_carrito(request):
    carrito = _get_cart(request)
    items = []
    error = None

    if not carrito:
        return render(request, "catalogo/carrito.html", {"items": items, "error": error})

    # Consultar productos en FastAPI
    for pid, cantidad in list(carrito.items()):
        try:
            r = requests.get(f"{API_URL}/productos/{pid}", timeout=4)
            if r.status_code == 200:
                p = r.json()
                items.append({
                    "id": pid,
                    "nombre": p.get("nombre", "Producto"),
                    "material": p.get("material", "N/A"),
                    "peso": p.get("peso", 0),
                    "cantidad": cantidad
                })
            elif r.status_code == 404:
                error = "Uno o más productos en tu carrito ya no están disponibles en el catálogo."
        except requests.exceptions.ConnectionError:
            error = "No se pudo conectar con el Backend para verificar los productos del carrito."
            items.append({
                "id": pid,
                "nombre": f"Producto (ID: {pid[:8]}...)",
                "material": "No disponible temporalmente",
                "cantidad": cantidad
            })
        except requests.exceptions.RequestException:
            error = "Ocurrió un problema al consultar la información de tus productos."

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


# ---------------- CHECKOUT & CONFIRMACIÓN ----------------

def checkout(request):
    carrito = _get_cart(request)
    if not carrito:
        messages.warning(request, "Tu carrito está vacío. Agrega productos antes de realizar el checkout.")
        return redirect("index")

    # Cargar información detallada de los items en el carrito
    items = []
    total_peso = 0.0
    total_items = 0
    error = None

    for pid, cantidad in carrito.items():
        try:
            r = requests.get(f"{API_URL}/productos/{pid}", timeout=4)
            if r.status_code == 200:
                p = r.json()
                peso = float(p.get("peso", 0.0))
                items.append({
                    "id": pid,
                    "nombre": p.get("nombre", "Producto"),
                    "material": p.get("material", "N/A"),
                    "peso": peso,
                    "cantidad": cantidad,
                    "subtotal_peso": round(peso * cantidad, 2)
                })
                total_peso += peso * cantidad
                total_items += cantidad
            else:
                items.append({
                    "id": pid,
                    "nombre": f"Producto ({pid})",
                    "material": "N/A",
                    "peso": 0.0,
                    "cantidad": cantidad,
                    "subtotal_peso": 0.0
                })
                total_items += cantidad
        except requests.exceptions.ConnectionError:
            error = "Advertencia: El backend FastAPI no responde. Los datos locales del pedido se mantienen."
            items.append({
                "id": pid,
                "nombre": f"Producto ({pid})",
                "material": "N/A",
                "peso": 0.0,
                "cantidad": cantidad,
                "subtotal_peso": 0.0
            })
            total_items += cantidad
        except requests.exceptions.RequestException:
            pass

    if request.method == "POST":
        cliente_nombre = request.POST.get("cliente_nombre", "").strip()
        cliente_email = request.POST.get("cliente_email", "").strip()
        cliente_telefono = request.POST.get("cliente_telefono", "").strip()
        cliente_direccion = request.POST.get("cliente_direccion", "").strip()
        cliente_ciudad = request.POST.get("cliente_ciudad", "").strip()

        form_data = {
            "cliente_nombre": cliente_nombre,
            "cliente_email": cliente_email,
            "cliente_telefono": cliente_telefono,
            "cliente_direccion": cliente_direccion,
            "cliente_ciudad": cliente_ciudad,
        }

        # Validaciones de datos de cliente
        if not all([cliente_nombre, cliente_email, cliente_telefono, cliente_direccion, cliente_ciudad]):
            error = "Por favor completa todos los campos del formulario de envío."
            return render(request, "catalogo/checkout.html", {
                "items": items,
                "total_peso": round(total_peso, 2),
                "total_items": total_items,
                "error": error,
                "form_data": form_data
            })

        items_payload = [{"producto_id": pid, "cantidad": cant} for pid, cant in carrito.items()]

        payload = {
            "cliente_nombre": cliente_nombre,
            "cliente_email": cliente_email,
            "cliente_telefono": cliente_telefono,
            "cliente_direccion": cliente_direccion,
            "cliente_ciudad": cliente_ciudad,
            "items": items_payload
        }

        try:
            r = requests.post(f"{API_URL}/pedidos", json=payload, timeout=6)
            if r.status_code == 201:
                pedido_resp = r.json()
                pedido_id = pedido_resp.get("id")
                
                # Guardar información para la pantalla de confirmación
                request.session["ultimo_pedido"] = {
                    "id": pedido_id,
                    "cliente_nombre": cliente_nombre,
                    "cliente_email": cliente_email,
                    "cliente_direccion": cliente_direccion,
                    "cliente_ciudad": cliente_ciudad,
                    "total_items": total_items,
                    "items": items
                }
                
                # Vaciar carrito tras checkout exitoso
                request.session[CART_KEY] = {}
                request.session.modified = True
                return redirect("confirmacion")
            elif r.status_code in (400, 404):
                detail = r.json().get("detail", "Error al procesar el pedido.")
                error = f"No se pudo completar el pedido: {detail}"
            else:
                error = f"Error inesperado del servidor backend (Código HTTP {r.status_code})."
        except requests.exceptions.ConnectionError:
            error = "Error de Conexión: La API Backend (FastAPI) no está disponible en este momento. Por favor verifica que el servidor esté activo."
        except requests.exceptions.Timeout:
            error = "Tiempo de espera agotado al conectar con el Backend. Por favor intenta de nuevo."
        except requests.exceptions.RequestException as e:
            error = f"Ocurrió un error al enviar tu pedido: {str(e)}"

        return render(request, "catalogo/checkout.html", {
            "items": items,
            "total_peso": round(total_peso, 2),
            "total_items": total_items,
            "error": error,
            "form_data": form_data
        })

    return render(request, "catalogo/checkout.html", {
        "items": items,
        "total_peso": round(total_peso, 2),
        "total_items": total_items,
        "error": error,
        "form_data": {}
    })


def confirmacion(request):
    pedido_info = request.session.get("ultimo_pedido")
    return render(request, "catalogo/confirmacion.html", {"pedido": pedido_info})