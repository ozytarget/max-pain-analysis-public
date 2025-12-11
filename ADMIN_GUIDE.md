# 👨‍💼 ADMIN PANEL GUIDE - Pro Scanner

**Para Administradores Solo**

---

## 🔐 ACCESO AL ADMIN PANEL

### 1. Click en Tab: 🔐 ADMIN

```
Pro Scanner
📊 LOGIN     📝 REGISTER     🔐 ADMIN ← Click aquí
```

### 2. Ingresa tus credenciales:

| Campo | Valor |
|-------|-------|
| **Admin Email** | `ozytargetcom@gmail.com` |
| **Admin Password** | [Tu contraseña admin] |

### 3. Click: 🔐 ENTER ADMIN PANEL

---

## 👥 PANEL ADMINISTRATIVO (4 Pestañas)

```
📊 Users  │  📈 Statistics  │  ⚙️ Config  │  📋 Logs
```

---

## 📊 PESTAÑA 1: USERS MANAGEMENT

**Aquí administras todos los usuarios registrados.**

### Vista General:

```
┌─────────────────────────────────────────────────────┐
│ Username │ Email  │ Tier    │ Status │ Block │ Delete │
├─────────────────────────────────────────────────────┤
│ user123  │ u@mail │Premium  │ 🟢Act  │ 🔒   │ 🗑️    │
│ john_doe │ j@mail │Premium  │ 🔴Bloc │ 🔓   │ 🗑️    │
│ maria22  │ m@mail │Premium  │ 🟢Act  │ 🔒   │ 🗑️    │
└─────────────────────────────────────────────────────┘
```

### Información de cada usuario:

| Columna | Significado | Ejemplo |
|---------|-----------|---------|
| **Username** | Nombre de usuario | `john_doe` |
| **Email** | Correo registrado | `john@example.com` |
| **Tier** | Plan (Premium/Pro/Free) | `Premium` |
| **Status** | 🟢 Activo o 🔴 Bloqueado | `🟢 Activo` |
| **Block** | Botón para bloquear/desbloquear | 🔒 / 🔓 |
| **Delete** | Botón para eliminar usuario | 🗑️ |

---

## 🎮 ACCIONES DEL ADMIN

### 1. BLOQUEAR USUARIO (🔒)

**¿Cuándo usarlo?**
- Usuario spam
- Usuario malicioso
- Cuenta comprometida
- Usuario que incumple ToS

**Qué sucede:**
- Usuario NO puede hacer login
- Datos se guardan en BD
- Puedes desbloquear después

**Paso a paso:**
1. Encuentra usuario en la lista
2. Haz click 🔒 BLOQUEAR
3. Verás: ✅ "user123 bloqueado"
4. El usuario ahora tiene 🔴 Bloqueado
5. Cuando intente login: ❌ "Account is deactivated"

---

### 2. DESBLOQUEAR USUARIO (🔓)

**¿Cuándo usarlo?**
- Desbloqueaste por error
- Usuario arregló el problema
- Deseas permitir acceso nuevamente

**Qué sucede:**
- Usuario PUEDE hacer login de nuevo
- Recupera acceso instantáneamente

**Paso a paso:**
1. Encuentra usuario bloqueado (🔴)
2. Haz click 🔓 DESBLOQUEAR
3. Verás: ✅ "user123 desbloqueado"
4. El usuario ahora tiene 🟢 Activo
5. Puede hacer login de nuevo

---

### 3. ELIMINAR USUARIO (🗑️)

**¿Cuándo usarlo?**
- Cuenta duplicada
- Usuario solicita eliminación
- Cuenta de prueba/test
- Spam permanente

**⚠️ IMPORTANTE:** Esta acción es PERMANENTE

**Qué sucede:**
- Usuario ELIMINADO de BD completamente
- Datos NO pueden recuperarse
- Usuario NO puede hacer login más

**Paso a paso:**
1. Encuentra usuario en la lista
2. Haz click 🗑️ ELIMINAR
3. Verás: ✅ "user123 eliminado"
4. Usuario desaparece de lista
5. Usuario debe registrarse nuevamente si quiere acceso

---

## 📈 PESTAÑA 2: STATISTICS

**Estadísticas del sistema (informativo)**

Muestra:
- Total de usuarios registrados
- Usuarios activos
- Usuarios bloqueados
- Uso total de análisis por día

---

## ⚙️ PESTAÑA 3: CONFIG

**Configuración del sistema (avanzado)**

Permite:
- Cambiar límites diarios
- Ajustar tiers
- Configurar opciones globales

---

## 📋 PESTAÑA 4: LOGS

**Historial de actividad**

Muestra:
- Cuándo se registró cada usuario
- Cuándo hizo login
- Análisis realizados
- Cambios de admin

---

## 🔍 BÚSQUEDA DE USUARIOS

Para encontrar un usuario específico:

1. Usa Ctrl+F (en navegador)
2. Busca por username, email, o status
3. Sistema resalta el usuario

---

## 📊 ESTADÍSTICAS DE USUARIOS

### Ejemplo de información visible:

```
Total Usuarios: 47
├─ Activos: 43
├─ Bloqueados: 3
└─ Premium: 47 (100%)

Uso Diario Total: 1,234 análisis
```

---

## ⚠️ RESPONSABILIDADES DEL ADMIN

### HACER:
- ✅ Monitorear usuarios nuevos
- ✅ Bloquear/eliminar spam inmediatamente
- ✅ Responder inquietudes de usuarios
- ✅ Mantener logs de acciones
- ✅ Backup regular de BD

### NO HACER:
- ❌ Compartir credenciales admin
- ❌ Bloquear usuarios por "castigo"
- ❌ Cambiar contraseñas de usuarios
- ❌ Acceder a datos personales sin causa
- ❌ Dejar admin panel sin cerrar

---

## 🔐 PROTECCIONES INTEGRADAS

### El sistema automáticamente:

1. **Detecta 3+ IPs**
   - Usuario intenta acceso desde 3ª IP
   - ❌ Acceso DENEGADO automáticamente
   - Admin ve en logs

2. **Bloquea Contraseñas Legacy**
   - Usuario intenta con contraseña antigua
   - ❌ Login FALLIDO automáticamente
   - Protege si contraseña fue publicada

3. **Expira Licencias**
   - Usuario Premium después de 365 días
   - ❌ Acceso DENEGADO automáticamente
   - Admin puede extender en BD

4. **Valida Email Único**
   - 2 usuarios no pueden usar mismo email
   - Error: "Email already exists"
   - Previene cuentas duplicadas

---

## 🆘 PROBLEMAS COMUNES (ADMIN)

### ❓ "Database is locked"
**Causa:** Múltiples cambios simultáneos  
**Solución:** Espera 10 segundos, intenta de nuevo

### ❓ Usuario no aparece en lista
**Causa:** Cambios no refrescados  
**Solución:** Haz click F5 para recargar, o logout/login

### ❓ "Error deleting user"
**Causa:** Permisos insuficientes o BD corrupta  
**Solución:** Intenta de nuevo, chequea logs

### ❓ ¿Cómo cambio contraseña de usuario?
**Respuesta:** No puedes directamente. Usuario debe:
1. Contactarte
2. Tú eliminas su cuenta
3. Él se re-registra con contraseña nueva

---

## 📋 CHECKLIST DIARIO DE ADMIN

- [ ] Revisar usuarios nuevos de ayer
- [ ] Chequear si hay usuarios bloqueados
- [ ] Revisar logs de actividad
- [ ] Buscar patrones de spam
- [ ] Backup de BD (automático)
- [ ] Responder inquietudes de usuarios

---

## 📞 CONTACTO Y ESCALONAMIENTO

**Problema grave?** Contacta a:
- **Email:** [Super Admin Email]
- **Teléfono:** [Super Admin Phone]

**Reporta:**
- Ataque de spam masivo
- Intento de hack
- Datos corruptos en BD
- Errores críticos

---

## 🎯 MEJORES PRÁCTICAS

### 1. **Responde Rápido**
- Usuario spam/malicioso → Bloquea en minutos
- Usuario pregunta → Responde en horas

### 2. **Documenta Acciones**
- Por qué bloqueaste usuario X
- Cuándo fue la acción
- Si es reversible

### 3. **Mantén Privacidad**
- Respeta datos personales
- No compartas emails con otros
- Borrar logs antiguos regularmente

### 4. **Previene Problemas**
- Monitorea actividad sospechosa
- Bloquea antes de que sea problema grande
- Mantén BD optimizada

---

## 📊 MÉTRICAS A MONITOREAR

| Métrica | Umbral | Acción |
|---------|--------|--------|
| Usuarios Nuevos/Día | >20 | Revisa spam |
| Bloqueados | >5% | Investiga |
| Análisis/Día | <100 | Normal |
| Errores | >10/día | Debug |

---

## 🔐 SEGURIDAD DEL ADMIN PANEL

### Tu contraseña admin:
- ✓ NO compartas con nadie
- ✓ Cámbiala cada 90 días
- ✓ Usa contraseña fuerte (12+ caracteres)
- ✓ Cierra sesión cuando termines

### Acceso desde:
- ✓ Solo tu computadora
- ✓ Red privada/VPN
- ✗ Computadoras públicas
- ✗ Wifi público sin VPN

---

## 📚 DOCUMENTACIÓN RELACIONADA

- `SECURITY_AUDIT.md` - Detalles de seguridad
- `USER_REGISTRATION_GUIDE.md` - Guía para usuarios
- `SECURITY.md` - Políticas globales

---

**Versión:** 1.0  
**Actualizado:** 2025-12-11  
**Estado:** ✅ En Producción
