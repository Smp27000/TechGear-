from fastapi import FastAPI, HTTPException
from bson import ObjectId
from Models import ProductoBase, PedidoBase
from Database import collection, productos_collection, pedidos_collection

app = FastAPI()


@app.get("/")
async def home():
    return {"mensaje": "API funcionando"}


# ---------------- PRODUCTOS ----------------

@app.post("/productos")
async def crear_producto(producto: ProductoBase):
    nuevo = await productos_collection.insert_one(producto.model_dump())
    return {"id": str(nuevo.inserted_id)}


@app.get("/productos")
async def listar_productos():
    productos = await productos_collection.find().to_list(length=None)
    for p in productos:
        p["_id"] = str(p["_id"])
    return productos


@app.get("/productos/{producto_id}")
async def obtener_producto(producto_id: str):
    try:
        oid = ObjectId(producto_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de producto inválido")
    producto = await productos_collection.find_one({"_id": oid})
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    producto["_id"] = str(producto["_id"])
    return producto


@app.put("/productos/{producto_id}")
async def actualizar_producto(producto_id: str, producto: ProductoBase):
    try:
        oid = ObjectId(producto_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de producto inválido")
    resultado = await productos_collection.update_one(
        {"_id": oid},
        {"$set": producto.model_dump()}
    )
    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"mensaje": "Producto actualizado"}


@app.delete("/productos/{producto_id}")
async def eliminar_producto(producto_id: str):
    try:
        oid = ObjectId(producto_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de producto inválido")
    resultado = await productos_collection.delete_one({"_id": oid})
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"mensaje": "Producto eliminado"}


# ---------------- PEDIDOS ----------------

@app.post("/pedidos")
async def crear_pedido(pedido: PedidoBase):
    # Validar que cada producto exista antes de crear el pedido
    for item in pedido.items:
        try:
            oid = ObjectId(item.producto_id)
        except Exception:
            raise HTTPException(
                status_code=400,
                detail=f"El producto_id '{item.producto_id}' no es un ObjectId válido"
            )
        if not await productos_collection.find_one({"_id": oid}):
            raise HTTPException(
                status_code=400,
                detail=f"El producto {item.producto_id} no existe"
            )

    nuevo = await pedidos_collection.insert_one(pedido.model_dump())
    return {"id": str(nuevo.inserted_id)}


@app.get("/pedidos")
async def listar_pedidos():
    pedidos = await pedidos_collection.find().to_list(length=None)
    for p in pedidos:
        p["_id"] = str(p["_id"])
    return pedidos


@app.get("/pedidos/{pedido_id}")
async def obtener_pedido(pedido_id: str):
    try:
        oid = ObjectId(pedido_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de pedido inválido")
    pedido = await pedidos_collection.find_one({"_id": oid})
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    pedido["_id"] = str(pedido["_id"])
    return pedido