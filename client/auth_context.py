"""
Sistema de Autenticación - CallManager
Gestiona el rol y datos del usuario actual
Versión: 1.0
"""

class CurrentUser:
    """Información del usuario actual"""
    def __init__(self, username: str, role: str, team_id: str = None, team_name: str = None):
        self.username = username
        self.role = role  # agent, supervisor, teamlead, projectmanager, ti
        self.team_id = team_id
        self.team_name = team_name
    
    def is_agent(self):
        return self.role.lower() == "agent"
    
    def is_supervisor(self):
        return self.role.lower() == "supervisor"
    
    def is_teamlead(self):
        return self.role.lower() == "teamlead"
    
    def is_projectmanager(self):
        return self.role.lower() in ["projectmanager", "pm"]
    
    def is_admin(self):
        return self.role.lower() in ["ti", "admin"]
    
    def can_view_team_metrics(self):
        """Puede ver métricas de su equipo o de todos"""
        return self.role.lower() in ["teamlead", "projectmanager", "pm", "ti", "admin"]
    
    def can_view_all_metrics(self):
        """Puede ver métricas de toda la organización"""
        return self.role.lower() in ["projectmanager", "pm", "ti", "admin"]

# Usuario actual (por defecto es agente)
# En una aplicación real, esto vendría del servidor de autenticación
current_user = CurrentUser(
    username="Agent User",
    role="agent",
    team_id="team_1",
    team_name="Team 1"
)

def set_current_user(username: str, role: str, team_id: str = None, team_name: str = None):
    """Actualiza el usuario actual (llamar después de autenticación exitosa)"""
    global current_user
    current_user = CurrentUser(username, role, team_id, team_name)
