"""
Metrics Dashboard - CallManager
Panel visual de métricas de llamadas y rendimiento por rol de usuario.

Roles:
- Agent: Ve solo sus propias métricas
- TeamLead/Supervisor: Ve su equipo + totales
- ProjectManager/Admin/TI: Ve toda la organización
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
import requests
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# Colores del tema
COLOR_PRIMARY = "#3498db"
COLOR_SUCCESS = "#2ecc71"
COLOR_WARNING = "#f39c12"
COLOR_DANGER = "#e74c3c"
COLOR_DARK_BG = "#1e1e1e"
COLOR_CARD_BG = "#2d2d2d"
COLOR_CARD_HOVER = "#3d3d3d"


class MetricsCard(ctk.CTkFrame):
    """Tarjeta KPI para mostrar métrica individual"""
    
    def __init__(self, parent, title: str, value: str = "0", unit: str = "", 
                 color: str = COLOR_PRIMARY, **kwargs):
        super().__init__(parent, fg_color=COLOR_CARD_BG, corner_radius=10, **kwargs)
        
        self.title = title
        self.color = color
        
        # Título
        lbl_title = ctk.CTkLabel(
            self, 
            text=title,
            font=("Segoe UI", 12, "bold"),
            text_color="#888888"
        )
        lbl_title.pack(pady=(15, 5), padx=15, anchor="w")
        
        # Contenedor de valor
        value_frame = ctk.CTkFrame(self, fg_color="transparent")
        value_frame.pack(pady=(5, 15), padx=15, fill="x")
        
        # Valor principal
        self.lbl_value = ctk.CTkLabel(
            value_frame,
            text=value,
            font=("Segoe UI", 28, "bold"),
            text_color=color
        )
        self.lbl_value.pack(side="left")
        
        # Unidad
        if unit:
            lbl_unit = ctk.CTkLabel(
                value_frame,
                text=f" {unit}",
                font=("Segoe UI", 12),
                text_color="#888888"
            )
            lbl_unit.pack(side="left", padx=(5, 0))
    
    def set_value(self, value: str):
        """Actualizar valor mostrado"""
        self.lbl_value.configure(text=value)


class CallLogsTable(ctk.CTkToplevel):
    """Ventana con tabla de historiales de llamadas"""
    
    def __init__(self, parent, base_url: str, headers: Dict, user_role: str):
        super().__init__(parent)
        self.title("Historial de Llamadas")
        self.geometry("900x500")
        
        self.base_url = base_url
        self.headers = headers
        self.user_role = user_role
        
        self._build_ui()
        self.load_logs()
    
    def _build_ui(self):
        """Construir interfaz"""
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.pack(fill="x", padx=15, pady=10)
        
        lbl = ctk.CTkLabel(header, text="📞 Historial de Llamadas", 
                          font=("Segoe UI", 16, "bold"))
        lbl.pack(side="left")
        
        btn_refresh = ctk.CTkButton(header, text="🔄 Actualizar", width=100, 
                                   command=self.load_logs)
        btn_refresh.pack(side="right")
        
        # Tabla (usando ttk.Treeview)
        self.tree = ttk.Treeview(
            self,
            columns=("Usuario", "Contacto", "Teléfono", "Duración", "Estado", "Hora"),
            height=20,
            show="headings"
        )
        
        # Configurar columnas
        self.tree.column("Usuario", width=100)
        self.tree.column("Contacto", width=150)
        self.tree.column("Teléfono", width=120)
        self.tree.column("Duración", width=80)
        self.tree.column("Estado", width=100)
        self.tree.column("Hora", width=150)
        
        for col in ("Usuario", "Contacto", "Teléfono", "Duración", "Estado", "Hora"):
            self.tree.heading(col, text=col)
        
        self.tree.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscroll=scrollbar.set)
    
    def load_logs(self):
        """Cargar logs en un thread"""
        threading.Thread(target=self._fetch_logs, daemon=True).start()
    
    def _fetch_logs(self):
        """Obtener logs del servidor"""
        try:
            response = requests.get(
                f"{self.base_url}/api/calls/log?limit=100",
                headers=self.headers,
                timeout=5
            )
            
            if response.status_code == 200:
                calls = response.json()
                self.after(0, lambda: self._populate_table(calls))
        except Exception as e:
            logger.error(f"Error fetching logs: {e}")
    
    def _populate_table(self, calls: List[Dict]):
        """Llenar tabla con datos"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Agregar filas
        for call in calls:
            duration = call.get('duration_seconds', 0)
            duration_str = self._format_duration(duration)
            
            start_time = call.get('start_time', '')
            if start_time:
                try:
                    dt = datetime.fromisoformat(start_time)
                    time_str = dt.strftime("%H:%M:%S")
                except:
                    time_str = start_time
            else:
                time_str = "—"
            
            values = (
                call.get('user_id', '—')[:20],
                call.get('contact_id', '—')[:20],
                call.get('contact_phone', '—'),
                duration_str,
                call.get('status', '—'),
                time_str
            )
            
            self.tree.insert("", "end", values=values)
    
    @staticmethod
    def _format_duration(seconds: int) -> str:
        """Formatear segundos a MM:SS"""
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"


class MetricsDashboard(ctk.CTkToplevel):
    """Panel de métricas principal"""
    
    def __init__(self, parent, base_url: str, api_key: str, 
                 user_id: str, user_role: str = 'agent', username: str = ''):
        super().__init__(parent)
        self.title(f"📊 Métricas de Rendimiento - {username or user_role.upper()}")
        self.geometry("1000x700")
        
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.user_id = user_id
        self.user_role = user_role
        self.username = username
        
        self.headers = {
            'Content-Type': 'application/json',
        }
        if api_key:
            self.headers['X-API-Key'] = api_key
        
        self._build_ui()
        self.load_metrics()
    
    def _build_ui(self):
        """Construir interfaz"""
        # Frame principal con scroll
        main_frame = ctk.CTkScrollableFrame(self, fg_color=COLOR_DARK_BG)
        main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # ===== HEADER =====
        header = ctk.CTkFrame(main_frame, fg_color="transparent", height=60)
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        lbl_title = ctk.CTkLabel(
            header, 
            text="📊 Panel de Métricas",
            font=("Segoe UI", 20, "bold")
        )
        lbl_title.pack(side="left")
        
        # Botones de acción
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")
        
        btn_refresh = ctk.CTkButton(
            btn_frame, 
            text="🔄 Actualizar",
            width=100,
            command=self.load_metrics
        )
        btn_refresh.pack(side="left", padx=5)
        
        btn_logs = ctk.CTkButton(
            btn_frame,
            text="📋 Historial",
            width=100,
            fg_color=COLOR_WARNING,
            command=self.open_call_logs
        )
        btn_logs.pack(side="left", padx=5)
        
        # ===== MÉTRICAS PERSONALES =====
        lbl_personal = ctk.CTkLabel(
            main_frame,
            text="📈 Mis Métricas",
            font=("Segoe UI", 16, "bold")
        )
        lbl_personal.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Cards en grid
        cards_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        cards_frame.pack(fill="x", padx=20, pady=10)
        
        self.card_calls = MetricsCard(
            cards_frame, "Llamadas Realizadas", "0", color=COLOR_PRIMARY
        )
        self.card_calls.pack(side="left", fill="both", expand=True, padx=5)
        
        self.card_success = MetricsCard(
            cards_frame, "Llamadas Exitosas", "0", color=COLOR_SUCCESS
        )
        self.card_success.pack(side="left", fill="both", expand=True, padx=5)
        
        self.card_failed = MetricsCard(
            cards_frame, "Llamadas Fallidas", "0", color=COLOR_DANGER
        )
        self.card_failed.pack(side="left", fill="both", expand=True, padx=5)
        
        # Segunda fila
        cards_frame2 = ctk.CTkFrame(main_frame, fg_color="transparent")
        cards_frame2.pack(fill="x", padx=20, pady=10)
        
        self.card_aht = MetricsCard(
            cards_frame2, "AHT (Promedio)", "00:00", unit="seg", color=COLOR_SUCCESS
        )
        self.card_aht.pack(side="left", fill="both", expand=True, padx=5)
        
        self.card_total_time = MetricsCard(
            cards_frame2, "Tiempo Total", "0 min", unit="", color=COLOR_PRIMARY
        )
        self.card_total_time.pack(side="left", fill="both", expand=True, padx=5)
        
        self.card_sr = MetricsCard(
            cards_frame2, "Tasa de Éxito", "0%", unit="", color=COLOR_SUCCESS
        )
        self.card_sr.pack(side="left", fill="both", expand=True, padx=5)
        
        # ===== VISTA POR ROL =====
        if self.user_role in ['supervisor', 'teamlead', 'ProjectManager', 'TI', 'admin']:
            self._build_team_view(main_frame)
    
    def _build_team_view(self, parent):
        """Construir vista de equipo/organización"""
        lbl_team = ctk.CTkLabel(
            parent,
            text="👥 Métricas del Equipo/Organización",
            font=("Segoe UI", 16, "bold")
        )
        lbl_team.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Frame para tabla
        table_frame = ctk.CTkFrame(parent, fg_color=COLOR_CARD_BG, corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Tabla
        self.team_tree = ttk.Treeview(
            table_frame,
            columns=("Usuario", "Equipo", "Llamadas", "Exitosas", "Tasa %", "AHT"),
            height=8,
            show="headings"
        )
        
        self.team_tree.column("Usuario", width=150)
        self.team_tree.column("Equipo", width=150)
        self.team_tree.column("Llamadas", width=80)
        self.team_tree.column("Exitosas", width=80)
        self.team_tree.column("Tasa %", width=70)
        self.team_tree.column("AHT", width=80)
        
        for col in ("Usuario", "Equipo", "Llamadas", "Exitosas", "Tasa %", "AHT"):
            self.team_tree.heading(col, text=col)
        
        self.team_tree.pack(fill="both", expand=True, padx=15, pady=15)
    
    def load_metrics(self):
        """Cargar métricas en thread separado"""
        threading.Thread(target=self._fetch_metrics, daemon=True).start()
    
    def _fetch_metrics(self):
        """Obtener métricas del servidor"""
        try:
            # Obtener métricas personales
            response = requests.get(
                f"{self.base_url}/metrics/personal",
                headers=self.headers,
                timeout=5
            )
            
            if response.status_code == 200:
                personal = response.json()
                self.after(0, lambda: self._update_personal_metrics(personal))
            
            # Si aplica, obtener métricas de equipo
            if self.user_role in ['supervisor', 'teamlead', 'ProjectManager', 'TI', 'admin']:
                endpoint = '/metrics/team' if self.user_role != 'TI' else '/metrics/all'
                response = requests.get(
                    f"{self.base_url}{endpoint}",
                    headers=self.headers,
                    timeout=5
                )
                
                if response.status_code == 200:
                    team = response.json()
                    self.after(0, lambda: self._update_team_metrics(team))
        except Exception as e:
            logger.error(f"Error fetching metrics: {e}")
    
    def _update_personal_metrics(self, data: Dict):
        """Actualizar tarjetas de métricas personales"""
        calls = data.get('calls_made', 0)
        success = data.get('calls_success', 0)
        failed = data.get('calls_failed', 0)
        aht = data.get('avg_call_duration', 0)
        success_rate = data.get('success_rate', 0)
        
        self.card_calls.set_value(str(calls))
        self.card_success.set_value(str(success))
        self.card_failed.set_value(str(failed))
        self.card_sr.set_value(f"{success_rate:.1f}%")
        
        # AHT formateado
        mins = aht // 60
        secs = aht % 60
        aht_str = f"{mins:02d}:{secs:02d}"
        self.card_aht.set_value(aht_str)
        
        # Tiempo total
        total_secs = calls * aht if calls > 0 else 0
        total_mins = total_secs // 60
        self.card_total_time.set_value(f"{total_mins} min")
    
    def _update_team_metrics(self, data):
        """Actualizar tabla de equipo"""
        if hasattr(self, 'team_tree'):
            # Limpiar
            for item in self.team_tree.get_children():
                self.team_tree.delete(item)
            
            # Agregar filas
            items = data if isinstance(data, list) else data.get('team_users', [])
            
            for user in items:
                username = user.get('username', '—')
                team = user.get('team_name', '—')
                calls = user.get('calls_made', 0)
                success = user.get('calls_success', 0)
                rate = user.get('success_rate', 0)
                aht = user.get('avg_call_duration', 0)
                
                aht_str = f"{aht}s" if isinstance(aht, int) else str(aht)
                
                self.team_tree.insert("", "end", values=(
                    username,
                    team,
                    str(calls),
                    str(success),
                    f"{rate:.1f}%",
                    aht_str
                ))
    
    def open_call_logs(self):
        """Abrir ventana de historial de llamadas"""
        CallLogsTable(self, self.base_url, self.headers, self.user_role)
