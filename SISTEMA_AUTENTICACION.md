# 🔐 SISTEMA DE AUTENTICACIÓN PRO SCANNER

## 👑 TÚ COMO MASTER (OZYTARGETCOM@GMAIL.COM)

### Credenciales Admin
- **Email:** ozytargetcom@gmail.com
- **Password:** zxc11ASD
- **Acceso:** Admin Panel en la barra lateral (⚙️ Admin Panel)

### 🎛️ Tus Poderes Como Admin:

1. **Ver TODOS los usuarios** (All Users tab)
   - Lista completa de quién está registrado
   - Información: username, email, tier, fecha expiración, uso diario, estado

2. **Cancelar acceso a usuarios**
   - Botón "Deactivate" → Usuario no puede entrar más
   - Se registra la acción automáticamente

3. **Dar más crédito/escaneos**
   - **Reset Daily Limit:** Reinicia contador diario del usuario (para que pueda hacer más scans hoy)
   - **Extend License:** Agregar días de validez a una cuenta
   - **Assign Unlimited Access:** Dar acceso ILIMITADO (♾️) por X días

4. **Cambiar plan de usuario**
   - Cambiar de Free → Pro → Premium
   - Los límites diarios se actualizan automáticamente
   - Ejemplo: cambiar Free (10/día) a Premium (ilimitado)

5. **Ver Activity Log**
   - Historial de TODOS los logins
   - Quién entró, cuándo, desde qué IP
   - Útil para detectar compartir contraseñas

6. **Estadísticas en tiempo real**
   - Usuarios activos totales
   - Cuántos Free, Pro, Premium
   - Total de logins en el sistema

---

## 👥 LOS DEMÁS USUARIOS

### Paso 1: Registro
En la página de login:
1. Hacen clic en tab **"📝 Registrarse"**
2. Completan:
   - Username (único)
   - Email
   - Contraseña (mín 6 caracteres)
   - Confirmar contraseña
3. **Eligen su plan:**
   - 🆓 **Free** → 10 scans/día, válido 30 días
   - 💚 **Pro** → 100 scans/día, válido 365 días
   - 💛 **Premium** → Ilimitado, válido 365 días

### Paso 2: Login
1. Hacen clic en tab **"🔐 Login"**
2. Entran con username/contraseña nueva
3. ¡Acceso!

### Validaciones automáticas
- ✅ Si expiró la licencia → Bloqueado
- ✅ Si alcanzó límite diario → Bloqueado
- ✅ Si fue deactivado → Bloqueado
- ✅ Si tiene acceso → ¡Entra!

---

## 🛡️ CONTRASEÑAS ANTIGUAS

**TODAS las contraseñas antiguas están BLOQUEADAS:**
- fabi125, twmmpro, sandrira1, mark123, nonu12, mary123, etc.

Si alguien intenta entrar con contraseña antigua:
- ❌ Ve un mensaje diciéndole que use el nuevo sistema
- 📝 Se le redirige a que se registre

---

## 📊 FLUJO COMPLETO DEL SISTEMA

```
┌─────────────────────────────────────────────────────────┐
│         PRO SCANNER - PÁGINA DE AUTENTICACIÓN           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────┐      ┌──────────────────┐       │
│  │  🔐 Login Tab    │      │ 📝 Register Tab  │       │
│  ├──────────────────┤      ├──────────────────┤       │
│  │ Password entrada │      │ Username         │       │
│  │ (bloqueada si    │      │ Email            │       │
│  │  es antigua)     │      │ Password (6+ ch) │       │
│  │                  │      │ Confirm Password │       │
│  │ ↓                │      │ Tier Select      │       │
│  │ authenticate_    │      │ (Free/Pro/Prem) │       │
│  │ password()       │      │                  │       │
│  │ ↓                │      │ ↓                │       │
│  │ BLOQUEADO ❌     │      │ create_user()    │       │
│  │ o                │      │ ↓                │       │
│  │ ACCESO ✅        │      │ CUENTA CREADA ✅ │       │
│  └──────────────────┘      └──────────────────┘       │
│                                                         │
└─────────────────────────────────────────────────────────┘
                        ↓
            ┌───────────────────────┐
            │   USUARIO LOGUEADO    │
            ├───────────────────────┤
            │ - Acceso a 7 tabs     │
            │ - Scans diarios       │
            │ - Licencia válida     │
            └───────────────────────┘
```

---

## 🎯 CÓMO Texplosionas CON USUARIOS

### En el Admin Panel (⚙️ Admin Panel → All Users tab):

**Tabla de usuarios con acciones:**
```
Username  | Email              | Tier     | Exp Date   | Uso    | Acciones
----------|-------------------|----------|------------|--------|------------------
juan      | juan@email.com     | Pro      | 2025-12-15 | 45/100 | [Reset] [Tier] [Deact]
maria     | maria@email.com    | Free     | 2025-12-10 | 10/10  | [Reset] [Tier] [Deact]
pedro     | pedro@email.com    | Premium  | 2026-12-04 | 250/∞  | [Reset] [Tier] [Deact]
```

### ⚡ Acciones disponibles:

1. **Reset Daily Limit**
   - Usuario llegó a 100/100 → click → vuelve a 0/100
   - Puede hacer más scans hoy

2. **Change Tier**
   - Free → Pro → Premium
   - Ajusta límites automáticamente
   - Ejemplo: cambiar pedro de Pro a Premium (sin restricción)

3. **Deactivate User**
   - Usuario no puede entrar más
   - Puedes "reactivarlo" desde BD si quieres

4. **Extend License** (Admin Tools tab)
   - Usuario "juan" vence el 15 → agregar 30 días → vence el 14 enero
   - Ideal para clientes VIP

5. **Assign Unlimited Access** (Admin Tools tab)
   - Usuario "maria" → click "Assign Unlimited" → 365 días
   - Tier cambia a "Unlimited"
   - Límite: 999,999 scans/día (ilimitado prácticamente)

---

## 📈 ACTIVITY LOG

En Admin Panel → Activity Log tab:
- Ves TODOS los logins
- Quién entró, cuándo, desde qué IP
- Detectas si alguien comparte cuenta (misma IP múltiple?)

```
Username | Action      | Timestamp           | IP Address
---------|-------------|---------------------|----------------
juan     | login       | 2025-12-04 14:30:00 | 192.168.1.100
maria    | login       | 2025-12-04 14:31:15 | 203.45.67.89
juan     | login       | 2025-12-04 15:45:00 | 192.168.1.100
pedro    | deactivated | 2025-12-04 16:00:00 | admin
```

---

## 🔄 FLUJO COMPLETO DE UN USUARIO

### Usuario Nuevo:
```
1. Va a https://ozy.up.railway.app
2. Ve dos tabs: 🔐 Login | 📝 Registrarse
3. Elige tab Registrarse
4. Completa: username, email, password, elige plan (Free/Pro/Premium)
5. Click "✅ Registrarse"
6. Cuenta creada ✅
7. Recibe instrucción: "Ahora inicia sesión en tab 🔐 Login"
8. Va a tab Login
9. Entra con username/password
10. ¡ACCESO A LOS 7 TABS! 📊
```

### Usuario Nuevo pero sin credibilidad:
```
1. Intenta hacer spam/abuse
2. TÚ (admin) lo ves en All Users
3. Click "Deactivate"
4. ❌ Usuario bloqueado, no entra más
5. Puedes: reactivarlo después o dejarlo bloqueado
```

### Usuario VIP:
```
1. Está en Free (10/día)
2. Paga upgrade
3. TÚ en Admin → Change Tier → Premium
4. Automáticamente: límite → ilimitado, días → 365 nuevos
5. Usuario: "¿Qué cambió?" → Prueba y ve que puede hacer infinitos scans
```

### Usuario a punto de expirar:
```
1. Vence en 3 días
2. TÚ en Admin Tools → Extend License → 30 días
3. Expiration_date actualizado automáticamente
4. Usuario sigue teniendo acceso
```

---

## 🗄️ BASE DE DATOS

**Archivo:** `auth_data/users.db` (SQLite)

**Tabla: users**
```
id              | INTEGER (primary key)
username        | TEXT (único)
email           | TEXT (único)
password_hash   | TEXT (bcrypt hashed)
tier            | TEXT (Free/Pro/Premium/Unlimited)
created_date    | TEXT (ISO format)
expiration_date | TEXT (ISO format)
daily_limit     | INTEGER (10/100/999999)
usage_today     | INTEGER (scans hechos hoy)
last_reset      | TEXT (fecha último reset)
active          | BOOLEAN (True/False)
ip_address      | TEXT (última IP usada)
```

**Tabla: activity_log**
```
id        | INTEGER
username  | TEXT
action    | TEXT (login/deactivated/tier_changed/etc)
timestamp | TEXT
ip_address| TEXT
```

---

## 🔐 SEGURIDAD

✅ **Contraseñas hasheadas** con bcrypt (estándar industria)
✅ **Antiguas contraseñas bloqueadas** permanentemente
✅ **Licensing automático** - se valida en cada login
✅ **Activity logging** - auditoría de todos los logins
✅ **Admin autenticado** - solo tú (ozytargetcom@gmail.com) puedes acceder
✅ **IP tracking** - detección de abuso
✅ **Auto-reset diario** - límites se reinician cada día

---

## 📞 CONCLUSIÓN

**TÚ (Master):**
- Login: ozytargetcom@gmail.com / zxc11ASD
- Admin Panel: ⚙️ Admin Panel (sidebar)
- Controlas COMPLETAMENTE a todos los usuarios
- Puedes: resetear límites, cambiar planes, bloquear, extender licencias, dar acceso ilimitado

**Los demás:**
- Se registran en 📝 Registrarse
- Entran en 🔐 Login
- Reciben acceso según su plan
- No pueden usar contraseñas antiguas
- TÚ los monitorizas y controlas en todo momento

---

**Sistema 100% operativo y desplegado en Railway.app** ✅
