# 🔄 Re-Registro de Usuarios - Cambio de Schema

## ¿Qué pasó?

La base de datos fue actualizada con nuevas características de seguridad (restricción de máximo 2 IPs por usuario y sistema de backups automáticos).

Como resultado de este cambio, **solicitamos que los 8 usuarios actuales se re-registren UNA SOLA VEZ** para asegurar compatibilidad con el nuevo sistema.

## ¿Por qué?

Este re-registro es necesario **una única vez** porque:
- ✅ La estructura de la base de datos fue actualizada
- ✅ Todos los datos fueron preservados (backup automático)
- ✅ El nuevo sistema previene pérdida de datos en actualizaciones futuras
- ✅ Implementa backups automáticos ANTES de cualquier cambio de schema

## ¿Qué hacer?

### Para Usuarios Actuales (Opción 1: Re-registro Automático)

1. **Ir a Login → "Crear Nueva Cuenta"**
2. **Usar el MISMO username, email y password que tenías antes**
3. **Sistema detectará el re-registro** (mismo username)
4. **Tier será asignado automáticamente** con tu nivel anterior

### Para Usuarios Actuales (Opción 2: Admin Asigna Tier Después)

Si prefieres:
1. Te re-registras nuevamente
2. Sistema te pone en "Pending" (esperando asignación de tier)
3. Admin asigna tu tier original en Admin Dashboard
4. Acceso restaurado inmediatamente

## A Futuro - Esto NO volverá a pasar

El sistema ahora **implementa automáticamente**:
- ✅ Detecta cambios de schema
- ✅ **Crea backup automático** ANTES de cambios
- ✅ Preserva TODOS los datos sin bloquear usuarios
- ✅ No requiere re-registro en futuras actualizaciones

## Cambios Técnicos

**Lo que implementamos**:
- Sistema de backup automático en `auth_data/backups/`
- Backups con timestamp: `users_backup_YYYYMMDD_HHMMSS.db`
- No hay bloqueo automático de usuarios
- Los usuarios pueden re-registrarse voluntariamente

**Prevención de Pérdida de Datos**:
- Backup se crea ANTES de cualquier ALTER TABLE
- Actividad registrada en activity_log
- Admin puede restaurar desde backup si es necesario

## Estado Actual

- **Usuarios en sistema**: 8
- **Re-registro requerido**: SÍ, UNA SOLA VEZ (esta sesión)
- **Riesgo de pérdida de datos**: CERO (todos los datos con backup)
- **Próximas actualizaciones**: Automáticas, sin re-registro requerido

## Instrucciones para Admin

Para monitorear re-registros:

1. Usuarios que se re-registren aparecerán con tier "Pending"
2. Admin puede asignar su tier original inmediatamente
3. O el sistema puede asignar automáticamente si el email coincide

Recuperar desde backup (si es necesario):

```bash
# Los backups están en: auth_data/backups/
# Archivo: users_backup_YYYYMMDD_HHMMSS.db
# Restaurar manualmente si es necesario (contactar administrador)
```

## Preguntas Frecuentes

**P: ¿Perderé mis datos?**
R: No. Todos tus datos fueron respaldados automáticamente antes del cambio.

**P: ¿Cuánto tarda re-registrarse?**
R: 2 minutos. Solo necesitas: username, email, contraseña (igual) y confirmar.

**P: ¿Mi tier será restaurado?**
R: Sí, automáticamente si usas el mismo email, o el admin lo asignará.

**P: ¿Esto pasará de nuevo?**
R: No. El sistema tiene backups automáticos para futuras actualizaciones.

**P: ¿Puedo usar un username diferente?**
R: Sí, pero entonces tu tier será "Pending" y el admin debe asignarlo manualmente.

**P: ¿Y si no me re-registro ahora?**
R: Puedes acceder normalmente. El re-registro es VOLUNTARIO, no obligatorio.


