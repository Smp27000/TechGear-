def carrito(request):
    return {"carrito": request.session.get("carrito", {})}


def carrito_count(request):
    carrito = request.session.get("carrito", {})
    if isinstance(carrito, dict):
        total = 0
        for val in carrito.values():
            if isinstance(val, int):
                total += val
            elif isinstance(val, dict):
                total += val.get("cantidad", 0)
        return {"carrito_count": total}
    return {"carrito_count": 0}


def carrito_total(request):
    carrito = request.session.get("carrito", {})
    total = 0
    if isinstance(carrito, dict):
        for val in carrito.values():
            if isinstance(val, dict):
                total += val.get("subtotal", 0)
            elif isinstance(val, int):
                total += val
    return {"carrito_total": total}
