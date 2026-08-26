def carrito(request):
    return {"carrito": request.session.get("carrito", {})}


def carrito_count(request):
    carrito = request.session.get("carrito", {})
    return {"carrito_count": sum(carrito.values())}

def carrito_total(request):
    carrito = request.session.get("carrito", {})
    total = 0
    for item in carrito.values():
        total += item["subtotal"]
    return {"carrito_total": total}