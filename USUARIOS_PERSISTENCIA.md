# 📊 Persistencia de Usuarios - Guía Completa

## ✅ Respuesta Directa: NO SE RESTABLECEN

Cuando actualizas la app, **los usuarios NO se pierden** porque están guardados en **SQLite en disco**, no en memoria de Streamlit.

---

## 🗂️ Estructura de Almacenamiento

```
auth_data/
├── users.db              ← ✅ BASE DE DATOS (PERSISTENTE EN DISCO)
├── backups/
│   ├── users_backup_20251207.db
│   └── users_backup_20251206.db
└── sessions.json         ← Sesiones activas
```

---

## 🔄 Qué Pasa en una Actualización

| Paso | Qué Sucede | Usuarios |
|------|-----------|----------|
| 1. Cambias app.py | Editas features, UI | ✅ Intactos |
| 2. Git push | Subes cambios a GitHub | ✅ Intactos |
| 3. Streamlit recarga | App se reinicia | ✅ BD se abre nuevamente |
| 4. Usuario hace login | Verifica credenciales en BD | ✅ Encuentra al usuario |

---

## 📊 Datos que Se Guardan PERMANENTEMENTE

```
✅ Username (ÚNICO)
✅ Email (ÚNICO)  
✅ Password Hash (bcrypt, cifrada)
✅ Tier (Free/Pro/Premium/Pending)
✅ Created Date (Fecha de registro)
✅ Expiration Date (Vencimiento)
✅ Daily Limit (Límite diario)
✅ Usage Today (Uso actual)
✅ Active Status (Si está activo)
✅ IP Addresses (Últimas IPs)
✅ Activity Log (Historial)
```

---

## 🛡️ Protecciones

### ✅ Backups Automáticos
- Se crean cuando hay cambios en la BD
- Guardados en `auth_data/backups/`
- Protege contra cambios accidentales

### ✅ Encryption
- Passwords hasheadas con bcrypt
- Irreversible - nunca se pierden

### ✅ Persistencia en Disco
- SQLite almacena en archivo físico
- Sobrevive recargas de Streamlit
- No depende de memoria RAM

---

## 📌 Lo Que SÍ Se Restablece (Normal)

- ⚠️ **Sesiones Activas** → Se limpian al recargar (usuario hace login nuevamente)
- ⚠️ **Cache en Memoria** → Se limpia (normal en Streamlit)

---

## 🚀 CONCLUSIÓN

```
✅ Es COMPLETAMENTE SEGURO actualizar la app
✅ Los usuarios NUNCA se pierden
✅ Puedes hacer push cuantas veces quieras
✅ Sistema está diseñado para proteger datos
```

---

## 📝 Ejemplo Real

### ANTES DE ACTUALIZACIÓN
```
Usuario "juan" en BD:
├── username: juan
├── email: juan@email.com
├── tier: Pro
└── created_date: 2025-12-01
```

### HACES GIT PUSH
```
app.py → GitHub → App recarga
```

### DESPUÉS DE ACTUALIZACIÓN
```
Usuario "juan" SIGUE en BD:
├── username: juan
├── email: juan@email.com  
├── tier: Pro              ← ✅ INTACTO
└── created_date: 2025-12-01  ← ✅ INTACTO

Usuario puede hacer login normalmente ✅
```

---

## 📚 Archivos Relacionados

- `user_management.py` - Sistema de usuarios (SQLite)
- `auth_data/users.db` - Base de datos actual
- `auth_data/backups/` - Copias de seguridad automáticas
- `ACTUALIZACION_USUARIOS.md` - Documentación detallada

---

**¡Puedes actualizar sin miedo! 🚀**
