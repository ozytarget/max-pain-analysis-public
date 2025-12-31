#!/usr/bin/env python3
"""
Generar 40 passwords simples tipo trading
Formato: 4 letras (ticker) + 2 números
Ejemplos: tsla23, aapl12, msft45, googl89, etc.
"""

import random

def generar_passwords_trading():
    """Genera 40 passwords simples estilo trading"""
    
    # Tickers y símbolos de trading comunes (4 letras)
    tickers = [
        "tsla", "aapl", "msft", "googl", "amzn",
        "meta", "nvda", "amd", "intc", "pypl",
        "uber", "snap", "twtr", "roku", "pepl",
        "disk", "avgo", "crwd", "snow", "mstr",
        "mrvl", "lrcx", "amat", "asml", "cdns",
        "vrtx", "tech", "spot", "dash", "coin",
        "riot", "mara", "clsk", "mstr", "lens",
        "nflx", "hulu", "ipod", "qqqq", "spy",
        "vti", "ark", "qqq", "xle", "xlf"
    ]
    
    passwords = []
    
    print("\n" + "="*70)
    print("🔐 40 PASSWORDS TRADING (FORMATO SIMPLE)")
    print("="*70 + "\n")
    
    for i in range(40):
        # Seleccionar ticker (sin repetir demasiado)
        ticker = tickers[i % len(tickers)]
        # Generar 2 números aleatorios (01 a 99)
        numeros = f"{random.randint(1, 99):02d}"
        # Combinar
        password = f"{ticker}{numeros}"
        passwords.append(password)
        print(f"{i+1:2d}. {password}")
    
    # Guardar en archivo
    with open('40_passwords.txt', 'w', encoding='utf-8') as f:
        f.write("40 PASSWORDS TRADING PARA DISTRIBUIR A LOS ALUMNOS\n")
        f.write("="*70 + "\n")
        f.write("Formato: 4 letras (ticker) + 2 números\n")
        f.write("Ejemplos: tsla23, aapl12, msft45\n")
        f.write("="*70 + "\n\n")
        
        for i, pwd in enumerate(passwords, 1):
            f.write(f"{i:2d}. {pwd}\n")
    
    print("\n" + "="*70)
    print(f"✅ 40 passwords guardados en: 40_passwords.txt")
    print("="*70)
    
    return passwords

if __name__ == "__main__":
    generar_passwords_trading()
