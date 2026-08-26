from pydantic import BaseModel, Field
from typing import Optional

class ProductoBase(BaseModel):
    nombre: str = Field(..., description="Nombre del producto", min_length=3)
    material: str = Field(..., description="Material del producto", min_length=3)
    peso: float = Field(..., description="Peso del producto", gt=0)
    valoracion: float = Field(..., description="Valoracion del producto", gt=0)

class Producto(ProductoBase):
    id: str

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(ProductoBase):
    pass

class PedidoBase(BaseModel):
    producto_id: str = Field(..., description="ID (ObjectId) del producto")
    cantidad: int = Field(..., description="Cantidad del producto", gt=0)

class PedidoCreate(PedidoBase):
    pass