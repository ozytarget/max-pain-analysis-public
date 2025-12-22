# 🎯 MM SCANNER - ESPECIFICACIÓN TÉCNICA INSTITUCIONAL

## FASE 0: DEFINICIÓN

### 1. UNIVERSO DE ACTIVOS
```
Base inicial:
- SPY (índice - referencia)
- QQQ (tech - volatilidad media)
- NVDA (mega cap - vol alta)
- TSLA (especulativa - vol extrema)
```

### 2. FUENTES DE DATOS REQUERIDAS
```
A. Options Chain (CRÍTICA)
   - Proveedor: Tradier API (ya tenemos)
   - Por contrato necesitamos:
     * Strike
     * IV (implied volatility)
     * Open Interest (OI)
     * Volume
     * Greeks: Delta, Gamma, Theta, Vega
     * Bid/Ask (spread)
   - Frecuencia: Real-time al hacer análisis

B. Price & Volume
   - Proveedor: Tradier / FMP
   - OHLCV diarios
   - Necesitamos histórico de 252 días mínimo

C. Noticias
   - Proveedor: Google News / RSS
   - Filtro: market-moving keywords
   - Timestamp crítico
   - Sentimiento básico (bullish/bearish)

D. Calendario
   - Earnings (cuando sea posible)
   - OPEX weeks
   - Macro events key
```

### 3. ALMACENAMIENTO (MEMORIA)
```
Estructura de datos central:

snapshots_table:
  id, ticker, timestamp, underlying_price, underlying_iv
  
contracts_table:
  snapshot_id, strike, type(call/put), iv, oi, volume
  delta, gamma, theta, vega, bid, ask

levels_table:
  snapshot_id, call_wall_strike, call_wall_oi, put_wall_strike, put_wall_oi
  pinning_score, regime(chop/trend/squeeze), gamma_flip_zone

news_table:
  ticker, timestamp, title, source, sentiment_score, impact_score

ticker_profile_table:
  ticker, stat_pinnig_hit_rate, stat_wall_respect, avg_vol_expansion
  behavior_notes (aprendido del backtest)
```

### 4. SALIDAS (MM BRIEF)
```
INPUT: ticker + timestamp

OUTPUT: JSON estructura fija

{
  "ticker": "SPY",
  "timestamp": "2025-12-21 14:30:00 ET",
  "snapshot": {
    "price": 587.23,
    "iv": 0.142,
    "put_call_ratio": 0.87
  },
  
  "walls": {
    "call_wall": {
      "strike": 590.00,
      "oi": 245000,
      "distance_pct": 0.47,
      "strength": "MEDIUM"
    },
    "put_wall": {
      "strike": 585.00,
      "oi": 198000,
      "distance_pct": -0.41,
      "strength": "MEDIUM"
    }
  },
  
  "regime": {
    "classification": "CHOP",
    "confidence": 0.78,
    "gamma_health": "POSITIVE",
    "pin_probability": 0.65,
    "vol_risk": "EXPANSION"
  },
  
  "targets": {
    "target_a": {"level": 590.50, "probability": 0.42, "invalidation": "breaks 591.50"},
    "target_b": {"level": 585.30, "probability": 0.38, "invalidation": "breaks 584.00"}
  },
  
  "news_impact": {
    "last_24h": [
      {"title": "...", "sentiment": "BEARISH", "impact": "HIGH"}
    ],
    "next_event": "FOMC (2 days)"
  },
  
  "ticker_profile": {
    "pin_hit_rate": 0.68,
    "wall_respect_rate": 0.72,
    "vol_expansion_frequency": 0.31,
    "notes": "SPY respeta walls más que NVDA"
  },
  
  "scenarios": {
    "bull": {"entry": "586.50", "target": "592.00", "stop": "584.00"},
    "bear": {"entry": "589.00", "target": "583.00", "stop": "591.00"},
    "chop": {"entry": "587.23", "range_low": "585.00", "range_high": "590.00"}
  }
}
```

### 5. ALGORITMOS PRINCIPALES

#### A. GEX (Gamma Exposure) y WALLS
```python
# Por cada strike y expiration:
gamma_exposure = sum(contracts.gamma * contracts.oi)
call_wall = max OI entre calls OTM
put_wall = max OI entre puts OTM

# Definición de "wall"
wall_significance = oi / mean(oi_nearby_strikes)
```

#### B. PINNING SCORE
```python
# Cuán probable es que el precio termine en/cerca de una wall?
pinning_score = function(
  distance_to_wall,      # más cerca = más probable
  wall_strength (oi),    # oi más alta = más gravedad
  gamma_sign,            # negativa = más "sticky"
  historical_pin_rate,   # ticker aprende
  vol_regime            # chop = más pinning
)
```

#### C. REGIME CLASSIFIER
```
CHOP: 
  - ATR bajo
  - Gamma positiva neta (mean reversion)
  - Precio oscila entre walls
  
TREND:
  - ATR alto / aceleración
  - Gamma negativa (fragilidad)
  - Precio rompe walls
  
SQUEEZE:
  - Bollinger Bands estrechas
  - IV baja
  - Expansión probable
```

#### D. TARGET CALCULATION
```
Basado en:
1. Wall locations (imanes naturales)
2. ATR / rangos históricos
3. IV term structure (dónde se mueve más)
4. Estadística pura: cuantiles de movimiento
```

### 6. MÉTRICAS DE PRECISIÓN (Backtesting)
```
Por ticker, guardar:
- pin_hit_rate: % de veces que pinnea en wall
- wall_respect_rate: % veces que rebota en wall
- target_accuracy: % de targets acertados (± 1 ATR)
- regime_accuracy: % regimes correctamente clasificados
- false_signal_rate: % de señales falsa
```

---

## PHASE 1: MVP FUNCIONAL

### Módulos a construir:

**1. data_ingestion.py**
   - Descargar y parsear options chain
   - Guardar snapshots en SQLite
   - Histórico mínimo 30 días

**2. quant_engine.py**
   - Calcular GEX, walls, pinning, regime
   - Outputear MM Report JSON

**3. ai_layer.py**
   - Tomar JSON cuantitativo
   - Armar escenarios A/B/C
   - Explicar en texto (sin invención)

**4. memory.py**
   - Guardar outcomes (qué pasó vs predicción)
   - Calcular hit rates por ticker
   - Ajustar pesos

**5. ui.py (Tab refactorizado)**
   - Input: ticker
   - Output: walls + regime + scenarios + news + profile

---

## ENTREGABLES DE PHASE 1

✅ Snapshots guardados (30+ días histórico)
✅ GEX + Wall detection funcional
✅ Pinning score + regime classifier
✅ MM Report JSON completo
✅ AI que explica (sin alucinaciones)
✅ Ticker profiles con hit rates
✅ UI limpia y funcional

---

## TIMELINE REALISTA

**Week 1**: Data ingestion + DB schema (3-4 días)
**Week 2**: Quant engine (GEX, walls, regime) (3-4 días)
**Week 3**: AI layer + memory (2-3 días)
**Week 4**: UI refactor + testing (2-3 días)

**Horas totales**: ~100-120 horas de coding real
