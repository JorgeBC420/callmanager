#!/usr/bin/env python
"""
Script de Demostración - Sistema de Métricas
Muestra un ejemplo de cómo usar el sistema de métricas programáticamente
"""

from client.metrics_dashboard import (
    get_dashboard_for_role,
    AgentMetricsDashboard,
    SupervisorMetricsDashboard,
    ProjectManagerDashboard
)
from client.auth_context import set_current_user, current_user
import customtkinter as ctk

def demo_agent_dashboard():
    """Demostración: Dashboard de Agente"""
    print("\n" + "="*60)
    print("🎯 DEMO: Dashboard de Agente")
    print("="*60)
    
    # Configurar usuario como agente
    set_current_user(
        username="juan_perez",
        role="agent",
        team_id="team_1",
        team_name="Equipo Ventas"
    )
    
    print(f"✅ Usuario actual: {current_user.username}")
    print(f"✅ Rol: {current_user.role}")
    print(f"✅ Equipo: {current_user.team_name}")
    print(f"\n📊 Dashboard mostrará:")
    print("   • Total de llamadas realizadas")
    print("   • Llamadas exitosas/fallidas")
    print("   • Tasa de éxito en porcentaje")
    print("   • Gráfico de estado de llamadas")
    print("   • Gráfico de llamadas por día")

def demo_supervisor_dashboard():
    """Demostración: Dashboard de Supervisor"""
    print("\n" + "="*60)
    print("👨‍💼 DEMO: Dashboard de Supervisor")
    print("="*60)
    
    set_current_user(
        username="carlos_supervisor",
        role="supervisor",
        team_id="team_1",
        team_name="Equipo Ventas"
    )
    
    print(f"✅ Usuario actual: {current_user.username}")
    print(f"✅ Rol: {current_user.role}")
    print(f"✅ Equipo: {current_user.team_name}")
    print(f"\n📊 Dashboard mostrará:")
    print("   • Pestaña 'Mi Equipo':")
    print("     - Métricas consolidadas del equipo")
    print("     - Tabla de desempeño de cada agente")
    print("   • Pestaña 'Otro Equipo':")
    print("     - Totales del equipo competidor")

def demo_projectmanager_dashboard():
    """Demostración: Dashboard de Jefe de Proyecto"""
    print("\n" + "="*60)
    print("🏢 DEMO: Dashboard Ejecutivo (Jefe de Proyecto)")
    print("="*60)
    
    set_current_user(
        username="maria_pm",
        role="projectmanager",
        team_id=None,
        team_name="Administración"
    )
    
    print(f"✅ Usuario actual: {current_user.username}")
    print(f"✅ Rol: {current_user.role}")
    print(f"\n📊 Dashboard mostrará:")
    print("   • Métricas consolidadas de TODA la organización:")
    print("     - Total de llamadas globales")
    print("     - Total de ventas")
    print("     - Total de instalaciones")
    print("     - Cantidad de equipos activos")
    print("   • Pestaña 'Resumen General':")
    print("     - Gráfico comparativo de equipos")
    print("     - Gráfico de ventas por equipo")

def demo_permissions():
    """Demostración: Sistema de Permisos"""
    print("\n" + "="*60)
    print("🔐 DEMO: Sistema de Permisos")
    print("="*60)
    
    roles = [
        ("agent", "Agente"),
        ("supervisor", "Supervisor"),
        ("projectmanager", "Jefe de Proyecto"),
        ("ti", "Administrador TI")
    ]
    
    for role_key, role_name in roles:
        set_current_user("test_user", role_key)
        
        can_view_team = "✅ SÍ" if current_user.can_view_team_metrics() else "❌ NO"
        can_view_all = "✅ SÍ" if current_user.can_view_all_metrics() else "❌ NO"
        
        print(f"\n{role_name}:")
        print(f"  Ver métricas de equipo: {can_view_team}")
        print(f"  Ver métricas globales: {can_view_all}")

def demo_api_integration():
    """Demostración: Integración con API"""
    print("\n" + "="*60)
    print("🔗 DEMO: Integración con API")
    print("="*60)
    
    print("\n📡 Endpoints utilizados:")
    print("  • GET /metrics/personal")
    print("    └─ Retorna: calls_made, calls_success, success_rate")
    print("\n  • GET /metrics/team")
    print("    └─ Retorna: Métricas de todos los usuarios del equipo")
    print("\n  • GET /metrics/all")
    print("    └─ Retorna: Métricas consolidadas por equipo")
    
    print("\n🔑 Headers necesarios:")
    print("  • Authorization: Bearer {API_KEY}")
    print("  • Content-Type: application/json")
    
    print("\n💾 Datos en caché:")
    print("  • Se actualizan al hacer click en '🔄 Actualizar'")
    print("  • Se cargan en background (sin bloquear UI)")

def print_feature_checklist():
    """Imprime lista de features implementados"""
    print("\n" + "="*60)
    print("✨ FEATURES IMPLEMENTADOS")
    print("="*60)
    
    features = {
        "Dashboard de Agente": [
            "✅ 8 tarjetas de métricas principales",
            "✅ Gráfico de estado de llamadas",
            "✅ Gráfico de llamadas por día",
            "✅ Actualización en tiempo real",
            "✅ Botón refresh",
        ],
        "Dashboard de Supervisor": [
            "✅ Métricas consolidadas del equipo",
            "✅ Tabla de desempeño de agentes",
            "✅ Pestaña 'Otro Equipo' para comparación",
            "✅ Actualización dinámica de datos",
            "✅ Botón refresh",
        ],
        "Dashboard Ejecutivo": [
            "✅ 4 métricas principales consolidadas",
            "✅ Gráfico comparativo de equipos",
            "✅ Gráfico de ventas por equipo",
            "✅ Vista de resumen general",
            "✅ Pestañas por equipo",
        ],
        "Sistema de Autenticación": [
            "✅ Clase CurrentUser",
            "✅ Variable global current_user",
            "✅ Función set_current_user()",
            "✅ Métodos de verificación de permisos",
            "✅ Detección automática de dashboard según rol",
        ],
        "Integración en App Principal": [
            "✅ Botón '📊 Métricas' en header",
            "✅ Método show_metrics()",
            "✅ Ventana modal para dashboard",
            "✅ Import del módulo de métricas",
            "✅ Manejo de errores",
        ],
    }
    
    for categoria, items in features.items():
        print(f"\n📌 {categoria}:")
        for item in items:
            print(f"   {item}")

def print_usage_example():
    """Imprime ejemplo de uso"""
    print("\n" + "="*60)
    print("💻 EJEMPLO DE USO")
    print("="*60)
    
    print("\n# 1. En call_manager_app.py, el botón ejecuta:")
    print("""
    def show_metrics(self):
        metrics_window = ctk.CTkToplevel(self)
        dashboard = get_dashboard_for_role(
            metrics_window,
            role="agent",  # O lo que sea
            api_url=SERVER_URL,
            api_key=API_KEY
        )
        dashboard.pack(fill="both", expand=True)
    """)
    
    print("\n# 2. Para cambiar usuario (después de autenticación):")
    print("""
    from auth_context import set_current_user
    
    set_current_user(
        username="juan_perez",
        role="supervisor",
        team_id="team_1",
        team_name="Equipo Ventas"
    )
    """)
    
    print("\n# 3. Para crear un dashboard independiente:")
    print("""
    root = ctk.CTk()
    dashboard = ProjectManagerDashboard(
        root,
        api_url="http://localhost:5000",
        api_key="your-api-key"
    )
    dashboard.pack(fill="both", expand=True)
    root.mainloop()
    """)

if __name__ == "__main__":
    print("\n" + "🎬 "*20)
    print("     DEMOSTRACIÓN - SISTEMA DE MÉTRICAS CALLMANAGER v2.0")
    print("🎬 "*20)
    
    print("\nEste script demuestra las capacidades del nuevo sistema de métricas.")
    print("Los dashboards reales se abren al hacer click en '📊 Métricas'.\n")
    
    # Ejecutar demostraciones
    demo_agent_dashboard()
    demo_supervisor_dashboard()
    demo_projectmanager_dashboard()
    demo_permissions()
    demo_api_integration()
    print_feature_checklist()
    print_usage_example()
    
    print("\n" + "="*60)
    print("✅ PARA PROBAR EL SISTEMA:")
    print("="*60)
    print("""
    1. Inicia el servidor:
       $ python server.py
    
    2. En otra terminal, inicia la app:
       $ python client/call_manager_app.py
    
    3. Haz click en el botón '📊 Métricas' en el header
    
    4. Elige tu rol y explora el dashboard
    """)
    
    print("="*60)
    print("📖 Para más información: docs/METRICAS_Y_DASHBOARDS.md")
    print("📖 Guía de prueba: docs/GUIA_PRUEBA_METRICAS.md")
    print("="*60 + "\n")
