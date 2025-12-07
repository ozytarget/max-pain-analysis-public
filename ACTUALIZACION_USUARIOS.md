# 📊 ¿Qué Pasa con los Usuarios Cuando Actualizas la App?

## Respuesta Corta: ✅ **NO SE RESTABLECEN** 

Los usuarios **NO se pierden nunca** cuando actualizas la aplicación porque están almacenados en una **base de datos SQLite persistente**, no en la memoria de Streamlit.

---

## Arquitectura de Almacenamiento de Usuarios

### 1. **Base de Datos SQLite (Persistente)**
```
auth_data/
├── users.db              ← 🔒 BASE DE DATOS PRINCIPAL
├── backups/              ← 🔐 BACKUPS AUTOMÁTICOS
│   ├── users_backup_20251207_120000.db
│   ├── users_backup_20251207_130000.db
│   └── ...
└── sessions.json         ← Tokens de sesión
```

### 2. **Datos Almacenados Permanentemente**
Cada usuario tiene:
- ✅ **Username** - Nombre de usuario (ÚNICO)
- ✅ **Email** - Correo electrónico (ÚNICO)
- ✅ **Password Hash** - Contraseña cifrada con bcrypt
- ✅ **Tier** - Plan de usuario (Free, Pro, Premium, Pending)
- ✅ **Created Date** - Fecha de creación
- ✅ **Expiration Date** - Vencimiento de licencia
- ✅ **Daily Limit** - Límite de uso diario
- ✅ **Usage Today** - Uso hoy
- ✅ **Active Status** - Si está activo o no
- ✅ **IP Addresses** - Últimas IPs de acceso

---

## Flujo de Actualización Segura

```
┌─────────────────────────────────────────────────────┐
│ 1. Haces cambios en app.py (UI, features, etc)      │
│    ❌ ESTO NO AFECTA LOS USUARIOS                   │
└─────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│ 2. Commiteas cambios a GitHub                        │
│    ❌ Los usuarios siguen en la BD                  │
└─────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│ 3. Streamlit recarga la app                          │
│    ✅ BD SQLite se abre nuevamente                  │
└─────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│ 4. Al hacer login, app consulta la BD               │
│    ✅ TODOS los usuarios existen todavía            │
└─────────────────────────────────────────────────────┘
```

---

## Casos de Actualización

### ✅ CASO 1: Actualización Normal de Features
```python
# Cambias la UI, añades nuevas funcionalidades
git add app.py
git commit -m "Nueva feature X"
git push

# RESULTADO:
# ✅ Usuarios intactos
# ✅ Pueden hacer login con sus credenciales
# ✅ Sus tiers se mantienen
# ✅ Su uso se mantiene
```

### ✅ CASO 2: Actualización de Cambios en Funciones de Auth
```python
# Cambias user_management.py o funciones de autenticación
git add user_management.py
git commit -m "Mejoras en autenticación"
git push

# RESULTADO:
# ✅ Usuarios intactos en la BD
# ✅ Nuevas funcionalidades aplican
# ✅ NO se pierde historial de usuarios
```

### ✅ CASO 3: Cambios en Base de Datos (Nuevas Columnas)
```python
# Necesitas agregar un campo nuevo a usuarios
# El código automáticamente:

1. DETECTA que la schema cambió
2. CREA UN BACKUP automático
3. AGREGA la columna nueva
4. PRESERVA todos los datos existentes

# RESULTADO:
# ✅ Backup guardado en: auth_data/backups/users_backup_TIMESTAMP.db
# ✅ Todos los usuarios conservan sus datos
# ✅ Pueden hacer login sin problemas
```

---

## Protección de Datos en Actualización

### 🔄 Sistema de Backups Automático

Cuando ocurren cambios en la estructura de la base de datos:

```python
# En user_management.py - initialize_users_db()

if table_exists and schema_changed:
    # 1. CREAR BACKUP PRIMERO
    backup_file = f"auth_data/backups/users_backup_{timestamp}.db"
    shutil.copy2(USERS_DB, backup_file)  # ✅ Copia completa de seguridad
    
    # 2. LUEGO aplicar cambios
    c.execute("ALTER TABLE users ADD COLUMN new_column TEXT DEFAULT ''")
    conn.commit()
```

---

## Lo Que NO se Restablece

| Elemento | ¿Se Restablece? | Por Qué |
|----------|-----------------|---------|
| **Usuarios Registrados** | ❌ NO | Almacenados en SQLite |
| **Contraseñas** | ❌ NO | Hasheadas en BD, nunca se pierden |
| **Tiers de Usuario** | ❌ NO | Persistidos en BD |
| **Historial de Uso** | ❌ NO | Activity log en BD |
| **Sesiones Activas** | ⚠️ SÍ* | Se limpian al recargar (normal) |
| **Cache de Memoria** | ⚠️ SÍ* | Se limpia al recargar (normal) |

*Las sesiones y cache de memoria se limpian, pero eso es NORMAL - los usuarios simplemente vuelven a hacer login

---

## Qué Ocurre Cuando Recargas la App

### ANTES (mientras la app estaba corriendo)
```
st.session_state = {
    "authenticated": True,
    "current_user": "username",
    "session_token": "abc123xyz"
}
```

### DESPUÉS (cuando actualizas y Streamlit recarga)
```
# Memoria borrada (normal en Streamlit)
st.session_state = {} 

# PERO en la BD sigue existiendo:
usuarios.db:
  - username: "username"
  - password_hash: "$2b$12$..."
  - tier: "Pro"
  - active: 1
```

### El Usuario Hace Login Nuevamente
```
1. Usuario ve pantalla de Login
2. Ingresa credenciales
3. App verifica en BD
4. ✅ Usuario autenticado nuevamente
5. Nueva sesión creada
```

---

## Flujo Real de Autenticación

```
┌──────────────────────────────┐
│   Usuario hace login         │
└──────────────────────────────┘
            ↓
┌──────────────────────────────────────────┐
│ authenticate_user(username, password)    │
│ (from user_management.py)                │
└──────────────────────────────────────────┘
            ↓
┌──────────────────────────────────────────┐
│ Abre conexión a: auth_data/users.db      │
│ SELECT * FROM users WHERE username = ?   │
└──────────────────────────────────────────┘
            ↓
┌──────────────────────────────────────────┐
│ ✅ Verifica bcrypt.checkpw()             │
│    (contraseña está en disco)            │
└──────────────────────────────────────────┘
            ↓
┌──────────────────────────────────────────┐
│ ✅ Login exitoso                         │
│ Crea token de sesión                     │
│ Actualiza st.session_state               │
└──────────────────────────────────────────┘
```

---

## Escenarios de Actualización

### Escenario 1: Actualización Normal (99% de casos)
```
git push → Streamlit recarga app.py → Usuarios pueden hacer login
✅ Totalmente seguro
```

### Escenario 2: Cambio en Estructura de BD
```
Agregar columna nueva → Sistema detecta → Backup automático
→ Cambio aplicado → Usuarios intactos
✅ Totalmente seguro
```

### Escenario 3: Cambio en Funciones de Auth
```
Editar user_management.py → Nuevo código carga → BD sigue igual
→ Usuarios autentica con nueva lógica
✅ Totalmente seguro
```

### Escenario 4: Eliminar BD Manualmente (⚠️ PELIGRO)
```
❌ rm auth_data/users.db  ← NO HAGAS ESTO
→ Todos los usuarios se pierden
→ Pero tienes backup en: auth_data/backups/
→ Puedes restaurar: cp backups/users_backup_TIMESTAMP.db users.db
```

---

## Resumen de Seguridad

| Aspecto | Estado | Garantía |
|--------|--------|-----------|
| **Datos de Usuarios** | 🔒 SEGURO | SQLite persistente |
| **Backups Automáticos** | 🔄 ACTIVOS | Cada cambio de schema |
| **Contraseñas** | 🔐 HASHEADAS | bcrypt (irreversible) |
| **Tiers/Acceso** | ✅ PRESERVADO | En BD |
| **Sesiones** | ⚠️ TEMPORAL | Se renuevan al login |
| **Actualización de App** | ✅ SEGURA | No afecta BD |

---

## Lo Mejor del Diseño Actual

✅ **Persistencia Total**: BD en disco, no en memoria
✅ **Backups Automáticos**: Protección antes de cambios
✅ **Sin Pérdida de Datos**: Usuarios NUNCA se restablecen
✅ **Escalable**: SQLite maneja 1000s de usuarios sin problemas
✅ **Secure**: Bcrypt + hash de passwords
✅ **Versionado**: Activity log de todas las acciones

---

## Recomendaciones de Buenas Prácticas

### ✅ SEGURO DE HACER
```bash
git push                          # Actualizar app
git add user_management.py        # Cambiar auth
git add requirements.txt          # Agregar paquetes
streamlit run app.py              # Recargar app
```

### ⚠️ VERIFICAR ANTES DE HACER
```bash
# Si cambias la estructura de BD, asegúrate que:
# 1. El backup se crea
# 2. El change es no-destructivo (agregar, no eliminar)
# 3. Los datos existentes se preservan
```

### ❌ NO HAGAS
```bash
rm auth_data/users.db             # Elimina usuarios (pero hay backup)
rm -rf auth_data/                 # Elimina TODO (muy peligroso)
```

---

## Conclusión

**Los usuarios NO se restablecen NUNCA** cuando actualizas la app porque:

1. ✅ Están en SQLite (disco), no en memoria
2. ✅ Las actualizaciones no tocan la BD
3. ✅ Si hay cambios en BD, se crea backup automático
4. ✅ Sistema de autenticación siempre consulta la BD

**Es completamente seguro actualizar la app cuantas veces quieras** - los usuarios siempre estarán ahí. 🚀
