#!/usr/bin/env python3
"""
Auditoría completa de usuarios del sistema
"""
import sqlite3
from datetime import datetime
import json

def audit_users():
    try:
        conn = sqlite3.connect('auth_data/users.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        print("=" * 70)
        print("AUDITORÍA DE USUARIOS - PRO SCANNER")
        print("=" * 70)
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Get users
        try:
            c.execute('SELECT * FROM users')
            users = c.fetchall()
            
            print(f"📊 TOTAL DE USUARIOS REGISTRADOS: {len(users)}")
            print("-" * 70)
            
            if len(users) == 0:
                print("\n⚠️  No hay usuarios registrados aún en la base de datos.")
            else:
                for idx, user in enumerate(users, 1):
                    print(f"\n{idx}. USUARIO")
                    print(f"   Username: {user['username']}")
                    print(f"   Email: {user['email']}")
                    print(f"   Tier: {user['tier']}")
                    print(f"   Expiration: {user['expiration_date']}")
                    print(f"   Active: {'✅ YES' if user['active'] else '❌ NO'}")
                    print(f"   Created: {user['created_date']}")
                    print(f"   Daily Usage: {user['usage_today']}/{user['daily_limit']}")
            
            print("\n" + "=" * 70)
            print("RESUMEN")
            print("=" * 70)
            
            if len(users) > 0:
                # Count by tier
                c.execute("SELECT tier, COUNT(*) as count FROM users GROUP BY tier")
                tier_counts = c.fetchall()
                
                print("\nUsuarios por Tier:")
                for tier_row in tier_counts:
                    print(f"  • {tier_row['tier']}: {tier_row['count']}")
                
                # Count active vs inactive
                c.execute("SELECT active, COUNT(*) as count FROM users GROUP BY active")
                active_counts = c.fetchall()
                
                print("\nEstado de Cuentas:")
                for active_row in active_counts:
                    status = "Activas" if active_row['active'] else "Inactivas"
                    print(f"  • {status}: {active_row['count']}")
            
        except Exception as e:
            print(f"Error reading users table: {e}")
            users = []
        
        conn.close()
        
        # Save audit report
        with open('AUDIT_USUARIOS_2025.md', 'w', encoding='utf-8') as f:
            f.write("# Auditoría de Usuarios - Pro Scanner\n\n")
            f.write(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"## Total de Usuarios: {len(users)}\n\n")
            
            if len(users) == 0:
                f.write("### ⚠️ No hay usuarios registrados aún\n\n")
                f.write("El sistema está listo para recibir nuevos registros.\n\n")
            else:
                f.write("## Usuarios Registrados\n\n")
                for idx, user in enumerate(users, 1):
                    f.write(f"### {idx}. {user['username']}\n")
                    f.write(f"- **Email:** {user['email']}\n")
                    f.write(f"- **Tier:** {user['tier']}\n")
                    f.write(f"- **Expiration:** {user['expiration_date']}\n")
                    f.write(f"- **Active:** {'✅' if user['active'] else '❌'}\n")
                    f.write(f"- **Created:** {user['created_date']}\n")
                    f.write(f"- **Daily Usage:** {user['usage_today']}/{user['daily_limit']}\n\n")
        
        print("\n✅ Audit report saved to: AUDIT_USUARIOS_2025.md")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    audit_users()
