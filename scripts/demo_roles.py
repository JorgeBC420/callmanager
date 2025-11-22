#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Demo interactivo del sistema de autorización por roles de CallManager
Muestra cómo diferentes roles tienen acceso a diferentes endpoints
"""

import requests
import json
from tabulate import tabulate

# Configuración
BASE_URL = "http://127.0.0.1:5000"

# API Keys de los usuarios creados (cambiar según salida de init_users.py)
USERS = {
    "Agent": {"name": "agent1", "key": "agent1-key-b51817d3"},
    "TeamLead": {"name": "teamlead_sales", "key": "teamlead-sales-13fc848f"},
    "ProjectManager": {"name": "project_manager", "key": "pm-key-486c39b8"},
    "TI": {"name": "ti_admin", "key": "ti-key-41b567fa"},
}

def test_endpoint(role, endpoint, method="GET", data=None):
    """Test an endpoint with a specific role's API key"""
    api_key = USERS[role]["key"]
    headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
    
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=data, timeout=5)
        
        status = response.status_code
        if status == 200:
            return "[OK] Acceso permitido", status
        elif status == 403:
            return "[DENIED] Acceso denegado", status
        elif status == 401:
            return "[UNAUTH] No autenticado", status
        else:
            return f"[ERROR] ({status})", status
    except Exception as e:
        return f"[FAILED] Error: {str(e)}", 0

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def main():
    print_header("DEMO: SISTEMA DE AUTORIZACION POR ROLES - CallManager")
    
    # Test 1: Personal Metrics Access
    print_header("TEST 1: Acceso a Métricas Personales (/metrics/personal)")
    print("Todos los roles deberían poder acceder\n")
    
    results = []
    for role in USERS.keys():
        result, status = test_endpoint(role, "/metrics/personal")
        results.append([role, result, status])
    
    print(tabulate(results, headers=["Rol", "Resultado", "Status"], tablefmt="grid"))
    
    # Test 2: Team Metrics Access
    print_header("TEST 2: Acceso a Métricas de Equipo (/metrics/team)")
    print("Solo TeamLead y roles superiores deberían tener acceso\n")
    
    results = []
    for role in USERS.keys():
        result, status = test_endpoint(role, "/metrics/team")
        results.append([role, result, status])
    
    print(tabulate(results, headers=["Rol", "Resultado", "Status"], tablefmt="grid"))
    
    # Test 3: All Metrics Access
    print_header("TEST 3: Acceso a Todas las Métricas (/metrics/all)")
    print("Solo ProjectManager y TI deberían tener acceso\n")
    
    results = []
    for role in USERS.keys():
        result, status = test_endpoint(role, "/metrics/all")
        results.append([role, result, status])
    
    print(tabulate(results, headers=["Rol", "Resultado", "Status"], tablefmt="grid"))
    
    # Test 4: Configuration Access (GET)
    print_header("TEST 4: Acceso a Configuración - Lectura (/config GET)")
    print("Solo ProjectManager y TI deberían tener acceso\n")
    
    results = []
    for role in USERS.keys():
        result, status = test_endpoint(role, "/config")
        results.append([role, result, status])
    
    print(tabulate(results, headers=["Rol", "Resultado", "Status"], tablefmt="grid"))
    
    # Test 5: Configuration Access (POST)
    print_header("TEST 5: Acceso a Configuración - Escritura (/config POST)")
    print("Solo TI debería tener acceso\n")
    
    results = []
    for role in USERS.keys():
        result, status = test_endpoint(role, "/config", method="POST", data={"test": "data"})
        results.append([role, result, status])
    
    print(tabulate(results, headers=["Rol", "Resultado", "Status"], tablefmt="grid"))
    
    # Summary
    print_header("RESUMEN DE PERMISOS")
    
    permissions = {
        "Agent": {
            "Personal Metrics": "[OK]",
            "Team Metrics": "[DENIED]",
            "All Metrics": "[DENIED]",
            "Config (GET)": "[DENIED]",
            "Config (POST)": "[DENIED]",
        },
        "TeamLead": {
            "Personal Metrics": "[OK]",
            "Team Metrics": "[OK]",
            "All Metrics": "[DENIED]",
            "Config (GET)": "[DENIED]",
            "Config (POST)": "[DENIED]",
        },
        "ProjectManager": {
            "Personal Metrics": "[OK]",
            "Team Metrics": "[OK]",
            "All Metrics": "[OK]",
            "Config (GET)": "[OK]",
            "Config (POST)": "[DENIED]",
        },
        "TI": {
            "Personal Metrics": "[OK]",
            "Team Metrics": "[OK]",
            "All Metrics": "[OK]",
            "Config (GET)": "[OK]",
            "Config (POST)": "[OK]",
        },
    }
    
    print("\n")
    headers = ["Rol"] + list(next(iter(permissions.values())).keys())
    rows = [[role] + list(perms.values()) for role, perms in permissions.items()]
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    
    print_header("DEMO COMPLETADA")
    print("""
Acciones sugeridas:
  1. Revisar los logs del servidor para ver las autorización denegadas
  2. Probar manualmente con curl:
     
     curl -H "X-API-Key: agent1-key-b51817d3" http://127.0.0.1:5000/metrics/personal
     curl -H "X-API-Key: ti-key-41b567fa" http://127.0.0.1:5000/config
  
  3. Ejecutar el cliente UI (call_manager_app.py)
  4. Revisar el código de @require_role en server.py para entender la implementación
  5. Leer ROLES_Y_AUTORIZACION.md para documentación completa
""")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor en http://127.0.0.1:5000")
        print("   Asegúrate de que server.py está ejecutándose")
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrumpida")
