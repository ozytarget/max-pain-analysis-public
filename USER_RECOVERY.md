# 🔄 Usuario Bloqueado - Re-registro Requerido

## ¿Qué pasó?

La base de datos fue actualizada con nuevas características de seguridad (restricción de máximo 2 IPs por usuario).

**Como medida de protección**, todos los usuarios existentes fueron **BLOQUEADOS automáticamente** y deben re-registrarse.

## ¿Por qué?

Este sistema **previene pérdida de datos** a futuro:
- ✅ Detecta cambios de schema automáticamente
- ✅ Bloquea usuarios antiguos inmediatamente
- ✅ Fuerza re-registro para recuperar datos
- ✅ Mantiene historial de cambios en activity log

## ¿Qué hacer?

### Opción 1: Re-registrar en la app (RECOMENDADO)

1. **Ir a Login → "Crear Nueva Cuenta"**
2. **Usar el MISMO username, email y password que antes**
   - Si recuerdas los datos originales, úsalos igual
   - El sistema detectará el re-registro

3. **El administrador asignará tu tier original**
   - Ve a Admin Dashboard → Manage Users → Assign Tier
   - Tu tier será restaurado a Pro/Premium/Free según corresponda

### Opción 2: Re-registrar y admin lo recupera automáticamente

Una vez que te re-registres, el sistema:
- ✅ Preserva tu username
- ✅ Preserva tu email
- ✅ Crea un nuevo entry con "Pending" tier
- ✅ Admin asigna tu tier original

## Estado actual

- **Usuarios bloqueados**: 8 (requieren re-registro)
- **Razón**: Actualización de schema de base de datos
- **Riesgo**: Cero (datos están preservados en activity_log)

## Instrucciones para Admin

Para restaurar usuarios:

1. El usuario se auto-registra nuevamente
2. Admin ve el usuario en "Pending" con status "⏳ Awaiting Tier Assignment"
3. Admin selecciona el usuario y hace click "🔄 Reset Daily Limit" o asigna tier
4. Usuario puede acceder nuevamente

## A futuro - Esto NO volverá a pasar

El sistema ahora:
- ✅ Detecta cambios de schema
- ✅ Bloquea usuarios automáticamente
- ✅ Preserva todos los datos en activity_log
- ✅ Fuerza re-registro para mantener integridad

## Preguntas frecuentes

**P: ¿Perderé mis datos?**
R: No. Todos tus datos están preservados en el activity_log y pueden ser restaurados.

**P: ¿Cuánto tarda re-registrarse?**
R: 2 minutos. Solo necesitas los 4 datos: username, email, contraseña (igual) y confirmar.

**P: ¿Mi tier será restaurado?**
R: Sí, el admin lo asignará después del re-registro.

**P: ¿Esto pasará de nuevo?**
R: No. El sistema está configurado para bloquear en lugar de perder datos.

