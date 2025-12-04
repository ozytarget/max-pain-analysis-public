# 🚀 Guía de Deployment en Railway (FastAPI Backend)

## Arquitectura Actual

Tu app tiene dos servicios:
1. **FastAPI Backend** (api_backend.py) - Maneja llamadas a APIs terceros
2. **Streamlit Frontend** (app.py) - Interfaz de usuario

Ambos están en el mismo repositorio pero necesitan deployment **separado**.

## 📋 Requisitos

- Repositorio GitHub conectado a Railway
- Todas las variables de entorno configuradas

## ✅ Paso a Paso

### Paso 1: Crear Segundo Servicio en Railway

1. Ve a tu proyecto en Railway: **max-pain-analysis-public**
2. Click en **+ New Service**
3. Selecciona **GitHub Repo** (elige el mismo repositorio)
4. Name: `api` o `backend`
5. Click **Deploy**

### Paso 2: Configurar Variables de Entorno del Backend

Para el servicio **api** (nuevo):

```
POLYGON_API_KEY = 1749f7f5-66eb-47ae-9c7e-bf8110d04d55
TRADIER_API_KEY = (tu clave)
FMP_API_KEY = (tu clave)
API_PORT = 8000
```

El servicio web (Streamlit) necesita:

```
API_BACKEND_URL = (URL del backend - ver abajo)
PORT = 8501
```

### Paso 3: Obtener URL del Backend

1. Deploy el servicio **api**
2. Ve a su configuración → Domain
3. Copia la URL (ejemplo: `https://max-pain-analysis-api-production.up.railway.app`)
4. Configura en el servicio **web**:
   - `API_BACKEND_URL = https://max-pain-analysis-api-production.up.railway.app`

### Paso 4: Configurar el Procfile

El `Procfile` ya está configurado:

```
api: python -m uvicorn api_backend:app --host 0.0.0.0 --port $API_PORT
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

Railway automáticamente:
- Ejecutará el comando `api` para el servicio backend
- Ejecutará el comando `web` para el servicio frontend

### Paso 5: Verificar Conectividad

Después de deployar ambos servicios:

1. Backend: Visita `https://tu-backend-url.up.railway.app/health`
   - Deberías ver:
   ```json
   {
     "status": "healthy",
     "timestamp": "2025-12-03T...",
     "apis": {
       "polygon": "configured",
       "tradier": "configured",
       "fmp": "configured"
     }
   }
   ```

2. Frontend: Visita tu app Streamlit
   - Las Tabs deberían cargar correctamente
   - Los precios deberían mostrar sin errores

## 🔗 Variables de Entorno Completas

### Servicio Backend (`api`)

```
# Obligatorias
POLYGON_API_KEY=1749f7f5-66eb-47ae-9c7e-bf8110d04d55
TRADIER_API_KEY=<tu_tradier_key>
FMP_API_KEY=<tu_fmp_key>

# Opcional
API_PORT=8000
```

### Servicio Frontend (`web`)

```
# Conexión al backend (CRÍTICA)
API_BACKEND_URL=https://max-pain-analysis-api-production.up.railway.app

# Para Streamlit
PORT=8501

# Opcional (para otras funcionalidades)
KRAKEN_API_KEY=<tu_kraken_key>
KRAKEN_PRIVATE_KEY=<tu_kraken_private_key>
FINVIZ_API_KEY=<tu_finviz_key>
```

## ⚡ Flujo de Datos

```
Usuario → Streamlit App (web)
           ↓
           api_client.get_current_price("SPY")
           ↓
           HTTP GET http://backend:8000/api/price/SPY
           ↓
FastAPI Backend (api)
  ├─ Try Polygon API
  ├─ Fallback to Tradier
  └─ Fallback to FMP
           ↓
           JSON Response
           ↓
           Streamlit muestra el precio
```

## 🧪 Testing Local (Antes de Deploy)

```bash
# Terminal 1: Backend
export POLYGON_API_KEY=1749f7f5-66eb-47ae-9c7e-bf8110d04d55
export TRADIER_API_KEY=<tu_key>
export FMP_API_KEY=<tu_key>
python -m uvicorn api_backend:app --host 0.0.0.0 --port 8000

# Terminal 2: Frontend (en otra ventana)
export API_BACKEND_URL=http://localhost:8000
streamlit run app.py
```

## 🐛 Troubleshooting

### "Unable to fetch price from any API"

1. Verifica que el backend está corriendo
2. Verifica `API_BACKEND_URL` en Streamlit
3. Revisa los logs del backend: `GET /health` debe retornar `"status": "healthy"`

### "Connection refused" entre Streamlit y Backend

1. Asegúrate que ambos servicios están deployed en Railway
2. Usa la URL completa del backend (https://..., no localhost)
3. Verifica firewall/CORS (ya configurado en FastAPI)

### Backend returns 403/401

1. Verifica que las API keys están correctas en Railway
2. Polygon key es la más importante (real-time quotes)
3. Revisa logs en Railway → Deployments → Build Logs

## 📊 Monitoreo

Railway proporciona:
- **Logs**: Deployments → View Logs
- **Métricas**: Métricas de CPU, memoria, requests
- **Status**: Health checks automáticos

Revisa regularmente los logs de ambos servicios para asegurar que están funcionando.

## 🔄 Updates Futuros

Si necesitas agregar más endpoints al backend:

1. Edita `api_backend.py`
2. Agrega el endpoint
3. Edita `api_client.py` con el cliente correspondiente
4. Edita `app.py` para usar `api_client.metodo_nuevo()`
5. Push a GitHub
6. Railway redeploya automáticamente

¡No necesitas tocar Railways setting nuevamente!
