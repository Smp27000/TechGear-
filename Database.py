from pymongo.synchronous.database import Database
from pymongo import collection
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client.samuelpalaciohoyos_db_user
collection = db["taller 2"]

async def test_collection():
    try:
        await client.admin.command('ping')
        print("Conección exitosa a MongoDB Atlas")

        #Crear objeto de prueba

        doctest = {
            "nombre": "Mesa Prueba",
            "material": "Madera",
            "peso": 5.5,
            "valoracion": 1200.5,
        }
        await collection.insert_one(doctest)
        print("Documento insertado exitosamente")

        #Buscar documentos

        documents = await collection.find().to_list(length=None)
        print("Documentos encontrados")
        for document in documents:
            print(document)
            print(f"Nombre: {document['nombre']}")
            print(f"Material: {document['material']}")
            print(f"Peso: {document['peso']}")
            print(f"Valoracion: {document['valoracion']}")
            print("_________________________________________________________________")
        

    except Exception as e:
        print(f"Error al conectar a MongoDB Atlas: {e}")
if __name__ == "__main__":
    asyncio.run(test_collection())