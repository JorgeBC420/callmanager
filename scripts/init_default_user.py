#!/usr/bin/env python3
"""
init_default_user.py - Crear usuario por defecto
Corre automáticamente cuando no hay usuarios en la BD
"""

import os
import sys
from pathlib import Path

# Agregar el directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

from server import Session, User, hash_password
import secrets

def create_default_user():
    """Crear usuario admin por defecto si no existen usuarios"""
    db = Session()
    try:
        # Verificar si hay usuarios
        count = db.query(User).count()
        if count > 0:
            print("✅ Ya existen usuarios en la base de datos. No se crea usuario por defecto.")
            return
        
        # Crear usuario admin
        username = "admin"
        password = "1234"  # CONTRASEÑA POR DEFECTO - El usuario debe cambiarla
        api_key = secrets.token_urlsafe(32)
        
        user = User(
            id="user_admin_default",
            username=username,
            password_hash=hash_password(password),
            api_key=api_key,
            role="TI",  # Admin role
            team_name="Administración",
            is_active=1
        )
        
        db.add(user)
        db.commit()
        
        print("""
╔════════════════════════════════════════════════════════════╗
║         ✅ USUARIO POR DEFECTO CREADO                     ║
╚════════════════════════════════════════════════════════════╝

Credenciales:
  Username: admin
  Password: 1234

API Key (para integración):
  """)
        print(f"  {api_key}\n")
        
        print("""⚠️  IMPORTANTE:
1. Guarda la API Key en un lugar seguro
2. Cambia la contraseña inmediatamente después de primer login
3. NO compartir estas credenciales

Próximos pasos:
1. Login con admin/1234
2. Ir a /auth/change-password para cambiar contraseña
3. Crear otros usuarios según necesites
        """)
        
    except Exception as e:
        print(f"❌ Error creando usuario por defecto: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    create_default_user()
