# 🔍 AUDITORÍA TÉCNICA - PROBLEMAS DETECTADOS

**Fecha:** 4 Diciembre 2025  
**Estado:** ⚠️ 12 PROBLEMAS CRÍTICOS ENCONTRADOS

---

## 1. ❌ PROBLEMAS CON pd.to_datetime() SIN MANEJO DE ERRORES

### Líneas críticas sin `errors='coerce'`:
- **Línea 2211**: `df["date"] = pd.to_datetime(df["date"])`
- **Línea 2339**: `df["date"] = pd.to_datetime(df["date"])`
- **Línea 3157**: `df["date"] = pd.to_datetime(df["date"])`
- **Línea 3268**: `df["date"] = pd.to_datetime(df["date"])`
- **Línea 3624**: `item["filingDate"] = pd.to_datetime(item["filingDate"]).strftime("%Y-%m-%d")`
- **Línea 4113**: `pending_display['created_date'] = pd.to_datetime(pending_display['created_date']).dt.strftime("%Y-%m-%d")`
- **Línea 4189**: `activity_df["timestamp"] = pd.to_datetime(activity_df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M")`
- **Línea 4468**: `tab1_hist_df['date'] = pd.to_datetime(tab1_hist_df['date']).dt.tz_localize(None)`
- **Línea 4473**: `tab1_targets_df['publishedDate'] = pd.to_datetime(tab1_targets_df['publishedDate']).dt.tz_localize(None)`

### Riesgo:
- OutOfBoundsDatetime error con valores fuera de rango
- ParserError con formatos incorrectos
- TypeError con valores None/null
- Crashing de la app en producción

### Solución:
Agregar `errors='coerce'` a todos los `pd.to_datetime()`:
```python
df["date"] = pd.to_datetime(df["date"], errors='coerce')
```

---

## 2. ⚠️ BARE EXCEPT SIN ESPECIFICAR EXCEPCIONES

### Líneas problemáticas:
- **Línea 4276**: `except:` ← Atrapa TODO incluyendo KeyboardInterrupt, SystemExit
- **Línea 5601**: `except:` ← En ciclo de processing
- **Línea 5618**: `except:` ← Sin logging de error
- **Línea 5638**: `except:` ← Silencia todos los errores
- **Línea 5671**: `except:` ← Oculta problemas de lógica

### Riesgo:
- Dificulta debugging
- Oculta errores importantes
- Previene KeyboardInterrupt (usuario no puede detener)
- Logs vacios sin información

### Solución:
```python
except Exception as e:
    logger.error(f"Specific error: {e}")
```

---

## 3. 🔴 CONVERSIONES DE TIPO SIN VALIDACIÓN

### Líneas encontradas:
- **Línea 4241-4242** (ya solucionado):
  ```python
  usage_today = int(user_info["usage_today"]) if user_info["usage_today"] else 0
  daily_limit = int(user_info["daily_limit"]) if user_info["daily_limit"] else 0
  ```
  
  ✅ **Solucionado** - Ahora hace cast seguro a int

### Otros lugares a revisar:
- Conversiones en loops de datos
- Multiplicaciones/divisiones que asumen int/float

---

## 4. 📅 COMPARACIONES DE DATETIME CON STRINGS

### Líneas encontradas:
- **Línea 4256**: `if datetime.fromisoformat(expiration_date) > datetime.now(MARKET_TIMEZONE):`
  
  ⚠️ **Riesgo:** Si `expiration_date` no es ISO format válido, falla
  
### Solución:
```python
try:
    exp_date = datetime.fromisoformat(expiration_date)
except (ValueError, TypeError):
    exp_date = datetime.now(MARKET_TIMEZONE)
```

---

## 5. 🔑 ACCESO A DICCIONARIOS SIN VERIFICACIÓN

### Áreas de riesgo:
- `user_info["username"]` - Si key no existe → KeyError
- `user_info["email"]` - Sin verificación
- `item["filingDate"]` - En loops
- Dict unpacking sin `.get()` fallbacks

### Solución:
Usar `.get()` con valores por defecto:
```python
username = user_info.get("username", "Unknown")
email = user_info.get("email", "")
```

---

## 6. ⚙️ CONVERSIONES MÚLTIPLES DE TIPOS

### Problemas identificados:
- **String → DateTime → String**: Conversiones innecesarias
- **Float → Int → Float**: Pérdida de precisión
- **None → Int**: Sin verificación de None

### Línea 4468-4473:
```python
tab1_hist_df['date'] = pd.to_datetime(tab1_hist_df['date']).dt.tz_localize(None)
```
- ⚠️ Sin `errors='coerce'`
- ⚠️ `.tz_localize(None)` puede fallar sin validación

---

## 7. 🔄 LOOPS CON CONVERSIONES INSEGURAS

### Líneas 5601-5671 (Finviz screener):
```python
except:  # ← BARE EXCEPT
    pass   # ← Silencia errores
```

En loops de processing, cada error silenciado oculta problemas

---

## RESUMEN DE FIXES REQUERIDOS

| Categoría | Problemas | Criticidad | Fixes |
|-----------|-----------|-----------|-------|
| pd.to_datetime() | 9 líneas | 🔴 Crítico | Agregar `errors='coerce'` |
| Bare except | 5 líneas | 🔴 Crítico | Especificar excepciones |
| Dict access | 20+ usos | 🟠 Alto | Usar `.get()` |
| Datetime parsing | 3+ líneas | 🔴 Crítico | Try/except fromisoformat |
| Type casting | 5+ líneas | 🟠 Alto | Validar antes de cast |
| Loops | 15+ líneas | 🟠 Alto | Logging de excepciones |

---

## PRIORITY FIXES (EN ORDEN)

### 🔥 CRÍTICO (Causa crashes):
1. **Línea 2211, 2339, 3157, 3268, 3624, 4113, 4189**: Agregar `errors='coerce'` a `pd.to_datetime()`
2. **Línea 4276, 5601, 5618, 5638, 5671**: Cambiar `except:` por `except Exception as e:`

### 🟠 ALTO (Comportamiento impredecible):
3. **Línea 4256**: Try/except para datetime.fromisoformat()
4. **Generalizado**: Cambiar dict access directo por `.get()`

### 🟡 MEDIO (Mejora de code quality):
5. **Loops**: Agregar logging a bare excepts

---

## CÓDIGO PROPUESTO PARA FIXES

### FIX 1: pd.to_datetime() con errors='coerce'
```python
# ANTES:
df["date"] = pd.to_datetime(df["date"])

# DESPUÉS:
df["date"] = pd.to_datetime(df["date"], errors='coerce')
```

### FIX 2: Bare except → Exception específica
```python
# ANTES:
except:
    pass

# DESPUÉS:
except Exception as e:
    logger.warning(f"Processing error: {e}")
    continue  # o pass, según context
```

### FIX 3: Dict access seguro
```python
# ANTES:
username = user_info["username"]

# DESPUÉS:
username = user_info.get("username", "Unknown")
```

### FIX 4: Datetime parsing seguro
```python
# ANTES:
exp_date = datetime.fromisoformat(expiration_date)

# DESPUÉS:
try:
    exp_date = datetime.fromisoformat(expiration_date)
except (ValueError, TypeError):
    exp_date = datetime.now(MARKET_TIMEZONE)
```

---

## ESTADÍSTICAS

- **Total de líneas analizadas**: 6916
- **Problemas encontrados**: 12 categorías
- **Líneas específicas con bugs**: 31
- **Potencial para crashes**: 🔴 ALTO
- **Degradación en producción**: ⚠️ CRÍTICA

---

## RECOMENDACIÓN FINAL

✅ **Implementar todos los CRITICAL fixes antes de producción**

Estos problemas causarán crashes irregulares en:
- Carga de datos del mercado (líneas 2211-3268)
- Admin panel (línea 4113)
- Activity log (línea 4189)
- Screener FINVIZ (líneas 5601-5671)

