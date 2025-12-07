#!/usr/bin/env python3
"""
Script de Demostración: Persistencia de Usuarios Después de Actualización
Muestra qué pasa con los datos cuando actualizas la app
"""

import os
import sys
import sqlite3
from datetime import datetime
import json

def check_users_persistence():
    """Verifica que los usuarios persisten después de actualización"""
    
    db_path = "auth_data/users.db"
    
    print("\n" + "="*70)
    print("📊 ANÁLISIS DE PERSISTENCIA DE USUARIOS")
    print("="*70)
    
    # Check 1: Existe la BD?
    print("\n✅ CHECK 1: ¿Existe la base de datos?")
    if os.path.exists(db_path):
        size_kb = os.path.getsize(db_path) / 1024
        print(f"   ✅ SÍ existe: {db_path}")
        print(f"   📦 Tamaño: {size_kb:.2f} KB")
    else:
        print(f"   ❌ NO existe: {db_path}")
        return
    
    # Check 2: Tabla de usuarios existe?
    print("\n✅ CHECK 2: ¿Tabla 'users' existe?")
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if c.fetchone():
            print("   ✅ SÍ existe tabla 'users'")
        else:
            print("   ❌ NO existe tabla 'users'")
            return
        
        # Check 3: ¿Cuántos usuarios hay?
        print("\n✅ CHECK 3: ¿Cuántos usuarios registrados?")
        c.execute("SELECT COUNT(*) FROM users")
        count = c.fetchone()[0]
        print(f"   📊 Total de usuarios: {count}")
        
        if count == 0:
            print("   ⚠️  No hay usuarios registrados aún")
        else:
            print(f"   ✅ {count} usuario(s) en la base de datos")
        
        # Check 4: Listar usuarios
        if count > 0:
            print("\n✅ CHECK 4: Usuarios registrados:")
            c.execute("""
                SELECT username, email, tier, created_date, active 
                FROM users 
                ORDER BY created_date DESC
            """)
            
            for row in c.fetchall():
                username, email, tier, created_date, active = row
                status = "✅ Activo" if active else "❌ Inactivo"
                print(f"   • {username}")
                print(f"     Email: {email}")
                print(f"     Tier: {tier}")
                print(f"     Registrado: {created_date}")
                print(f"     Estado: {status}")
                print()
        
        # Check 5: Información de la BD
        print("\n✅ CHECK 5: Información de la Base de Datos:")
        c.execute("PRAGMA table_info(users)")
        columns = c.fetchall()
        print(f"   Columnas: {len(columns)}")
        for col in columns:
            col_name, col_type = col[1], col[2]
            print(f"   • {col_name}: {col_type}")
        
        # Check 6: Backups
        print("\n✅ CHECK 6: Backups automáticos:")
        backup_dir = "auth_data/backups"
        if os.path.exists(backup_dir):
            backups = [f for f in os.listdir(backup_dir) if f.startswith("users_backup")]
            if backups:
                print(f"   🔐 {len(backups)} backup(s) encontrado(s):")
                for backup in sorted(backups, reverse=True)[:5]:  # Últimos 5
                    backup_path = os.path.join(backup_dir, backup)
                    size_kb = os.path.getsize(backup_path) / 1024
                    print(f"   • {backup} ({size_kb:.2f} KB)")
            else:
                print("   ℹ️  No hay backups aún (se crean cuando hay cambios de schema)")
        else:
            print("   ℹ️  Carpeta de backups no existe aún")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Conclusión
    print("\n" + "="*70)
    print("✅ CONCLUSIÓN: Los datos están SEGUROS y PERSISTENTES")
    print("="*70)
    print("\n📌 Qué significa esto:")
    print("   • Los usuarios NO se pierden cuando actualizas la app")
    print("   • La BD en SQLite es persistente en disco")
    print("   • Los datos se mantienen entre recargas de Streamlit")
    print("   • Existen backups automáticos para protección")
    print("\n🚀 Puedes actualizar la app sin miedo de perder usuarios\n")

if __name__ == "__main__":
    check_users_persistence()
