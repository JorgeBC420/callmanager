#!/usr/bin/env python3
"""
test_auth_system.py - Pruebas rápidas del sistema de autenticación
"""

import sys
import os
import json
from pathlib import Path

# Agregar el directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

# Imports del servidor
from server import (
    Session, User, 
    hash_password, verify_password,
    generate_jwt_token, verify_jwt_token
)
import secrets

def test_bcrypt_hashing():
    """Test 1: Verificar bcrypt hashing"""
    print("\n" + "="*60)
    print("TEST 1: Bcrypt Password Hashing")
    print("="*60)
    
    password = "1234"
    hashed = hash_password(password)
    
    print(f"✓ Password original: {password}")
    print(f"✓ Password hasheado: {hashed[:50]}...")
    print(f"✓ Hash length: {len(hashed)}")
    
    # Verificar correcta
    assert verify_password("1234", hashed), "❌ Hash verification FAILED"
    print("✓ verify_password('1234') = ✅ TRUE")
    
    # Verificar incorrecta
    assert not verify_password("wrong", hashed), "❌ Hash verification FAILED"
    print("✓ verify_password('wrong') = ✅ FALSE")
    
    print("\n✅ TEST 1 PASSED: Bcrypt funciona correctamente\n")

def test_jwt_tokens():
    """Test 2: Verificar JWT tokens"""
    print("\n" + "="*60)
    print("TEST 2: JWT Token Generation & Validation")
    print("="*60)
    
    user_id = "user_test_123"
    username = "admin"
    role = "TI"
    
    # Generar token
    token = generate_jwt_token(user_id, username, role)
    print(f"✓ Token generado: {token[:50]}...")
    print(f"✓ Token length: {len(token)}")
    
    # Verificar token válido
    payload = verify_jwt_token(token)
    assert payload is not None, "❌ Token validation FAILED"
    print(f"✓ Token payload: {json.dumps(payload, indent=2)}")
    
    assert payload['user_id'] == user_id, "❌ User ID mismatch"
    assert payload['username'] == username, "❌ Username mismatch"
    assert payload['role'] == role, "❌ Role mismatch"
    print("✓ Token claims verified correctly")
    
    print("\n✅ TEST 2 PASSED: JWT funciona correctamente\n")

def test_user_creation():
    """Test 3: Crear usuario en BD"""
    print("\n" + "="*60)
    print("TEST 3: User Creation in Database")
    print("="*60)
    
    db = Session()
    try:
        # Verificar si ya existe usuario de prueba
        test_user = db.query(User).filter_by(username="test_agente").first()
        if test_user:
            print("ℹ️  Usuario 'test_agente' ya existe, usando existente")
            return test_user
        
        # Crear nuevo usuario
        username = "test_agente"
        password = "testpass123"
        api_key = secrets.token_urlsafe(32)
        
        user = User(
            id=f"user_{username}_{int(__import__('time').time())}",
            username=username,
            password_hash=hash_password(password),
            api_key=api_key,
            role="Agent",
            team_name="Test Team",
            is_active=1
        )
        
        db.add(user)
        db.commit()
        
        print(f"✓ Usuario creado: {username}")
        print(f"✓ User ID: {user.id}")
        print(f"✓ Role: {user.role}")
        print(f"✓ API Key: {api_key[:30]}...")
        
        # Verificar que se guardó
        saved_user = db.query(User).filter_by(username=username).first()
        assert saved_user is not None, "❌ User not found after creation"
        print(f"✓ Usuario guardado correctamente en BD")
        
        # Verificar contraseña
        assert verify_password(password, saved_user.password_hash), "❌ Password verification FAILED"
        print(f"✓ Verificación de contraseña: ✅ OK")
        
        print("\n✅ TEST 3 PASSED: Usuario creado correctamente\n")
        return user
        
    finally:
        db.close()

def test_default_user():
    """Test 4: Verificar usuario por defecto"""
    print("\n" + "="*60)
    print("TEST 4: Default User Admin")
    print("="*60)
    
    db = Session()
    try:
        admin_user = db.query(User).filter_by(username="admin").first()
        
        if admin_user:
            print(f"✓ Usuario admin encontrado:")
            print(f"  - ID: {admin_user.id}")
            print(f"  - Username: {admin_user.username}")
            print(f"  - Role: {admin_user.role}")
            print(f"  - API Key: {admin_user.api_key[:30]}...")
            print(f"  - Is Active: {admin_user.is_active}")
            
            # Verificar que la contraseña es 1234
            if verify_password("1234", admin_user.password_hash):
                print(f"  - Password: ✅ Es '1234' (CAMBIAR EN PRODUCCIÓN)")
            else:
                print(f"  - Password: ✅ Ha sido cambiada")
            
            print("\n✅ TEST 4 PASSED: Usuario admin listo\n")
        else:
            print("ℹ️  Usuario admin no existe aún (se creará en primer inicio)\n")
            
    finally:
        db.close()

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║         PRUEBAS DEL SISTEMA DE AUTENTICACIÓN             ║
║                  CallManager v3.3.1                        ║
╚════════════════════════════════════════════════════════════╝
""")
    
    try:
        test_bcrypt_hashing()
        test_jwt_tokens()
        test_user_creation()
        test_default_user()
        
        print("\n" + "="*60)
        print("✅ TODAS LAS PRUEBAS PASARON CORRECTAMENTE")
        print("="*60)
        print("""
Próximos pasos:
1. Ejecutar: python server.py
2. Esperar a que se cree el usuario admin/1234
3. Probar login:
   curl -X POST http://localhost:5000/auth/login \\
     -H "Content-Type: application/json" \\
     -d '{"username":"admin","password":"1234"}'

4. Usar el token JWT para futuras requests:
   curl -H "Authorization: Bearer <token>" \\
     http://localhost:5000/contacts
""")
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE LAS PRUEBAS: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
