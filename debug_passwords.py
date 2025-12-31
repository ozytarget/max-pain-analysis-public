#!/usr/bin/env python3
"""
Debug: Verificar qué passwords están en la BD
y compararlos con el archivo
"""

import sqlite3
import bcrypt

def verificar_passwords_db():
    """Verifica qué passwords están realmente en la BD"""
    
    db_path = "auth_data/users.db"
    
    print("\n" + "="*70)
    print("🔍 DEBUG: COMPARAR PASSWORDS EN BD VS ARCHIVO")
    print("="*70 + "\n")
    
    # Leer archivo
    print("📋 Passwords en 40_passwords.txt:")
    try:
        with open('40_passwords.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        archivo_passwords = []
        for line in lines:
            line = line.strip()
            if line and '.' in line and len(line) > 3:
                pwd = line.split('. ', 1)[1]
                archivo_passwords.append(pwd)
        
        for i, pwd in enumerate(archivo_passwords[:5], 1):
            print(f"   {i}. {pwd}")
        print(f"   ... ({len(archivo_passwords)} total)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Conectar a BD
    print("\n🔐 Passwords en auth_data/users.db:")
    try:
        conn = sqlite3.connect(db_path, timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT id, password_hash FROM users LIMIT 5")
        db_users = cursor.fetchall()
        conn.close()
        
        print(f"   Encontrados {len(db_users)} primeros registros:")
        for uid, hash_pwd in db_users:
            print(f"   ID {uid}: {hash_pwd[:30]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Probar verificación
    print("\n🧪 Prueba: Verificar 'spy11' (último password)")
    try:
        conn = sqlite3.connect(db_path, timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT id, password_hash FROM users")
        all_users = cursor.fetchall()
        conn.close()
        
        test_password = "spy11"
        found = False
        
        for uid, hash_pwd in all_users:
            try:
                if bcrypt.checkpw(test_password.encode('utf-8'), hash_pwd.encode('utf-8')):
                    found = True
                    print(f"   ✅ ¡Encontrado! Usuario ID: {uid}")
                    break
            except:
                pass
        
        if not found:
            print(f"   ❌ 'spy11' no coincide con ningún hash en la BD")
            print(f"\n   Esto significa:")
            print(f"   - Los passwords en el archivo NO están en la BD")
            print(f"   - La BD tiene passwords viejos hasheados")
            print(f"\n   💡 SOLUCIÓN: Ejecutar 'python insert_40_passwords.py' para actualizar")
    except Exception as e:
        print(f"   ❌ Error en verificación: {e}")

if __name__ == "__main__":
    verificar_passwords_db()
