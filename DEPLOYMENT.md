# Guía de Despliegue en Railway - Backend Citas Médicas

Esta guía te ayudará a desplegar el backend Flask del sistema de citas médicas en Railway.

## Prerrequisitos

1. Una cuenta en [Railway](https://railway.app) (puedes registrarte con GitHub)
2. El código del backend subido a un repositorio Git (GitHub)
3. Una base de datos PostgreSQL (Railway puede proveer una, o puedes usar Supabase)

## Opción A: Despliegue con Base de Datos de Railway

### 1. Crear el Proyecto

1. Inicia sesión en [Railway](https://railway.app)
2. Haz clic en **"New Project"**
3. Selecciona **"Deploy from GitHub repo"**
4. Conecta tu cuenta de GitHub si no lo has hecho
5. Selecciona el repositorio `project-citas-medicas`
6. Railway detectará la carpeta `back-citas` - si no, configúrala como el directorio raíz

### 2. Agregar Base de Datos PostgreSQL

1. En el proyecto, haz clic en **"+ New"**
2. Selecciona **"Database"** → **"Add PostgreSQL"**
3. Railway creará automáticamente la base de datos
4. Haz clic en la base de datos y copia el **DATABASE_URL** desde Variables

### 3. Configurar Variables de Entorno

En tu servicio del backend (no en la base de datos), ve a **Variables** y añade:

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `SQLALCHEMY_DATABASE_URI` | `${{Postgres.DATABASE_URL}}` | Railway lo reemplaza automáticamente |
| `SQLALCHEMY_TRACK_MODIFICATIONS` | `False` | Desactivar tracking |
| `SECRET_KEY` | `tu_clave_secreta_muy_segura` | **Cambiar por una clave segura** |
| `FRONTEND_URL` | `https://tu-frontend.vercel.app` | URL de tu frontend en Vercel |
| `FLASK_ENV` | `production` | Modo producción |
| `API_PERU_DEV_TOKEN` | `tu_token` | *Opcional* - Para consulta de DNI |
| `GEMINI_API_KEY` | `tu_api_key` | *Opcional* - Para funciones de IA |

### 4. Configurar Root Directory

Si tienes un monorepo con frontend y backend:
1. Ve a **Settings** del servicio
2. En **Root Directory**, escribe: `back-citas`
3. Haz clic en **Redeploy** para aplicar

### 5. Verificar Despliegue

1. Espera a que Railway complete el build
2. Una vez desplegado, copia la URL generada (ej: `https://back-citas-production.up.railway.app`)
3. Visita `https://tu-url.railway.app/api/health` para verificar que funciona

---

## Opción B: Usar Supabase como Base de Datos

Si prefieres usar Supabase (que ya tienes configurado):

### Variables de Entorno

| Variable | Valor |
|----------|-------|
| `SQLALCHEMY_DATABASE_URI` | `postgresql://postgres.[tu-proyecto]:password@aws-0-us-west-1.pooler.supabase.com:6543/postgres` |

> ⚠️ **Importante**: Usa el **Connection Pooler** de Supabase (puerto `6543`) para mejor rendimiento.

---

## Archivos de Configuración Incluidos

### `Procfile`
```
web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120
```
- **gunicorn**: Servidor WSGI de producción
- **workers 2**: 2 procesos worker (ajustar según plan de Railway)
- **threads 4**: 4 threads por worker
- **timeout 120**: Timeout de 2 minutos para requests largos

### `railway.json`
```json
{
  "build": { "builder": "NIXPACKS" },
  "deploy": {
    "startCommand": "gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### `.env.example`
Template con todas las variables de entorno necesarias.

---

## Endpoints Importantes

Una vez desplegado, tu API tendrá estos endpoints:

| Endpoint | Descripción |
|----------|-------------|
| `GET /` | Información básica de la API |
| `GET /api/health` | Health check (usado por Railway) |
| `POST /api/auth/login` | Autenticación |
| `GET /api/pacientes/` | Lista de pacientes |
| `GET /api/citas/` | Lista de citas |
| ... | Otros endpoints |

---

## Conectar Frontend con Backend

Una vez que tengas la URL del backend desplegado:

1. Ve a tu proyecto de Vercel (frontend)
2. En **Settings** → **Environment Variables**
3. Actualiza `VITE_API_BASE_URL` con la URL de Railway:
   ```
   VITE_API_BASE_URL=https://back-citas-production.up.railway.app/api
   ```
4. Redeplegar el frontend

---

## Solución de Problemas

### Error: "Connection refused" o CORS

1. Verifica que `FRONTEND_URL` esté correctamente configurado en Railway
2. Asegúrate de incluir el protocolo completo: `https://tu-frontend.vercel.app`
3. Si tienes múltiples frontends, sepáralos con coma:
   ```
   FRONTEND_URL=https://app1.vercel.app,https://app2.vercel.app
   ```

### Error: "Application failed to respond"

1. Revisa los logs en Railway Dashboard
2. Verifica que `SQLALCHEMY_DATABASE_URI` esté correctamente configurado
3. Asegúrate de que la base de datos esté accesible

### Error: Base de datos

1. Si usas Railway PostgreSQL, asegúrate de usar la variable de referencia: `${{Postgres.DATABASE_URL}}`
2. Si usas Supabase, verifica el connection string y el puerto (6543 para pooler)

### Build Fallido

1. Revisa los logs de build en Railway
2. Verifica que `requirements.txt` tenga todas las dependencias
3. Asegúrate de que `gunicorn` esté en requirements.txt

---

## Comandos Útiles (Local)

```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Login
railway login

# Vincular proyecto existente
railway link

# Ver logs
railway logs

# Ejecutar comando en contexto de Railway
railway run python init_db.py

# Deploy manual
railway up
```

---

## Migración de Base de Datos

Si necesitas crear las tablas iniciales después del despliegue:

```bash
# Conectarse al contexto de Railway
railway run python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Tablas creadas!')"
```

O usa el dashboard de Railway:
1. Ve a tu servicio
2. Haz clic en **"Commands"**
3. Ejecuta: `python init_db.py`

---

## Recursos

- [Documentación de Railway](https://docs.railway.app/)
- [Guía de Flask en Railway](https://docs.railway.app/guides/flask)
- [Variables de Entorno en Railway](https://docs.railway.app/develop/variables)
- [Railway CLI](https://docs.railway.app/develop/cli)
