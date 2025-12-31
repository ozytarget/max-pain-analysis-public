#!/usr/bin/env python3
"""
Generar 40 passwords independientes para distribuir a los alumnos
Cada alumno recibe SOLO una contraseña (sin usuario)
"""

import secrets
import string

def generar_40_passwords():
    """Genera 40 passwords seguros y únicos"""
    
    # Caracteres para generar passwords
    caracteres = string.ascii_uppercase + string.ascii_lowercase + string.digits
    
    passwords = []
    
    print("\n" + "="*70)
    print("🔐 40 PASSWORDS INDEPENDIENTES PARA ALUMNOS")
    print("="*70 + "\n")
    
    for i in range(1, 41):
        # Generar password aleatorio de 12 caracteres
        password = ''.join(secrets.choice(caracteres) for _ in range(12))
        passwords.append(password)
        print(f"{i:2d}. {password}")
    
    # Guardar en archivo
    with open('40_passwords.txt', 'w', encoding='utf-8') as f:
        f.write("40 PASSWORDS PARA DISTRIBUIR A LOS ALUMNOS\n")
        f.write("="*70 + "\n")
        f.write("Cada alumno recibe UNA contraseña\n")
        f.write("No hay nombres de usuario - solo contraseña\n")
        f.write("="*70 + "\n\n")
        
        for i, pwd in enumerate(passwords, 1):
            f.write(f"{i:2d}. {pwd}\n")
    
    print("\n" + "="*70)
    print(f"✅ 40 passwords guardados en: 40_passwords.txt")
    print("="*70)

if __name__ == "__main__":
    generar_40_passwords()
