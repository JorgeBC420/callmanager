#!/usr/bin/env python3
"""
test_roles.py - Pruebas de autorización por roles
Uso: python test_roles.py
"""

import requests
import json
from datetime import datetime
import time

# Base URL
BASE_URL = "http://127.0.0.1:5000"

# API keys de prueba (obtenidas después de ejecutar init_users.py)
USERS = {
    "agent": "agent1-key-XXXX",  # Cambiar después de init_users.py
    "teamlead": "teamlead-sales-XXXX",
    "pm": "pm-key-XXXX",
    "ti": "ti-key-XXXX"
}

def test_endpoint(method, endpoint, api_key, data=None):
    """Realizar request a endpoint con API key"""
    url = f"{BASE_URL}{endpoint}"
    headers = {"X-API-Key": api_key}
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=5)
        
        status = "✅" if response.status_code < 400 else "❌"
        print(f"{status} [{response.status_code}] {method:6} {endpoint:25} → {len(response.text)} bytes")
        
        if response.status_code >= 400:
            print(f"    Error: {response.json()}")
        return response
    except Exception as e:
        print(f"❌ ERROR {endpoint}: {e}")
        return None

def run_tests():
    """Ejecutar suite de pruebas"""
    
    print("="*80)
    print("🧪 PRUEBAS DE AUTORIZACIÓN POR ROLES")
    print("="*80)
    
    print("\n" + "📌 1. VERIFICAR SALUD DEL SERVIDOR")
    test_endpoint("GET", "/health", "dummy-key")
    
    print("\n" + "👤 2. ENDPOINTS DE MÉTRICAS PERSONALES (Accesible por todos)")
    print("   Agent:")
    test_endpoint("GET", "/metrics/personal", USERS["agent"])
    print("   TeamLead:")
    test_endpoint("GET", "/metrics/personal", USERS["teamlead"])
    print("   PM:")
    test_endpoint("GET", "/metrics/personal", USERS["pm"])
    print("   TI:")
    test_endpoint("GET", "/metrics/personal", USERS["ti"])
    
    print("\n" + "👥 3. ENDPOINTS DE MÉTRICAS DE EQUIPO (Agent → Debe fallar)")
    print("   Agent (debe fallar):")
    test_endpoint("GET", "/metrics/team", USERS["agent"])
    print("   TeamLead (debe funcionar - su equipo + totales):")
    test_endpoint("GET", "/metrics/team", USERS["teamlead"])
    print("   PM (debe funcionar - todos):")
    test_endpoint("GET", "/metrics/team", USERS["pm"])
    print("   TI (debe funcionar - todos):")
    test_endpoint("GET", "/metrics/team", USERS["ti"])
    
    print("\n" + "📊 4. ENDPOINTS DE MÉTRICAS GLOBALES (Solo PM/TI)")
    print("   Agent (debe fallar):")
    test_endpoint("GET", "/metrics/all", USERS["agent"])
    print("   TeamLead (debe fallar):")
    test_endpoint("GET", "/metrics/all", USERS["teamlead"])
    print("   PM (debe funcionar):")
    test_endpoint("GET", "/metrics/all", USERS["pm"])
    print("   TI (debe funcionar):")
    test_endpoint("GET", "/metrics/all", USERS["ti"])
    
    print("\n" + "⚙️  5. ENDPOINT DE CONFIGURACIÓN - GET (PM/TI)")
    print("   Agent (debe fallar):")
    test_endpoint("GET", "/config", USERS["agent"])
    print("   TeamLead (debe fallar):")
    test_endpoint("GET", "/config", USERS["teamlead"])
    print("   PM (debe funcionar):")
    test_endpoint("GET", "/config", USERS["pm"])
    print("   TI (debe funcionar):")
    test_endpoint("GET", "/config", USERS["ti"])
    
    print("\n" + "⚙️  6. ENDPOINT DE CONFIGURACIÓN - POST (Solo TI)")
    print("   PM (debe fallar):")
    test_endpoint("POST", "/config", USERS["pm"], {"debug": True})
    print("   TI (debe funcionar):")
    test_endpoint("POST", "/config", USERS["ti"], {"debug": True})
    
    print("\n" + "="*80)
    print("✅ PRUEBAS COMPLETADAS")
    print("="*80)
    print("""
RESUMEN DE PERMISOS:
┌─────────────────┬──────────────┬─────────────┬──────────┬──────────┐
│ Endpoint        │ Agent        │ TeamLead    │ PM       │ TI       │
├─────────────────┼──────────────┼─────────────┼──────────┼──────────┤
│ /metrics/person │ ✅           │ ✅          │ ✅       │ ✅       │
│ /metrics/team   │ ❌           │ ✅          │ ✅       │ ✅       │
│ /metrics/all    │ ❌           │ ❌          │ ✅       │ ✅       │
│ /config (GET)   │ ❌           │ ❌          │ ✅       │ ✅       │
│ /config (POST)  │ ❌           │ ❌          │ ❌       │ ✅       │
└─────────────────┴──────────────┴─────────────┴──────────┴──────────┘
    """)

if __name__ == '__main__':
    print("\n⏳ Esperando 2 segundos para que el servidor esté listo...")
    time.sleep(2)
    run_tests()
