#!/usr/bin/env python3
"""
Script para generar passwords hasheados
Usa este script SOLO PARA GENERAR los passwords
Luego distribuye los passwords a cada alumno
"""

import bcrypt
import csv

def generar_passwords():
    """Genera passwords hasheados para cada alumno"""
    
    # Leer el archivo alumnos.csv
    alumnos = []
    try:
        with open('alumnos.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            alumnos = list(reader)
    except FileNotFoundError:
        print("❌ Archivo alumnos.csv no encontrado")
        return
    
    print("\n" + "="*70)
    print("📋 PASSWORDS HASHEADOS PARA DISTRIBUIR A LOS ALUMNOS")
    print("="*70 + "\n")
    
    passwords_generados = []
    
    for alumno in alumnos:
        username = alumno['username']
        password_plaintext = alumno['password']
        email = alumno['email']
        
        # Hashear el password con bcrypt
        password_hash = bcrypt.hashpw(
            password_plaintext.encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
        
        passwords_generados.append({
            'username': username,
            'password_plaintext': password_plaintext,
            'email': email,
            'password_hash': password_hash
        })
        
        print(f"👤 Usuario: {username}")
        print(f"📧 Email: {email}")
        print(f"🔑 Contraseña: {password_plaintext}")
        print(f"🔒 Hash: {password_hash}")
        print("-" * 70 + "\n")
    
    # Guardar los hashes en un archivo para referencia
    with open('passwords_hasheados.txt', 'w', encoding='utf-8') as f:
        f.write("PASSWORDS HASHEADOS - PARA USO EN LA BASE DE DATOS\n")
        f.write("="*70 + "\n\n")
        
        for pwd in passwords_generados:
            f.write(f"Usuario: {pwd['username']}\n")
            f.write(f"Email: {pwd['email']}\n")
            f.write(f"Password (plaintext): {pwd['password_plaintext']}\n")
            f.write(f"Password (hash): {pwd['password_hash']}\n")
            f.write("-"*70 + "\n\n")
    
    print("✅ Passwords hasheados guardados en: passwords_hasheados.txt")
    print("\n📌 INSTRUCCIONES:")
    print("1. Distribuye los passwords (plaintext) a cada alumno por email")
    print("2. Los hashes se guardan en la base de datos")
    print("3. Cada alumno usa su password (plaintext) para logearse")
    print("4. La app verifica el password con bcrypt automáticamente")

if __name__ == "__main__":
    generar_passwords()
