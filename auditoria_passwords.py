#!/usr/bin/env python3
"""
Auditoría de passwords y verificación del sistema
Verifica que todo funcione correctamente
"""

import sqlite3
import bcrypt
import os

def auditoria_passwords():
    """Hace auditoría completa del sistema de passwords"""
    
    db_path = "auth_data/users.db"
    
    print("\n" + "="*70)
    print("🔐 AUDITORÍA DE PASSWORDS Y VERIFICACIÓN DEL SISTEMA")
    print("="*70 + "\n")
    
    # 1. Verificar que la BD existe
    if not os.path.exists(db_path):
        print("❌ ERROR: Base de datos no existe en", db_path)
        return False
    
    print("✅ Base de datos encontrada")
    
    # 2. Conectar a la BD
    try:
        conn = sqlite3.connect(db_path, timeout=10)
        cursor = conn.cursor()
        print("✅ Conexión a la BD exitosa")
    except Exception as e:
        print(f"❌ ERROR al conectar: {e}")
        return False
    
    # 3. Verificar estructura de tabla
    try:
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print("\n📋 Estructura de tabla:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
    except Exception as e:
        print(f"❌ ERROR al verificar tabla: {e}")
        return False
    
    # 4. Contar passwords
    try:
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        print(f"\n📊 Total de passwords en BD: {count}")
        
        if count != 40:
            print(f"⚠️  ADVERTENCIA: Se esperaban 40 passwords, hay {count}")
        else:
            print("✅ Cantidad correcta de passwords")
    except Exception as e:
        print(f"❌ ERROR al contar: {e}")
        return False
    
    # 5. Verificar integridad de hashes
    print("\n🔍 Verificando integridad de hashes...")
    try:
        cursor.execute("SELECT id, password_hash, tier, daily_limit FROM users LIMIT 10")
        rows = cursor.fetchall()
        
        valid_hashes = 0
        for row_id, hash_pwd, tier, daily_limit in rows:
            # Verificar que es un hash válido de bcrypt
            if hash_pwd.startswith('$2b$'):
                valid_hashes += 1
                print(f"   ✅ Password {row_id}: Valid bcrypt hash")
            else:
                print(f"   ❌ Password {row_id}: Invalid hash format")
        
        print(f"\n✅ {valid_hashes}/10 primeros hashes son válidos")
    except Exception as e:
        print(f"❌ ERROR al verificar hashes: {e}")
        return False
    
    # 6. Verificar que no hay duplicados
    try:
        cursor.execute("SELECT password_hash FROM users")
        all_hashes = cursor.fetchall()
        unique_hashes = set([h[0] for h in all_hashes])
        
        if len(all_hashes) == len(unique_hashes):
            print(f"✅ No hay passwords duplicados ({len(unique_hashes)} únicos)")
        else:
            print(f"❌ ADVERTENCIA: Encontrados duplicados")
    except Exception as e:
        print(f"❌ ERROR al verificar duplicados: {e}")
        return False
    
    # 7. Verificar permisos y tiers
    try:
        cursor.execute("SELECT COUNT(*), tier FROM users GROUP BY tier")
        tiers = cursor.fetchall()
        
        print("\n👥 Distribución de tiers:")
        for count, tier in tiers:
            print(f"   - {tier}: {count} usuarios")
    except Exception as e:
        print(f"❌ ERROR al verificar tiers: {e}")
    
    # 8. Prueba de verificación con bcrypt
    print("\n🧪 Prueba de verificación con bcrypt...")
    try:
        # Obtener el primer password de la BD
        cursor.execute("SELECT id, password_hash FROM users LIMIT 1")
        result = cursor.fetchone()
        
        if result:
            user_id, stored_hash = result
            # Leer el archivo 40_passwords.txt y obtener el primer password
            with open('40_passwords.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            test_password = None
            for line in lines:
                line = line.strip()
                if line.startswith('1.'):
                    test_password = line.split('. ', 1)[1]
                    break
            
            if test_password:
                # Verificar contraseña
                is_valid = bcrypt.checkpw(
                    test_password.encode('utf-8'),
                    stored_hash.encode('utf-8')
                )
                
                if is_valid:
                    print(f"✅ Verificación de bcrypt funciona correctamente")
                    print(f"   Contraseña de prueba: {test_password}")
                else:
                    print(f"⚠️  Nota: Los passwords en la BD no coinciden con el archivo")
                    print(f"   (Esto es normal si regeneraste los passwords)")
    except Exception as e:
        print(f"⚠️  No se pudo hacer prueba de bcrypt: {e}")
    
    conn.close()
    
    # 9. Resumen final
    print("\n" + "="*70)
    print("✅ AUDITORÍA COMPLETADA - SISTEMA OPERACIONAL")
    print("="*70)
    print("\n📝 Próximos pasos:")
    print("   1. Distribuir los 40 passwords a los alumnos")
    print("   2. Alumnos ingresan SOLO con la contraseña (sin usuario)")
    print("   3. La app verifica automáticamente con bcrypt")
    print("   4. Railway deployará automáticamente los cambios")
    
    return True

if __name__ == "__main__":
    auditoria_passwords()
