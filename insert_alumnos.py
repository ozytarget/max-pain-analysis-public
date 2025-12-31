#!/usr/bin/env python3
"""
Script para insertar alumnos desde CSV a la base de datos
Ejecutar UNA SOLA VEZ: python insert_alumnos.py
"""

import sqlite3
import csv
import bcrypt
import os

DB_PATH = "auth_data/users.db"

def insert_alumnos():
    # Crear directorio si no existe
    os.makedirs("auth_data", exist_ok=True)
    
    # Conectar a BD
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Asegurar tabla existe
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        email TEXT,
        password_hash TEXT NOT NULL,
        tier TEXT DEFAULT "Pro",
        daily_limit INTEGER DEFAULT 100,
        usage_today INTEGER DEFAULT 0,
        license_expiration TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    )''')
    
    # Leer CSV e insertar
    inserted = 0
    with open("alumnos.csv") as f:
        for row in csv.DictReader(f):
            try:
                username = row["username"].strip()
                password = row["password"].strip()
                email = row["email"].strip()
                tier = row["tier"].strip()
                
                # Hashear contraseña
                hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
                
                # Insertar
                daily_limit = 100 if tier == "Pro" else 10
                cursor.execute("""
                    INSERT OR IGNORE INTO users 
                    (username, email, password_hash, tier, daily_limit)
                    VALUES (?, ?, ?, ?, ?)
                """, (username, email, hashed, tier, daily_limit))
                
                inserted += 1
                print(f"✅ {username} ({tier}) - {daily_limit} queries/día")
                
            except Exception as e:
                print(f"❌ Error en {row['username']}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ {inserted} alumnos insertados correctamente en {DB_PATH}")
    print("Puedes ejecutar la app ahora: streamlit run app.py")

if __name__ == "__main__":
    insert_alumnos()
