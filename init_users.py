#!/usr/bin/env python3
"""
init_users.py - Inicializar usuarios de prueba con diferentes roles
Uso: python init_users.py
"""

import os
import sys
import uuid
from datetime import datetime

# Importar el servidor
sys.path.insert(0, os.path.dirname(__file__))
from server import engine, Session, Base, User, UserMetrics
from config import logger

def init_users():
    """Crear usuarios de prueba con todos los roles"""
    
    # Crear tablas si no existen
    Base.metadata.create_all(engine)
    db = Session()
    
    try:
        # Usuarios de prueba
        test_users = [
            {
                'username': 'agent1',
                'api_key': 'agent1-key-' + str(uuid.uuid4())[:8],
                'role': 'Agent',
                'team_id': 'team-sales',
                'team_name': 'Equipo Ventas',
                'email': 'agent1@example.com'
            },
            {
                'username': 'agent2',
                'api_key': 'agent2-key-' + str(uuid.uuid4())[:8],
                'role': 'Agent',
                'team_id': 'team-sales',
                'team_name': 'Equipo Ventas',
                'email': 'agent2@example.com'
            },
            {
                'username': 'agent3',
                'api_key': 'agent3-key-' + str(uuid.uuid4())[:8],
                'role': 'Agent',
                'team_id': 'team-support',
                'team_name': 'Equipo Soporte',
                'email': 'agent3@example.com'
            },
            {
                'username': 'teamlead_sales',
                'api_key': 'teamlead-sales-' + str(uuid.uuid4())[:8],
                'role': 'TeamLead',
                'team_id': 'team-sales',
                'team_name': 'Equipo Ventas',
                'email': 'teamlead_sales@example.com'
            },
            {
                'username': 'teamlead_support',
                'api_key': 'teamlead-support-' + str(uuid.uuid4())[:8],
                'role': 'TeamLead',
                'team_id': 'team-support',
                'team_name': 'Equipo Soporte',
                'email': 'teamlead_support@example.com'
            },
            {
                'username': 'project_manager',
                'api_key': 'pm-key-' + str(uuid.uuid4())[:8],
                'role': 'ProjectManager',
                'team_id': None,
                'team_name': 'Administración',
                'email': 'pm@example.com'
            },
            {
                'username': 'ti_admin',
                'api_key': 'ti-key-' + str(uuid.uuid4())[:8],
                'role': 'TI',
                'team_id': None,
                'team_name': 'TI',
                'email': 'ti@example.com'
            }
        ]
        
        # Verificar si ya existen
        existing = db.query(User).count()
        if existing > 0:
            print(f"⚠️  Ya existen {existing} usuarios. Limpiando...")
            db.query(User).delete()
            db.query(UserMetrics).delete()
            db.commit()
        
        # Crear usuarios
        print("\n" + "="*60)
        print("👥 INICIALIZANDO USUARIOS DE PRUEBA")
        print("="*60)
        
        for user_data in test_users:
            user = User(
                id=f"u_{user_data['username']}",
                api_key=user_data['api_key'],
                username=user_data['username'],
                role=user_data['role'],
                team_id=user_data['team_id'],
                team_name=user_data['team_name'],
                email=user_data['email'],
                is_active=1,
                last_login=datetime.now()
            )
            db.add(user)
            
            # Crear métricas vacías
            metrics = UserMetrics(
                id=f"m_{user.id}",
                user_id=user.id,
                calls_made=0,
                calls_success=0,
                calls_failed=0,
                contacts_managed=0,
                avg_call_duration=0
            )
            db.add(metrics)
            
            print(f"✅ {user_data['role']:15} | {user_data['username']:20} | {user_data['api_key']}")
        
        db.commit()
        
        print("\n" + "="*60)
        print("📋 RESUMEN DE PERMISOS")
        print("="*60)
        print("""
Agent:
  ✓ Ver métricas personales
  ✓ Hacer llamadas
  
TeamLead:
  ✓ Ver métricas personales
  ✓ Ver métricas de su equipo
  ✓ Ver totales de otros equipos
  
ProjectManager:
  ✓ Ver métricas personales
  ✓ Ver todas las métricas de la organización
  ✓ Acceder a configuraciones
  
TI:
  ✓ Ver métricas personales
  ✓ Ver todas las métricas de la organización
  ✓ Acceder y modificar configuraciones
        """)
        
        print("="*60)
        print("\n✅ Usuarios inicializados exitosamente!")
        print("\nPrueba los endpoints:")
        print("  curl -H 'X-API-Key: APIKEY' http://127.0.0.1:5000/metrics/personal")
        print("  curl -H 'X-API-Key: APIKEY' http://127.0.0.1:5000/metrics/team")
        print("  curl -H 'X-API-Key: APIKEY' http://127.0.0.1:5000/metrics/all")
        print("  curl -H 'X-API-Key: APIKEY' http://127.0.0.1:5000/config")
        
    except Exception as e:
        logger.error(f"Error initializing users: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == '__main__':
    init_users()
