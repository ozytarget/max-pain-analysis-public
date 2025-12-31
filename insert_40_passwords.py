#!/usr/bin/env python3
"""
Script para insertar 40 passwords independientes en la BD
Cada contraseña es la llave de autenticación
"""

import sqlite3
import bcrypt
import os

def insert_40_passwords():
    """Inserta 40 passwords hasheados en la base de datos"""
    
    # Leer los 40 passwords del archivo
    try:
        with open('40_passwords.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("❌ Archivo 40_passwords.txt no encontrado")
        return
    
    # Extraer solo los passwords (líneas con formato "N. PASSWORD")
    passwords = []
    for line in lines:
        line = line.strip()
        if line and '.' in line and len(line) > 3:
            # Formato: "1. zQiJEGfOHNq4"
            try:
                parts = line.split('. ', 1)
                if len(parts) == 2:
                    password = parts[1]
                    passwords.append(password)
            except:
                pass
    
    print(f"\n✅ Encontrados {len(passwords)} passwords")
    
    # Crear/conectar a la BD
    db_path = "auth_data/users.db"
    os.makedirs("auth_data", exist_ok=True)
    
    conn = sqlite3.connect(db_path, timeout=10)
    cursor = conn.cursor()
    
    # Crear tabla si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            password_hash TEXT UNIQUE NOT NULL,
            tier TEXT DEFAULT 'Pro',
            daily_limit INTEGER DEFAULT 100,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Limpiar tabla anterior
    cursor.execute("DROP TABLE IF EXISTS users")
    
    # Recrear tabla SOLO con password_hash
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            password_hash TEXT UNIQUE NOT NULL,
            tier TEXT DEFAULT 'Pro',
            daily_limit INTEGER DEFAULT 100,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insertar cada password
    print("\n" + "="*70)
    print("Insertando passwords en la BD...")
    print("="*70 + "\n")
    
    for i, password in enumerate(passwords, 1):
        try:
            # Hashear con bcrypt
            password_hash = bcrypt.hashpw(
                password.encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
            
            # Insertar en BD
            cursor.execute(
                "INSERT INTO users (password_hash, tier, daily_limit) VALUES (?, ?, ?)",
                (password_hash, 'Pro', 100)
            )
            
            print(f"{i:2d}. ✅ {password}")
            
        except Exception as e:
            print(f"{i:2d}. ❌ Error: {password} - {e}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*70)
    print(f"✅ {len(passwords)} alumnos insertados en auth_data/users.db")
    print("="*70)

if __name__ == "__main__":
    insert_40_passwords()
