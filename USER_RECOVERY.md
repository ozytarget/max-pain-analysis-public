# 🔄 Recuperación de Usuarios - Instrucciones

## ¿Qué pasó?

Cuando actualicé la base de datos para agregar columnas `ip1` y `ip2` (restricción de máximo 2 IPs por usuario), la estructura de la tabla cambió y se perdieron los usuarios anteriores.

## ¿Cómo recuperar los usuarios?

Tienes **2 opciones**:

### Opción 1: Recrearlos manualmente en la app
1. Ve a Login → Crear Nueva Cuenta
2. Registra cada usuario nuevamente con sus datos originales
3. Ve a Admin Dashboard → Manage Users → Assign Tier
4. Asigna el tier correcto a cada usuario

### Opción 2: Usar el script de migración (si tienes backup)

Si tienes un backup de los datos, ejecuta:

```bash
python migrate_users.py
```

El script buscará automáticamente un backup de la tabla anterior y la migrará.

## ¿Cómo evitar esto en el futuro?

Para futuras migraciones de base de datos, el sistema ahora:

1. ✅ Crea un backup automático (`users_backup`)
2. ✅ Preserva los datos existentes
3. ✅ Agrega nuevas columnas sin perder información

## Lista de usuarios que tenías

Por favor proporciona los 8 usuarios que tenías:

- Usuario 1: ___________________
- Usuario 2: ___________________
- Usuario 3: ___________________
- Usuario 4: ___________________
- Usuario 5: ___________________
- Usuario 6: ___________________
- Usuario 7: ___________________
- Usuario 8: ___________________

Con esta información, puedo:
1. Insertarlos directamente en la BD
2. O proporcionar un comando para recuperarlos automáticamente

## Script rápido para agregar usuarios

Si tienes los datos, edita `migrate_users.py` y cambia:

```python
USERS_TO_RESTORE = [
    # (username, email, password, tier, days_valid)
    ("user1", "user1@email.com", "password123", "Pro", 365),
    ("user2", "user2@email.com", "password456", "Premium", 365),
    # ... agregar el resto
]
```

Luego ejecuta:
```bash
python migrate_users.py
```

## Estado actual

- **Usuarios en BD**: 0 (Pending)
- **Nueva estructura**: ✅ Con columnas ip1, ip2
- **Datos antiguos**: ⚠️ Necesitan ser recuperados

---

**Próximos pasos:**
1. Proporciona la lista de 8 usuarios
2. Insértalos nuevamente (opción 1 o 2)
3. Verifica en Admin Dashboard que aparezcan

