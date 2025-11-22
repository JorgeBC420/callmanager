"""
Dashboard de Métricas - CallManager
Módulo para visualizar métricas según el rol del usuario
Versión: 1.0
"""

import customtkinter as ctk
from tkinter import ttk, messagebox
import requests
import threading
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional

try:
    from auth_context import current_user
except ImportError:
    # Fallback si no está disponible
    class DummyUser:
        username = "user"
        role = "agent"
    current_user = DummyUser()

# Colores
COLOR_PRIMARY = "#0066cc"
COLOR_SUCCESS = "#2ecc71"
COLOR_WARNING = "#f39c12"
COLOR_DANGER = "#e74c3c"
COLOR_INFO = "#3498db"
COLOR_BG = "#1e1e2e"
COLOR_CARD = "#2d2d44"
COLOR_TEXT = "#ffffff"
COLOR_TEXT_SECONDARY = "#a0a0a0"

class SimpleChart(ctk.CTkFrame):
    """Gráfico de barras simple para métricas"""
    def __init__(self, parent, title="", data=None, **kwargs):
        super().__init__(parent, fg_color=COLOR_CARD, corner_radius=8, **kwargs)
        
        self.title = title
        self.data = data or {}
        
        # Título
        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=("Segoe UI", 12, "bold"),
            text_color=COLOR_TEXT
        )
        title_label.pack(pady=(10, 5), padx=10, anchor="w")
        
        # Canvas para dibujar
        self.canvas = ctk.CTkCanvas(
            self,
            bg=COLOR_CARD,
            highlightthickness=0,
            height=200
        )
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.draw_chart()
    
    def draw_chart(self):
        """Dibuja el gráfico de barras"""
        self.canvas.delete("all")
        
        if not self.data:
            self.canvas.create_text(
                100, 100,
                text="Sin datos",
                fill=COLOR_TEXT_SECONDARY,
                font=("Segoe UI", 10)
            )
            return
        
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        # Máximo valor para escala
        max_value = max(self.data.values()) if self.data else 1
        if max_value == 0:
            max_value = 1
        
        items = list(self.data.items())
        bar_width = (width - 40) / max(len(items), 1)
        x_start = 20
        y_bottom = height - 30
        
        for idx, (label, value) in enumerate(items):
            x = x_start + idx * bar_width + bar_width * 0.1
            bar_height = (value / max_value) * (height - 60)
            
            # Barra
            color = COLOR_SUCCESS if value > 0 else COLOR_WARNING
            self.canvas.create_rectangle(
                x, y_bottom - bar_height,
                x + bar_width * 0.8, y_bottom,
                fill=color,
                outline=COLOR_TEXT,
                width=1
            )
            
            # Valor
            self.canvas.create_text(
                x + bar_width * 0.4,
                y_bottom - bar_height - 10,
                text=str(value),
                fill=COLOR_TEXT,
                font=("Segoe UI", 9, "bold")
            )
            
            # Etiqueta
            self.canvas.create_text(
                x + bar_width * 0.4,
                y_bottom + 10,
                text=label[:8],
                fill=COLOR_TEXT_SECONDARY,
                font=("Segoe UI", 8)
            )

class MetricCard(ctk.CTkFrame):
    """Tarjeta de métrica individual"""
    def __init__(self, parent, title="", value="0", subtitle="", color=COLOR_INFO, **kwargs):
        super().__init__(parent, fg_color=COLOR_CARD, corner_radius=8, **kwargs)
        
        # Título
        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=("Segoe UI", 10),
            text_color=COLOR_TEXT_SECONDARY
        )
        title_label.pack(pady=(10, 5), padx=10)
        
        # Valor principal (grande)
        value_label = ctk.CTkLabel(
            self,
            text=str(value),
            font=("Segoe UI", 28, "bold"),
            text_color=color
        )
        value_label.pack(pady=5, padx=10)
        
        # Subtítulo
        if subtitle:
            subtitle_label = ctk.CTkLabel(
                self,
                text=subtitle,
                font=("Segoe UI", 9),
                text_color=COLOR_TEXT_SECONDARY
            )
            subtitle_label.pack(pady=(0, 10), padx=10)

class AgentMetricsDashboard(ctk.CTkFrame):
    """Dashboard para Agente/Asesor"""
    def __init__(self, parent, api_url="", api_key="", **kwargs):
        super().__init__(parent, fg_color=COLOR_BG, **kwargs)
        
        self.api_url = api_url
        self.api_key = api_key
        self.metrics_data = {}
        self.metric_cards = {}
        
        # Título
        title = ctk.CTkLabel(
            self,
            text="📊 Mis Métricas",
            font=("Segoe UI", 20, "bold"),
            text_color=COLOR_TEXT
        )
        title.pack(pady=15, padx=20)
        
        # Frame de métricas principales (4 columnas)
        metrics_frame = ctk.CTkFrame(self, fg_color="transparent")
        metrics_frame.pack(fill="x", padx=20, pady=10)
        
        # Crear tarjetas de métricas (guardando referencias)
        self.metric_cards['total_calls'] = MetricCard(
            metrics_frame,
            title="Total Llamadas",
            value="0",
            color=COLOR_INFO
        )
        self.metric_cards['total_calls'].pack(side="left", fill="both", expand=True, padx=5)
        
        self.metric_cards['calls_success'] = MetricCard(
            metrics_frame,
            title="Llamadas Exitosas",
            value="0",
            color=COLOR_SUCCESS
        )
        self.metric_cards['calls_success'].pack(side="left", fill="both", expand=True, padx=5)
        
        self.metric_cards['sales'] = MetricCard(
            metrics_frame,
            title="Ventas",
            value="0",
            color=COLOR_SUCCESS
        )
        self.metric_cards['sales'].pack(side="left", fill="both", expand=True, padx=5)
        
        self.metric_cards['installs'] = MetricCard(
            metrics_frame,
            title="Instalaciones",
            value="0",
            color=COLOR_PRIMARY
        )
        self.metric_cards['installs'].pack(side="left", fill="both", expand=True, padx=5)
        
        # Segunda fila de métricas
        metrics_frame2 = ctk.CTkFrame(self, fg_color="transparent")
        metrics_frame2.pack(fill="x", padx=20, pady=10)
        
        self.metric_cards['call_time'] = MetricCard(
            metrics_frame2,
            title="Tiempo en Llamadas",
            value="0h",
            color=COLOR_WARNING
        )
        self.metric_cards['call_time'].pack(side="left", fill="both", expand=True, padx=5)
        
        self.metric_cards['success_rate'] = MetricCard(
            metrics_frame2,
            title="Tasa de Éxito",
            value="0%",
            color=COLOR_INFO
        )
        self.metric_cards['success_rate'].pack(side="left", fill="both", expand=True, padx=5)
        
        self.metric_cards['avg_calls'] = MetricCard(
            metrics_frame2,
            title="Promedio de Llamadas/Día",
            value="0",
            color=COLOR_INFO
        )
        self.metric_cards['avg_calls'].pack(side="left", fill="both", expand=True, padx=5)
        
        self.metric_cards['calls_failed'] = MetricCard(
            metrics_frame2,
            title="Llamadas Fallidas",
            value="0",
            color=COLOR_DANGER
        )
        self.metric_cards['calls_failed'].pack(side="left", fill="both", expand=True, padx=5)
        
        # Gráficos
        charts_frame = ctk.CTkFrame(self, fg_color="transparent")
        charts_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Gráfico estado de llamadas
        self.chart_status = SimpleChart(
            charts_frame,
            title="Estado de Llamadas",
            data={"Exitosas": 0, "Fallidas": 0, "Pendientes": 0}
        )
        self.chart_status.pack(side="left", fill="both", expand=True, padx=5)
        
        # Gráfico por día
        self.chart_weekly = SimpleChart(
            charts_frame,
            title="Llamadas por Día (Última Semana)",
            data={"Lun": 0, "Mar": 0, "Mié": 0, "Jue": 0, "Vie": 0}
        )
        self.chart_weekly.pack(side="left", fill="both", expand=True, padx=5)
        
        # Botón refresh
        refresh_btn = ctk.CTkButton(
            self,
            text="🔄 Actualizar",
            command=self.refresh_metrics,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_INFO
        )
        refresh_btn.pack(pady=10)
        
        # Cargar datos al iniciar
        self.refresh_metrics()
    
    def refresh_metrics(self):
        """Actualiza las métricas desde el servidor"""
        threading.Thread(target=self._load_metrics, daemon=True).start()
    
    def _load_metrics(self):
        """Carga métricas del servidor"""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(
                f"{self.api_url}/metrics/personal",
                headers=headers,
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self.metrics_data = data
                self._update_display(data)
        except Exception as e:
            print(f"Error loading metrics: {e}")
    
    def _update_display(self, data):
        """Actualiza la pantalla con datos del servidor"""
        try:
            calls_made = data.get('calls_made', 0)
            calls_success = data.get('calls_success', 0)
            calls_failed = data.get('calls_failed', 0)
            success_rate = data.get('success_rate', 0)
            
            # Actualizar tarjetas
            self._update_metric('total_calls', str(calls_made))
            self._update_metric('calls_success', str(calls_success))
            self._update_metric('calls_failed', str(calls_failed))
            self._update_metric('success_rate', f"{success_rate:.1f}%")
            self._update_metric('sales', str(data.get('contacts_managed', 0)))
            self._update_metric('installs', "0")  # Pendiente en backend
            self._update_metric('call_time', "0h")  # Pendiente en backend
            
            # Calcular promedio
            avg_calls = calls_made // 30 if calls_made > 0 else 0
            self._update_metric('avg_calls', str(avg_calls))
            
            # Actualizar gráficos
            if self.chart_status:
                self.chart_status.data = {
                    "Exitosas": calls_success,
                    "Fallidas": calls_failed,
                    "Pendientes": max(0, calls_made - calls_success - calls_failed)
                }
                self.chart_status.draw_chart()
        except Exception as e:
            print(f"Error updating display: {e}")
    
    def _update_metric(self, key, value):
        """Actualiza una métrica en la pantalla"""
        try:
            if key in self.metric_cards:
                # Actualizar el valor en la tarjeta
                for widget in self.metric_cards[key].winfo_children():
                    if hasattr(widget, '_text') and widget._text and isinstance(widget, ctk.CTkLabel):
                        try:
                            # Si es numérico grande, es probablemente el valor principal
                            if widget.cget('font')[1] >= 28:
                                widget.configure(text=value)
                                break
                        except:
                            pass
        except Exception as e:
            print(f"Error updating metric {key}: {e}")

class SupervisorMetricsDashboard(ctk.CTkFrame):
    """Dashboard para Supervisor"""
    def __init__(self, parent, api_url="", api_key="", **kwargs):
        super().__init__(parent, fg_color=COLOR_BG, **kwargs)
        
        self.api_url = api_url
        self.api_key = api_key
        self.team_data = []
        
        # Título
        title = ctk.CTkLabel(
            self,
            text="📊 Métricas del Equipo",
            font=("Segoe UI", 20, "bold"),
            text_color=COLOR_TEXT
        )
        title.pack(pady=15, padx=20)
        
        # Tabs para equipos
        tab_view = ctk.CTkTabview(self, fg_color=COLOR_CARD)
        tab_view.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Tab Mi Equipo
        mi_equipo_tab = tab_view.add("Mi Equipo")
        mi_equipo_tab.configure(fg_color=COLOR_BG)
        
        # Frame scrollable para agentes
        self.team_table_frame = ctk.CTkScrollableFrame(
            mi_equipo_tab,
            fg_color=COLOR_CARD,
            corner_radius=8
        )
        self.team_table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame de métricas consolidadas
        metrics_frame = ctk.CTkFrame(mi_equipo_tab, fg_color="transparent")
        metrics_frame.pack(fill="x", padx=10, pady=10)
        
        self.card_team_calls = MetricCard(
            metrics_frame,
            title="Total Llamadas (Equipo)",
            value="0",
            color=COLOR_INFO
        )
        self.card_team_calls.pack(side="left", fill="both", expand=True, padx=5)
        
        self.card_team_sales = MetricCard(
            metrics_frame,
            title="Ventas Totales",
            value="0",
            color=COLOR_SUCCESS
        )
        self.card_team_sales.pack(side="left", fill="both", expand=True, padx=5)
        
        self.card_team_installs = MetricCard(
            metrics_frame,
            title="Instalaciones",
            value="0",
            color=COLOR_PRIMARY
        )
        self.card_team_installs.pack(side="left", fill="both", expand=True, padx=5)
        
        self.card_team_members = MetricCard(
            metrics_frame,
            title="Miembros Activos",
            value="0",
            color=COLOR_INFO
        )
        self.card_team_members.pack(side="left", fill="both", expand=True, padx=5)
        
        # Tab Otro Equipo (resumen)
        otro_equipo_tab = tab_view.add("Otro Equipo")
        otro_equipo_tab.configure(fg_color=COLOR_BG)
        
        metrics_frame2 = ctk.CTkFrame(otro_equipo_tab, fg_color="transparent")
        metrics_frame2.pack(fill="x", padx=10, pady=10)
        
        self.card_other_calls = MetricCard(
            metrics_frame2,
            title="Total Llamadas",
            value="0",
            color=COLOR_INFO
        )
        self.card_other_calls.pack(side="left", fill="both", expand=True, padx=5)
        
        self.card_other_sales = MetricCard(
            metrics_frame2,
            title="Ventas Totales",
            value="0",
            color=COLOR_SUCCESS
        )
        self.card_other_sales.pack(side="left", fill="both", expand=True, padx=5)
        
        self.card_other_installs = MetricCard(
            metrics_frame2,
            title="Instalaciones",
            value="0",
            color=COLOR_PRIMARY
        )
        self.card_other_installs.pack(side="left", fill="both", expand=True, padx=5)
        
        # Botón refresh
        refresh_btn = ctk.CTkButton(
            self,
            text="🔄 Actualizar",
            command=self.refresh_metrics,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_INFO
        )
        refresh_btn.pack(pady=10)
        
        # Cargar datos
        self.refresh_metrics()
    
    def _update_team_table(self):
        """Actualiza la tabla de agentes"""
        # Limpiar tabla anterior
        for widget in self.team_table_frame.winfo_children():
            widget.destroy()
        
        # Header
        header_frame = ctk.CTkFrame(self.team_table_frame, fg_color=COLOR_CARD)
        header_frame.pack(fill="x", padx=0, pady=10)
        
        ctk.CTkLabel(header_frame, text="Nombre", font=("Segoe UI", 10, "bold"), text_color=COLOR_TEXT).pack(side="left", expand=True, padx=10)
        ctk.CTkLabel(header_frame, text="Llamadas", font=("Segoe UI", 10, "bold"), text_color=COLOR_TEXT).pack(side="left", expand=True, padx=10)
        ctk.CTkLabel(header_frame, text="Exitosas", font=("Segoe UI", 10, "bold"), text_color=COLOR_TEXT).pack(side="left", expand=True, padx=10)
        ctk.CTkLabel(header_frame, text="Tasa Éxito", font=("Segoe UI", 10, "bold"), text_color=COLOR_TEXT).pack(side="left", expand=True, padx=10)
        
        # Datos de agentes
        for agent in self.team_data:
            row_frame = ctk.CTkFrame(self.team_table_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=0, pady=5)
            
            ctk.CTkLabel(row_frame, text=agent.get("username", "N/A"), text_color=COLOR_TEXT).pack(side="left", expand=True, padx=10)
            ctk.CTkLabel(row_frame, text=str(agent.get("calls_made", 0)), text_color=COLOR_INFO).pack(side="left", expand=True, padx=10)
            ctk.CTkLabel(row_frame, text=str(agent.get("calls_success", 0)), text_color=COLOR_SUCCESS).pack(side="left", expand=True, padx=10)
            
            rate = agent.get("success_rate", 0)
            ctk.CTkLabel(row_frame, text=f"{rate:.1f}%", text_color=COLOR_WARNING).pack(side="left", expand=True, padx=10)
    
    def refresh_metrics(self):
        """Actualiza las métricas"""
        threading.Thread(target=self._load_metrics, daemon=True).start()
    
    def _load_metrics(self):
        """Carga métricas del servidor"""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(
                f"{self.api_url}/metrics/team",
                headers=headers,
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self.team_data = data if isinstance(data, list) else [data]
                self._update_display(data)
        except Exception as e:
            print(f"Error loading metrics: {e}")
    
    def _update_display(self, data):
        """Actualiza la pantalla"""
        try:
            self._update_team_table()
            
            if isinstance(data, list):
                total_calls = sum(d.get('calls_made', 0) for d in data)
                total_success = sum(d.get('calls_success', 0) for d in data)
                total_managed = sum(d.get('contacts_managed', 0) for d in data)
                
                # Actualizar tarjetas
                self._update_card(self.card_team_calls, str(total_calls))
                self._update_card(self.card_team_sales, str(total_managed))
                self._update_card(self.card_team_installs, "0")
                self._update_card(self.card_team_members, str(len(data)))
        except Exception as e:
            print(f"Error updating display: {e}")
    
    def _update_card(self, card, value):
        """Actualiza un MetricCard con nuevo valor"""
        try:
            for widget in card.winfo_children():
                if hasattr(widget, '_text') and widget._text and isinstance(widget, ctk.CTkLabel):
                    try:
                        if widget.cget('font')[1] >= 28:
                            widget.configure(text=value)
                            break
                    except:
                        pass
        except Exception as e:
            print(f"Error updating card: {e}")

class ProjectManagerDashboard(ctk.CTkFrame):
    """Dashboard para Jefe de Proyecto"""
    def __init__(self, parent, api_url="", api_key="", **kwargs):
        super().__init__(parent, fg_color=COLOR_BG, **kwargs)
        
        self.api_url = api_url
        self.api_key = api_key
        self.all_metrics = {}
        
        # Título
        title = ctk.CTkLabel(
            self,
            text="📊 Dashboard Ejecutivo",
            font=("Segoe UI", 20, "bold"),
            text_color=COLOR_TEXT
        )
        title.pack(pady=15, padx=20)
        
        # Métricas consolidadas
        metrics_frame = ctk.CTkFrame(self, fg_color="transparent")
        metrics_frame.pack(fill="x", padx=20, pady=10)
        
        self.card_total_calls = MetricCard(
            metrics_frame,
            title="Total Llamadas (Todos)",
            value="0",
            color=COLOR_INFO
        )
        self.card_total_calls.pack(side="left", fill="both", expand=True, padx=5)
        
        self.card_total_sales = MetricCard(
            metrics_frame,
            title="Total Ventas",
            value="0",
            color=COLOR_SUCCESS
        )
        self.card_total_sales.pack(side="left", fill="both", expand=True, padx=5)
        
        self.card_total_installs = MetricCard(
            metrics_frame,
            title="Total Instalaciones",
            value="0",
            color=COLOR_PRIMARY
        )
        self.card_total_installs.pack(side="left", fill="both", expand=True, padx=5)
        
        self.card_total_teams = MetricCard(
            metrics_frame,
            title="Equipos Activos",
            value="0",
            color=COLOR_INFO
        )
        self.card_total_teams.pack(side="left", fill="both", expand=True, padx=5)
        
        # Tabs para equipos
        tab_view = ctk.CTkTabview(self, fg_color=COLOR_CARD)
        tab_view.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Crear tabs dinámicos para cada equipo
        self.team_tabs = {}
        
        # Tab Resumen
        resumen_tab = tab_view.add("Resumen General")
        resumen_tab.configure(fg_color=COLOR_BG)
        
        charts_frame = ctk.CTkFrame(resumen_tab, fg_color="transparent")
        charts_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.chart_teams = SimpleChart(
            charts_frame,
            title="Comparativa de Equipos",
            data={}
        )
        self.chart_teams.pack(side="left", fill="both", expand=True, padx=5)
        
        self.chart_sales = SimpleChart(
            charts_frame,
            title="Ventas por Equipo",
            data={}
        )
        self.chart_sales.pack(side="left", fill="both", expand=True, padx=5)
        
        # Botón refresh
        refresh_btn = ctk.CTkButton(
            self,
            text="🔄 Actualizar",
            command=self.refresh_metrics,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_INFO
        )
        refresh_btn.pack(pady=10)
        
        self.tab_view = tab_view
        self.refresh_metrics()
    
    def _create_team_section(self, parent, team_name):
        """Crea sección para un equipo"""
        # Métricas
        metrics_frame = ctk.CTkFrame(parent, fg_color="transparent")
        metrics_frame.pack(fill="x", padx=10, pady=10)
        
        MetricCard(
            metrics_frame,
            title="Llamadas",
            value="0",
            color=COLOR_INFO
        ).pack(side="left", fill="both", expand=True, padx=5)
        
        MetricCard(
            metrics_frame,
            title="Ventas",
            value="0",
            color=COLOR_SUCCESS
        ).pack(side="left", fill="both", expand=True, padx=5)
        
        MetricCard(
            metrics_frame,
            title="Instalaciones",
            value="0",
            color=COLOR_PRIMARY
        ).pack(side="left", fill="both", expand=True, padx=5)
        
        MetricCard(
            metrics_frame,
            title="Agentes",
            value="0",
            color=COLOR_INFO
        ).pack(side="left", fill="both", expand=True, padx=5)
        
        # Tabla de agentes
        table_frame = ctk.CTkFrame(parent, fg_color=COLOR_CARD, corner_radius=8)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        header_frame = ctk.CTkFrame(table_frame, fg_color=COLOR_CARD)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(header_frame, text="Agente", font=("Segoe UI", 10, "bold"), text_color=COLOR_TEXT).pack(side="left", expand=True)
        ctk.CTkLabel(header_frame, text="Llamadas", font=("Segoe UI", 10, "bold"), text_color=COLOR_TEXT).pack(side="left", expand=True)
        ctk.CTkLabel(header_frame, text="Ventas", font=("Segoe UI", 10, "bold"), text_color=COLOR_TEXT).pack(side="left", expand=True)
        ctk.CTkLabel(header_frame, text="Éxito %", font=("Segoe UI", 10, "bold"), text_color=COLOR_TEXT).pack(side="left", expand=True)
    
    def refresh_metrics(self):
        """Actualiza métricas"""
        threading.Thread(target=self._load_metrics, daemon=True).start()
    
    def _load_metrics(self):
        """Carga métricas del servidor"""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(
                f"{self.api_url}/metrics/all",
                headers=headers,
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                self.all_metrics = data
                self._update_display(data)
        except Exception as e:
            print(f"Error loading metrics: {e}")
    
    def _update_display(self, data):
        """Actualiza la pantalla"""
        try:
            # Actualizar métricas principales
            total_calls = data.get('total_calls', 0)
            total_success = data.get('total_success', 0)
            total_contacts = data.get('total_contacts', 0)
            by_team = data.get('by_team', {})
            
            self._update_card(self.card_total_calls, str(total_calls))
            self._update_card(self.card_total_sales, str(total_contacts))
            self._update_card(self.card_total_installs, "0")
            self._update_card(self.card_total_teams, str(len(by_team)))
            
            # Actualizar gráficos
            team_calls = {team: data['calls_made'] for team, data in by_team.items()}
            team_sales = {team: data['calls_success'] for team, data in by_team.items()}
            
            self.chart_teams.data = team_calls
            self.chart_teams.draw_chart()
            
            self.chart_sales.data = team_sales
            self.chart_sales.draw_chart()
            
        except Exception as e:
            print(f"Error updating display: {e}")
    
    def _update_card(self, card, value):
        """Actualiza un MetricCard"""
        try:
            for widget in card.winfo_children():
                if hasattr(widget, '_text') and widget._text and isinstance(widget, ctk.CTkLabel):
                    try:
                        if widget.cget('font')[1] >= 28:
                            widget.configure(text=value)
                            break
                    except:
                        pass
        except Exception as e:
            print(f"Error updating card: {e}")

def get_dashboard_for_role(parent, role: str, api_url="", api_key=""):
    """Retorna el dashboard correcto según el rol"""
    if role == "agent":
        return AgentMetricsDashboard(parent, api_url, api_key)
    elif role == "supervisor":
        return SupervisorMetricsDashboard(parent, api_url, api_key)
    elif role in ["projectmanager", "teamlead"]:
        return ProjectManagerDashboard(parent, api_url, api_key)
    else:
        return AgentMetricsDashboard(parent, api_url, api_key)
