#!/usr/bin/env python3
"""
Script de prueba de login directo
Simula exactamente lo que hace la app
"""

import sqlite3
import bcrypt

def test_login_spy11():
    """Prueba el login con spy11 localmente"""
    
    db_path = "auth_data/users.db"
    password_to_test = "spy11"
    
    print("\n" + "="*70)
    print("🧪 TEST DE LOGIN: 'spy11'")
    print("="*70 + "\n")
    
    try:
        # Conectar a BD
        conn = sqlite3.connect(db_path, timeout=10)
        cursor = conn.cursor()
        
        # Obtener todos los usuarios
        cursor.execute("SELECT id, password_hash FROM users")
        all_users = cursor.fetchall()
        conn.close()
        
        print(f"📊 Total de usuarios en BD: {len(all_users)}")
        print(f"🔑 Probando password: '{password_to_test}'")
        print("\n🔍 Verificando cada hash con bcrypt...")
        
        authenticated = False
        found_id = None
        
        for uid, hash_pwd in all_users:
            try:
                # Asegurar que es string
                if isinstance(hash_pwd, bytes):
                    hash_pwd = hash_pwd.decode('utf-8')
                
                # Verificar con bcrypt
                result = bcrypt.checkpw(password_to_test.encode('utf-8'), hash_pwd.encode('utf-8'))
                
                if result:
                    print(f"\n✅ ¡ENCONTRADO! Usuario ID: {uid}")
                    print(f"   Hash: {hash_pwd[:50]}...")
                    authenticated = True
                    found_id = uid
                    break
                    
            except Exception as e:
                print(f"   ⚠️  Error verificando ID {uid}: {e}")
                continue
        
        if authenticated:
            print(f"\n✅ LOGIN EXITOSO")
            print(f"   Usuario: alumno_{found_id}")
            print(f"   Tier: Pro")
            print(f"   Daily Limit: 100")
        else:
            print(f"\n❌ LOGIN FALLIDO")
            print(f"   No se encontró coincidencia para '{password_to_test}'")
            print(f"\n💡 Posibles causas:")
            print(f"   1. El password no está en la BD")
            print(f"   2. Hay error en bcrypt.checkpw()")
            
            # Mostrar info de debug
            print(f"\n🔬 Debug info:")
            cursor = sqlite3.connect(db_path, timeout=10).cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE 1=1")
            count = cursor.fetchone()[0]
            print(f"   Total de registros: {count}")
            
            # Mostrar primeros 3 hashes para debugging
            cursor.execute("SELECT id, password_hash FROM users LIMIT 3")
            rows = cursor.fetchall()
            print(f"   Primeros 3 registros:")
            for rid, rhash in rows:
                print(f"      ID {rid}: {rhash[:40]}...")
    
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_login_spy11()
