#!/usr/bin/env python3
"""
Script para resetear contraseñas de usuarios en producción
"""

import bcrypt
import psycopg2
from datetime import datetime

def hash_password(password: str) -> str:
    """Genera hash bcrypt para la contraseña"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def reset_passwords():
    """Resetea las contraseñas de los usuarios admin"""
    
    # Nuevas contraseñas
    new_passwords = {
        'admin@acme.com': 'Admin123!',
        'admin@bravo.com': 'Admin123!'
    }
    
    print("=== RESETEO DE CONTRASEÑAS PRODUCCIÓN ===")
    print()
    
    # Generar hashes
    password_hashes = {}
    for email, password in new_passwords.items():
        hash_pwd = hash_password(password)
        password_hashes[email] = hash_pwd
        print(f"✅ Hash generado para {email}")
    
    # Conectar a BD
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="ecommerce_multi_tenant", 
            user="ecommerce_user",
            password="ecommerce123"
        )
        cursor = conn.cursor()
        
        print("\n🔄 Actualizando contraseñas en BD...")
        
        # Actualizar contraseñas
        for email, hash_pwd in password_hashes.items():
            cursor.execute(
                "UPDATE tenant_users SET password_hash = %s WHERE email = %s;",
                (hash_pwd, email)
            )
            
            # Verificar que se actualizó
            cursor.execute("SELECT client_id FROM tenant_users WHERE email = %s;", (email,))
            result = cursor.fetchone()
            
            if result:
                client_id = result[0]
                print(f"✅ Contraseña actualizada para {email} (cliente: {client_id})")
            else:
                print(f"❌ No se encontró usuario {email}")
        
        conn.commit()
        print("\n💾 Cambios guardados en base de datos")
        
        # Mostrar credenciales finales
        print("\n" + "="*60)
        print("🎉 CREDENCIALES ACTUALIZADAS")
        print("="*60)
        
        cursor.execute("""
            SELECT 
                tu.email,
                tc.name as cliente,
                tc.slug,
                'https://' || tc.slug || '.sintestesia.cl' as url
            FROM tenant_users tu
            JOIN tenant_clients tc ON tu.client_id = tc.id
            WHERE tu.email IN %s
            ORDER BY tc.name;
        """, (tuple(new_passwords.keys()),))
        
        users = cursor.fetchall()
        
        for user in users:
            email, cliente, slug, url = user
            password = new_passwords[email]
            
            print(f"\n🏢 {cliente}")
            print(f"   URL: {url}")
            print(f"   Email: {email}")
            print(f"   Password: {password}")
            print(f"   Slug: {slug}")
        
        print("\n" + "="*60)
        print("✅ Las contraseñas han sido reseteadas exitosamente")
        print("🔐 Ambos usuarios tienen la misma contraseña: Admin123!")
        print("📱 Ya puedes acceder a los backoffices en producción")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    reset_passwords()