# Max Pain Analysis - Backend API & Streamlit App

Arquitectura centralizada con FastAPI backend + Streamlit frontend.

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                   Railway Platform                       │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────┐          ┌──────────────────┐    │
│  │   FastAPI Backend│          │ Streamlit App    │    │
│  │   (Port: 8000)   │          │ (Port: 8501)     │    │
│  │                  │◄─────────►│                  │    │
│  │ • /api/price     │  HTTP    │ • Tab 1-9        │    │
│  │ • /api/prices    │          │ • Real-time data │    │
│  │ • /api/historical│          │                  │    │
│  │ • /api/options   │          │                  │    │
│  │ • /api/metrics   │          │                  │    │
│  │ • /api/volatility│          │                  │    │
│  └──────────────────┘          └──────────────────┘    │
│         ▲                              ▲                 │
│         │                              │                 │
│  ┌──────┴─────────────────────────────┴────────┐       │
│  │                                              │       │
│  ├─► Polygon (Real-time quotes)                │       │
│  ├─► Tradier (Options chains)                  │       │
│  └─► FMP (Financial metrics)                   │       │
│                                                 │       │
└─────────────────────────────────────────────────┘       │
```

## 🚀 Deployment en Railway

### 1. Crear Servicio del Backend

```bash
# En tu proyecto de Railway
# Add > Python Service
# Conecta tu repositorio GitHub

# Variables de entorno necesarias:
POLYGON_API_KEY=1749f7f5-66eb-47ae-9c7e-bf8110d04d55
TRADIER_API_KEY=<tu_key>
FMP_API_KEY=<tu_key>
KRAKEN_API_KEY=<tu_key>
KRAKEN_PRIVATE_KEY=<tu_key>
FINVIZ_API_KEY=<tu_key>
API_PORT=8000
```

### 2. Crear Servicio del Frontend

```bash
# Add > Python Service (mismo repositorio)
# Variables de entorno:
API_BACKEND_URL=http://api-backend-service:8000
PORT=8501
```

### 3. Conectar Servicios

- En Railway Dashboard → settings
- Link `api` service variable para que Streamlit pueda acceder

## 📝 Endpoints Disponibles

### Precios
```bash
GET /api/price/{ticker}
GET /api/prices?tickers=SPY,QQQ,AAPL
```

### Datos Históricos
```bash
GET /api/historical/{ticker}?days=30&period=daily
```

### Opciones
```bash
GET /api/expirations/{ticker}
GET /api/options/{ticker}/{expiration}
```

### Métricas
```bash
GET /api/metrics/{ticker}
GET /api/volatility/{ticker}?days=30
```

### Health Check
```bash
GET /health
```

## 🔄 Flujo de Datos

1. **Streamlit App** hace request a `api_client.get_current_price()`
2. **API Client** envía GET a `http://localhost:8000/api/price/SPY`
3. **FastAPI Backend**:
   - Intenta Polygon (real-time, mejor calidad)
   - Fallback a Tradier (reliable)
   - Fallback a FMP (fallback final)
4. **Respuesta** vuelve al frontend en formato JSON

## 🛡️ Ventajas de esta Arquitectura

✅ **Control Centralizado**: Una sola fuente de verdad para todas las llamadas a APIs  
✅ **Fallbacks Automáticos**: Si Polygon falla, automáticamente usa Tradier/FMP  
✅ **Cacheo Inteligente**: Redis/in-memory caching en el backend  
✅ **Seguridad**: Las API keys no se exponen al frontend  
✅ **Escalabilidad**: Puedes mover cada servicio a máquinas diferentes  
✅ **Mantenimiento**: Cambiar de proveedor solo requiere actualizar el backend  

## 🧪 Pruebas Locales

```bash
# Terminal 1: Backend
python -m uvicorn api_backend:app --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
export API_BACKEND_URL=http://localhost:8000
streamlit run app.py
```

## 📊 Monitoring

- Backend health: `GET http://api-backend:8000/health`
- Logs en Railway: Dashboard → Deployments → View Logs
- Errores: Si backend no responde, app usa fallbacks con warning en logs

## 🔑 Variables de Entorno (Producción)

Railway detectará automáticamente `API_PORT` si está configurado.  
Para Streamlit, configura `API_BACKEND_URL` para apuntar a tu backend en Railway.

Ejemplo:
```
API_BACKEND_URL=https://max-pain-analysis-api-production.up.railway.app
```

## 🎯 Próximos Pasos

1. Crear segundo servicio en Railway para el backend
2. Configurar variables de entorno en ambos servicios
3. Deploy y testing
4. Opcionalmente: Agregar Redis para cacheo distribuido
