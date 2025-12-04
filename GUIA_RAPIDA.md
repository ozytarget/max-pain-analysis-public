# 🚀 GUÍA RÁPIDA - PRO SCANNER

**Estado:** ✅ Sistema Operativo  
**Última Auditoría:** 2025-12-04  

---

## 👑 PARA TI (Master/Admin)

### Acceso Rápido
```
1. URL: https://ozy.up.railway.app
2. Tab: "Login"
3. Password: zxc11ASD
4. Enter
5. ✅ Admin Dashboard abierto
```

### Lo que puedes hacer:

#### Estadísticas (Dashboard)
- Ver usuarios activos totales
- Ver distribución (Free/Pro/Premium)
- Ver total de logins

#### All Users (Tab 1)
```
Tabla con:
- Username, Email, Tier, Fechas, Uso, Estado
- Buttons para cada usuario:
  - Reset Daily Limit (reinicia contador del día)
  - Change Tier (cambiar de Free a Pro a Premium)
  - Deactivate (bloquear usuario)
```

#### Activity Log (Tab 2)
```
Historial de:
- Quién entró (username)
- Cuándo (timestamp)
- Desde dónde (IP address)
- Qué hizo (action)
```

#### Admin Tools (Tab 3)
```
Herramientas:
- Extend License (agregar días)
- Assign Unlimited Access (dar acceso ilimitado)
```

---

## 👥 PARA LOS USUARIOS

### 1️⃣ Primer acceso (Registrarse)

```
PASO 1: Tab "Registrarse"
        └─ Llenar formulario:
           - Username: su usuario único
           - Email: su email
           - Password: mínimo 6 caracteres
           - Confirmar Password
           - Plan: Free/Pro/Premium (elegir)

PASO 2: Click "Registrarse"
        └─ Cuenta creada ✅

PASO 3: Tab "Login"
        └─ Entrar con username + password

PASO 4: ✅ Acceso al sistema
```

### 2️⃣ Logins siguientes

```
PASO 1: Tab "Login"
PASO 2: Username + Password
PASO 3: ✅ Acceso
```

### Limitaciones según plan

| Plan | Scans/Día | Duración | 
|------|-----------|----------|
| Free | 10 | 30 días |
| Pro | 100 | 365 días |
| Premium | 999 | 365 días |

**¿Alcanzaste límite?** Espera a mañana o contacta al admin.

---

## 🔄 FLUJO COMPLETO

```
USUARIO NUEVO:
├─ Va a URL
├─ Tab "Registrarse"
├─ Completa datos
├─ Elige plan
├─ Cuenta creada
├─ Tab "Login"
├─ Entramcedillas con username/password
└─ ✅ ACCESO

USUARIO EXISTENTE:
├─ Va a URL
├─ Tab "Login"
├─ Username + password
├─ Sistema valida
└─ ✅ ACCESO (si todo ok)

USUARIO BLOQUEADO:
├─ Va a URL
├─ Tab "Login"
├─ Entra credenciales
├─ Sistema rechaza (usuario deactivated)
└─ ❌ SIN ACCESO

USUARIO SIN CRÉDITO:
├─ Intentó scannear
├─ Llegó a su límite diario
├─ Espera a mañana (se resetea automáticamente)
└─ ✅ Próximo día: disponible de nuevo
```

---

## 🛡️ CONTRASEÑAS ANTIGUAS

**BLOQUEADAS PERMANENTEMENTE:**
- fabi125
- twmmpro
- sandrira1
- mark123
- nonu12
- mary123
- (y más...)

**Si alguien intenta:**
```
❌ Acceso denegado
📝 Mensaje: "Usa el nuevo sistema de registro"
📧 Debe registrarse en "Registrarse" tab
```

---

## ⚙️ TAREAS COMUNES PARA ADMIN

### Cambiar plan de usuario
```
1. Admin Panel
2. All Users tab
3. Select User
4. Click "Change Tier"
5. Elige nuevo plan
6. Guardar
```

### Reiniciar límite diario
```
1. Admin Panel
2. All Users tab
3. Select User (ej: juan que llegó a 100/100)
4. Click "Reset Daily Limit"
5. Vuelve a 0/100
```

### Bloquear usuario
```
1. Admin Panel
2. All Users tab
3. Select User
4. Click "Deactivate"
5. Usuario no entra más
```

### Extender expiración
```
1. Admin Panel
2. Tools tab
3. Extend License
4. Select User
5. Agregar días (ej: 30)
6. Click "Extend"
```

### Dar acceso ilimitado
```
1. Admin Panel
2. Tools tab
3. Assign Unlimited Access
4. Select User
5. Ingresar días (ej: 365)
6. Click "Assign Unlimited"
7. Usuario ahora: 999,999 scans/día
```

---

## 📊 MONITOREO

### Activity Log (verificar abuso)
```
1. Admin Panel
2. Activity Log tab
3. Ver quién entró, cuándo, desde dónde
4. Detectar:
   - Múltiples IPs = cuenta compartida?
   - Muchos logins = bot?
   - Patrón anormal = spam?
```

---

## 🚨 PROBLEMAS COMUNES

### Usuario dice: "No me deja entrar"
**Causas posibles:**
1. ❌ Contraseña antigua → Debe registrarse
2. ❌ Usuario no existe → Debe registrarse
3. ❌ Password incorrecta → Resetear o crear nueva
4. ❌ Licencia expirada → Admin: extend license
5. ❌ Deactivated → Admin: reactive user
6. ❌ Límite diario alcanzado → Esperar mañana o admin reset

### Usuario dice: "No puedo hacer más scans"
**Solución:**
1. Verificar si es:
   - End of day? → Esperar a mañana (auto-reset)
   - Licencia expirada? → Admin extend
   - Plan limitado? → Admin upgrade a Pro/Premium
2. O admin resetea manualmente

### Usuario intenta con contraseña antigua
**Resultado:**
- ❌ BLOQUEADO automáticamente
- 📝 Recibe mensaje claro
- 📧 Debe registrarse con nuevo sistema

---

## 📱 DETALLES TÉCNICOS

### Base de datos
```
Ubicación: auth_data/users.db
Tipo: SQLite3
Tablas: users, activity_log
Auto-creación: Sí (primer login)
```

### Credenciales admin
```
Email: ozytargetcom@gmail.com
Password: zxc11ASD
Método: Password directo (no email)
```

### Seguridad
```
Hashing: bcrypt
Niveles: 2 (master + usuarios)
Logging: Completo (activity_log)
Validación: Automática en cada login
```

---

## 📈 ESTADÍSTICAS ÚTILES

En Admin Dashboard ves:
```
- Total de usuarios activos
- Distribuidos por tier (Free/Pro/Premium)
- Total de logins del sistema
- Ayuda a entender uso y crecimiento
```

---

## 🎯 PRÓXIMOS PASOS

1. **Hoy:** Prueba el sistema
2. **Mañana:** Invita usuarios beta
3. **Semana:** Recolecta feedback
4. **Mes:** Ajusta límites según uso real

---

## 📞 SOPORTE RÁPIDO

| Problema | Solución | Tiempo |
|----------|----------|--------|
| Usuario no entra | Ver Activity Log + Reset | 2 min |
| Limit alcanzado | Admin Reset Daily | 1 min |
| Exp expirada | Admin Extend License | 1 min |
| Spam/Abuse | Admin Deactivate | 1 min |
| Upgrade plan | Admin Change Tier | 1 min |

---

## ✅ CHECKLIST DE OPERACIÓN

Antes de notificar a usuarios:

- [ ] Ingresé con zxc11ASD
- [ ] Admin Dashboard visible
- [ ] All Users tab funciona
- [ ] Activity Log visible
- [ ] Admin Tools accesible
- [ ] Creé test user
- [ ] Test user puede entrar
- [ ] Test user ve límites correctos
- [ ] Reset límite funciona
- [ ] Change tier funciona
- [ ] Activity log registra acciones
- [ ] Extend license funciona
- [ ] Assign unlimited funciona

---

**Sistema listo para producción ✅**

¡Bienvenido a PRO SCANNER!
