# Guía de Despliegue en Render y Vercel (TechGear)

Esta guía explica paso a paso cómo subir y ejecutar tu proyecto tanto en **Render** como en **Vercel**.

---

## 1. Despliegue en Render (Recomendado para Backend y Frontend)

Render permite desplegar el Backend (FastAPI) y el Frontend (Django) de dos formas:

### Opción A: Despliegue Automático con Blueprint (Un solo clic)
1. Sube tu código a **GitHub**.
2. Ve a [Render Dashboard](https://dashboard.render.com/) y haz clic en **New +** -> **Blueprint**.
3. Conecta tu repositorio de GitHub.
4. Render detectará automáticamente el archivo `render.yaml` y creará los 2 servicios:
   - `techgear-backend` (FastAPI)
   - `techgear-frontend` (Django)
5. En la pantalla de configuración, ingresa el valor de la variable de entorno:
   - `MONGODB_URI`: Tu URL de conexión a MongoDB Atlas (ejemplo: `mongodb+srv://samuelpalaciohoyos_db_user:...@cluster.mongodb.net/`).
6. Haz clic en **Apply**. Render creará e interconectará ambos servicios automáticamente.

---

### Opción B: Despliegue Manual Servicio por Servicio

#### 1. Backend (FastAPI):
- **New +** -> **Web Service**
- **Root Directory**: `Backend`
- **Environment**: `Python`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**:
  - `MONGODB_URI`: Tu connection string de MongoDB Atlas.
  - `DB_NAME`: `samuelpalaciohoyos_db_user`
  - `PYTHON_VERSION`: `3.11.9`
- Copia la URL que te asigna Render (ejemplo: `https://techgear-backend.onrender.com`).

#### 2. Frontend (Django):
- **New +** -> **Web Service**
- **Root Directory**: `Frontend`
- **Environment**: `Python`
- **Build Command**: `./build.sh` (o `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput`)
- **Start Command**: `gunicorn techgear.wsgi:application --bind 0.0.0.0:$PORT`
- **Environment Variables**:
  - `SECRET_KEY`: Cualquier clave secreta segura o genera una.
  - `DEBUG`: `False`
  - `API_URL`: La URL de tu backend (ejemplo: `https://techgear-backend.onrender.com`).
  - `PYTHON_VERSION`: `3.11.9`

---

## 2. Despliegue en Vercel

En Vercel puedes desplegar cada carpeta como un proyecto independiente:

### 1. Desplegar Frontend (Django) en Vercel:
1. En [Vercel Dashboard](https://vercel.com/dashboard), haz clic en **Add New...** -> **Project**.
2. Selecciona tu repositorio.
3. En **Root Directory**, haz clic en **Edit** y selecciona la carpeta `Frontend`.
4. En **Environment Variables**, agrega:
   - `API_URL`: La URL pública de tu Backend en Render (ej: `https://techgear-backend.onrender.com`).
   - `SECRET_KEY`: Tu clave secreta.
   - `DEBUG`: `False`
5. Haz clic en **Deploy**. Vercel compilará los archivos estáticos y ejecutará Django mediante Serverless WSGI.

### 2. Desplegar Backend (FastAPI) en Vercel (Opcional):
1. Añade un nuevo proyecto en Vercel seleccionando la carpeta raíz `Backend`.
2. Agrega la variable de entorno:
   - `MONGODB_URI`: Tu URI de MongoDB Atlas.
3. Haz clic en **Deploy**.

---

## 3. Variables de Entorno Clave

| Variable | Dónde se usa | Descripción | Ejemplo |
|---|---|---|---|
| `MONGODB_URI` | Backend | Cadena de conexión a MongoDB Atlas | `mongodb+srv://user:pass@cluster...` |
| `DB_NAME` | Backend | Nombre de la base de datos MongoDB | `samuelpalaciohoyos_db_user` |
| `API_URL` | Frontend | URL donde corre la API FastAPI | `https://techgear-backend.onrender.com` |
| `SECRET_KEY` | Frontend | Llave de seguridad de Django | `django-insecure-...` |
| `DEBUG` | Frontend | Modo depuración (`True`/`False`) | `False` en producción |
