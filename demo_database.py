#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DEMOSTRACIÓN INTERACTIVA: Estructura de Base de Datos y Gestión de Registros
CallManager - Sistema de Gestión de Llamadas

Muestra:
1. Estructura de la base de datos
2. Tablas principales (Contacts, Users, UserMetrics)
3. Cómo cargar registros
4. Cómo trabajar con datos
5. Estadísticas y reportes
"""

import os
import sys
from datetime import datetime, timedelta
from tabulate import tabulate

# Configurar encoding para Windows
if sys.platform.startswith('win'):
    os.chdir(r'c:\Users\bjorg\OneDrive\Desktop\callmanager')

from server import Session, Contact, User, UserMetrics

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*100)
    print(f"  {title}")
    print("="*100 + "\n")

def show_database_structure():
    """Mostrar la estructura de la base de datos"""
    print_section("1. ESTRUCTURA DE LA BASE DE DATOS")
    
    structure = [
        ["Tabla", "Propósito", "Campos Principales"],
        ["-" * 20, "-" * 50, "-" * 50],
        [
            "contacts",
            "Registra clientes/contactos del call center",
            "name, phone, email, status, assigned_to_user_id, team_id, last_called, created_at"
        ],
        [
            "users",
            "Usuarios del sistema con roles y permisos",
            "username, role, team_id, team_name, api_key, is_active, last_login"
        ],
        [
            "user_metrics",
            "Métricas de desempeño por usuario",
            "user_id, calls_made, calls_success, calls_failed, contacts_managed, avg_call_duration"
        ]
    ]
    
    print(tabulate(structure, headers="firstrow", tablefmt="grid", maxcolwidths=[20, 50, 50]))

def show_contacts():
    """Mostrar contactos en la base de datos"""
    print_section("2. CONTACTOS CARGADOS (Muestra de primeros 10)")
    
    session = Session()
    contacts = session.query(Contact).limit(10).all()
    
    if not contacts:
        print("No hay contactos en la base de datos aún.")
        session.close()
        return
    
    rows = []
    for c in contacts:
        rows.append([
            c.name[:15] if c.name else "N/A",
            c.phone if c.phone else "N/A",
            c.email if c.email else "N/A",
            c.status,
            c.assigned_to_user_id if c.assigned_to_user_id else "Sin asignar",
            c.assigned_to_team_name if c.assigned_to_team_name else "N/A",
            c.last_called.strftime("%d/%m %H:%M") if c.last_called else "Nunca"
        ])
    
    print(tabulate(rows, headers=[
        "Nombre", "Teléfono", "Email", "Estado", "Asignado a", "Equipo", "Último contacto"
    ], tablefmt="grid", maxcolwidths=[15, 15, 20, 12, 15, 15, 15]))
    
    print(f"\nTotal de contactos: {session.query(Contact).count()}")
    session.close()

def show_users():
    """Mostrar usuarios del sistema"""
    print_section("3. USUARIOS DEL SISTEMA CON ROLES")
    
    session = Session()
    users = session.query(User).all()
    
    if not users:
        print("No hay usuarios en la base de datos.")
        session.close()
        return
    
    rows = []
    for u in users:
        rows.append([
            u.username,
            u.role,
            u.team_name if u.team_name else "Admin",
            "Activo" if u.is_active else "Inactivo",
            u.last_login.strftime("%d/%m %H:%M") if u.last_login else "Nunca",
            u.api_key[:20] + "..." if u.api_key else "N/A"
        ])
    
    print(tabulate(rows, headers=[
        "Usuario", "Rol", "Equipo", "Estado", "Último acceso", "API Key (primeros 20 chars)"
    ], tablefmt="grid", maxcolwidths=[20, 15, 20, 10, 20, 30]))
    
    print(f"\nTotal de usuarios: {len(users)}")
    
    # Mostrar resumen por rol
    print("\nResumen por rol:")
    role_summary = {}
    for u in users:
        role_summary[u.role] = role_summary.get(u.role, 0) + 1
    
    role_rows = [[role, count] for role, count in sorted(role_summary.items())]
    print(tabulate(role_rows, headers=["Rol", "Cantidad"], tablefmt="simple"))
    
    session.close()

def show_metrics():
    """Mostrar métricas de usuarios"""
    print_section("4. METRICAS DE DESEMPEÑO POR USUARIO")
    
    session = Session()
    metrics = session.query(UserMetrics).all()
    
    if not metrics:
        print("No hay métricas registradas aún.")
        session.close()
        return
    
    rows = []
    total_calls = 0
    total_success = 0
    
    for m in metrics:
        user = session.query(User).filter_by(id=m.user_id).first()
        username = user.username if user else "Unknown"
        
        success_rate = 0
        if m.calls_made > 0:
            success_rate = (m.calls_success / m.calls_made) * 100
        
        rows.append([
            username,
            m.calls_made,
            m.calls_success,
            m.calls_failed,
            f"{success_rate:.1f}%",
            m.contacts_managed,
            f"{m.avg_call_duration}s" if m.avg_call_duration else "N/A"
        ])
        
        total_calls += m.calls_made
        total_success += m.calls_success
    
    print(tabulate(rows, headers=[
        "Usuario", "Llamadas", "Exitosas", "Fallidas", "% Éxito", "Contactos", "Dur. Prom"
    ], tablefmt="grid", maxcolwidths=[20, 12, 12, 12, 10, 12, 12]))
    
    # Estadísticas globales
    print(f"\nEstadísticas Globales:")
    print(f"  Total de llamadas: {total_calls}")
    print(f"  Total de llamadas exitosas: {total_success}")
    if total_calls > 0:
        print(f"  Tasa de éxito global: {(total_success/total_calls)*100:.1f}%")
    
    session.close()

def show_contact_by_status():
    """Mostrar distribución de contactos por estado"""
    print_section("5. DISTRIBUCION DE CONTACTOS POR ESTADO")
    
    session = Session()
    status_counts = {}
    
    contacts = session.query(Contact).all()
    for contact in contacts:
        status = contact.status or "Sin estado"
        status_counts[status] = status_counts.get(status, 0) + 1
    
    if not status_counts:
        print("No hay contactos en la base de datos.")
        session.close()
        return
    
    rows = [[status, count] for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True)]
    print(tabulate(rows, headers=["Estado", "Cantidad"], tablefmt="grid"))
    
    session.close()

def show_team_distribution():
    """Mostrar distribución de contactos por equipo"""
    print_section("6. DISTRIBUCION DE CONTACTOS POR EQUIPO")
    
    session = Session()
    team_counts = {}
    
    contacts = session.query(Contact).all()
    for contact in contacts:
        team = contact.assigned_to_team_name or "Sin asignar"
        team_counts[team] = team_counts.get(team, 0) + 1
    
    if not team_counts:
        print("No hay contactos en la base de datos.")
        session.close()
        return
    
    rows = [[team, count] for team, count in sorted(team_counts.items(), key=lambda x: x[1], reverse=True)]
    print(tabulate(rows, headers=["Equipo", "Cantidad"], tablefmt="grid"))
    
    session.close()

def demo_sql_queries():
    """Mostrar ejemplos de queries útiles"""
    print_section("7. EJEMPLOS DE QUERIES ÚTILES")
    
    session = Session()
    
    examples = []
    
    # Ejemplo 1: Contactos no asignados
    unassigned = session.query(Contact).filter(Contact.assigned_to_user_id == None).count()
    examples.append([
        "Contactos sin asignar",
        f"session.query(Contact).filter(Contact.assigned_to_user_id == None).count()",
        unassigned
    ])
    
    # Ejemplo 2: Usuarios activos
    active_users = session.query(User).filter(User.is_active == 1).count()
    examples.append([
        "Usuarios activos",
        "session.query(User).filter(User.is_active == 1).count()",
        active_users
    ])
    
    # Ejemplo 3: Contactos por equipo
    sales_team = session.query(Contact).filter(Contact.assigned_to_team_name == "Equipo Ventas").count()
    examples.append([
        "Contactos en Equipo Ventas",
        'session.query(Contact).filter(Contact.assigned_to_team_name == "Equipo Ventas").count()',
        sales_team
    ])
    
    # Ejemplo 4: Llamadas en últimas 24h
    yesterday = datetime.now() - timedelta(days=1)
    recent_calls = session.query(Contact).filter(Contact.last_called >= yesterday).count()
    examples.append([
        "Contactos llamados en últimas 24h",
        "session.query(Contact).filter(Contact.last_called >= yesterday).count()",
        recent_calls
    ])
    
    # Ejemplo 5: Agentes con más de 50 llamadas
    high_performers = session.query(UserMetrics).filter(UserMetrics.calls_made > 50).count()
    examples.append([
        "Usuarios con más de 50 llamadas",
        "session.query(UserMetrics).filter(UserMetrics.calls_made > 50).count()",
        high_performers
    ])
    
    print(tabulate(examples, headers=["Descripción", "Query", "Resultado"], tablefmt="grid", maxcolwidths=[35, 60, 10]))
    
    session.close()

def show_relationships():
    """Mostrar cómo están relacionadas las tablas"""
    print_section("8. RELACIONES ENTRE TABLAS")
    
    relationships = [
        [
            "Contact -> User",
            "assigned_to_user_id",
            "Un contacto puede estar asignado a un usuario (Agent o TeamLead)",
            "Muchos contactos : Un usuario"
        ],
        [
            "Contact -> Team",
            "assigned_to_team_name",
            "Un contacto pertenece a un equipo (Ventas, Soporte, etc)",
            "Muchos contactos : Un equipo"
        ],
        [
            "User -> Team",
            "team_id, team_name",
            "Un usuario pertenece a un equipo específico",
            "Muchos usuarios : Un equipo"
        ],
        [
            "User -> UserMetrics",
            "user_id",
            "Cada usuario tiene un registro de métricas (1:1)",
            "Un usuario : Una métrica"
        ]
    ]
    
    print(tabulate(relationships, headers=[
        "Relación", "Campo", "Descripción", "Cardinalidad"
    ], tablefmt="grid", maxcolwidths=[20, 20, 50, 20]))

def show_endpoints_reference():
    """Mostrar endpoints disponibles para trabajar con datos"""
    print_section("9. ENDPOINTS DE API PARA TRABAJAR CON DATOS")
    
    endpoints = [
        ["GET", "/contacts", "Obtener todos los contactos", "Agent+"],
        ["GET", "/contacts/<id>", "Obtener contacto específico", "Agent+"],
        ["POST", "/contacts", "Crear nuevo contacto", "Agent+"],
        ["PUT", "/contacts/<id>", "Actualizar contacto", "Agent+"],
        ["DELETE", "/contacts/<id>", "Eliminar contacto", "Agent+"],
        ["GET", "/metrics/personal", "Mi desempeño", "Todos"],
        ["GET", "/metrics/team", "Métricas de mi equipo", "TeamLead+"],
        ["GET", "/metrics/all", "Todas las métricas", "ProjectManager+"],
        ["GET", "/config", "Ver configuración", "ProjectManager+"],
        ["POST", "/config", "Modificar configuración", "TI"],
    ]
    
    print(tabulate(endpoints, headers=[
        "Método", "Endpoint", "Descripción", "Requiere Rol"
    ], tablefmt="grid", maxcolwidths=[10, 25, 35, 15]))
    
    print("\nNota: Todos los endpoints requieren encabezado X-API-Key con la API key del usuario")

def main():
    """Ejecutar la demostración completa"""
    print("\n")
    print("╔" + "="*98 + "╗")
    print("║" + " "*20 + "CallManager - DEMOSTRACIÓN DE BASE DE DATOS Y GESTIÓN DE REGISTROS" + " "*14 + "║")
    print("╚" + "="*98 + "╝")
    
    try:
        show_database_structure()
        show_users()
        show_contacts()
        show_contact_by_status()
        show_team_distribution()
        show_metrics()
        show_relationships()
        demo_sql_queries()
        show_endpoints_reference()
        
        print_section("RESUMEN")
        print("""
El sistema CallManager es una aplicación de gestión de call centers con:

1. BASE DE DATOS:
   - SQLite con WAL mode para mejor concurrencia
   - Modelos SQLAlchemy para Contact, User, y UserMetrics
   - Relaciones entre tablas para mantener integridad

2. GESTIÓN DE REGISTROS:
   - API REST para CRUD completo de contactos
   - Asignación de contactos a usuarios y equipos
   - Histórico de llamadas y timestamps

3. ROLES Y PERMISOS:
   - Agent: Ver y gestionar sus contactos personales
   - TeamLead: Ver contactos de su equipo + métricas
   - ProjectManager: Ver todas las métricas
   - TI: Acceso total a configuración

4. METRICAS Y REPORTES:
   - Llamadas exitosas/fallidas por usuario
   - Contactos gestionados
   - Distribución por equipo y estado

5. INTERFAZ GRÁFICA (CustomTkinter):
   - Aplicación Windows moderna
   - Carga de contactos desde CSV/JSON
   - Dashboard en tiempo real
   - Integración con InterPhone (pywinauto)

USO TÍPICO DEL SISTEMA:
  1. Agent inicia sesión con su API key
  2. Ve sus contactos asignados
  3. Realiza llamadas y actualiza estados
  4. TeamLead supervisa el equipo
  5. ProjectManager ve reportes consolidados
  6. TI administra usuarios y configuración
        """)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
