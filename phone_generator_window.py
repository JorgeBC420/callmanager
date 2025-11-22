"""
PhoneGeneratorWindow - Versión Mejorada y Optimizada
Integración profesional para call_manager_app.py

Mejoras respecto a versión anterior:
✅ UI mucho más profesional (colores, estilos, emojis)
✅ Mejor manejo de errores y threading
✅ Descarga de archivos CSV/JSON directa
✅ Información detallada de estadísticas
✅ Auto-importación a BD opcional
✅ Validación robusta de entrada
✅ Mejor visualización de resultados
✅ Rate limiting y timeout handling
"""

import customtkinter as ctk
import requests
from tkinter import messagebox, filedialog
import threading
import json
import csv
import logging

logger = logging.getLogger(__name__)


class PhoneGeneratorWindow(ctk.CTkToplevel):
    """Ventana profesional para generar números telefónicos Costa Rica"""
    
    def __init__(self, parent, server_url, api_key):
        super().__init__(parent)
        
        self.server_url = server_url
        self.api_key = api_key
        self.generated_contacts = []
        self.is_generating = False
        
        # Configuración de la ventana
        self.title("Generador de Números Telefónicos CR")
        self.geometry("750x700")
        self.resizable(False, False)
        
        # Evitar que se cierre si hay generación en progreso
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Centrar ventana respecto al padre
        self.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        x = parent_x + (parent_width - 750) // 2
        y = parent_y + (parent_height - 700) // 2
        self.geometry(f"750x700+{max(0, x)}+{max(0, y)}")
        
        # Set appearance
        ctk.set_appearance_mode("dark")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz completa"""
        
        # Frame principal con scroll
        main_frame = ctk.CTkScrollableFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # ========== HEADER ==========
        self._build_header(main_frame)
        
        # ========== MARKET INFO ==========
        self._build_market_info(main_frame)
        
        # ========== CONFIGURATION ==========
        self._build_config_frame(main_frame)
        
        # ========== BUTTONS ==========
        self._build_buttons(main_frame)
        
        # ========== RESULTS ==========
        self._build_results_frame(main_frame)
        
    def _build_header(self, parent):
        """Sección de título y subtítulo"""
        title_label = ctk.CTkLabel(
            parent,
            text="🇨🇷 Generador de Números Telefónicos",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.pack(pady=(0, 5))
        
        subtitle_label = ctk.CTkLabel(
            parent,
            text="Plan Nacional de Numeración SUTEL 2024",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        subtitle_label.pack(pady=(0, 20))
        
    def _build_market_info(self, parent):
        """Información de distribución del mercado"""
        market_frame = ctk.CTkFrame(parent, fg_color="transparent")
        market_frame.pack(fill="x", pady=(0, 20))
        
        market_title = ctk.CTkLabel(
            market_frame,
            text="📊 Distribución Pospago 2024",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        market_title.pack(pady=(0, 10))
        
        # Operadores con colores
        operators = [
            ("Kölbi (ICE)", "40%", "#2ecc71"),
            ("Telefónica", "35%", "#3498db"),
            ("Claro", "25%", "#e67e22")
        ]
        
        ops_frame = ctk.CTkFrame(market_frame, fg_color="transparent")
        ops_frame.pack(fill="x", pady=(0, 10))
        
        for operator, percentage, color in operators:
            op_box = ctk.CTkFrame(ops_frame, fg_color=color, corner_radius=8)
            op_box.pack(side="left", expand=True, fill="both", padx=5, pady=5)
            
            ctk.CTkLabel(
                op_box,
                text=operator,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="white"
            ).pack(pady=(6, 0))
            
            ctk.CTkLabel(
                op_box,
                text=percentage,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="white"
            ).pack(pady=(2, 6))
    
    def _build_config_frame(self, parent):
        """Configuración de generación"""
        config_frame = ctk.CTkFrame(parent, fg_color="transparent")
        config_frame.pack(fill="x", pady=(0, 20))
        
        # --- Cantidad de números ---
        ctk.CTkLabel(
            config_frame,
            text="Cantidad de números:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=(0, 8))
        
        # Frame con entrada y límites
        count_inner = ctk.CTkFrame(config_frame, fg_color="transparent")
        count_inner.pack(fill="x", pady=(0, 15))
        
        self.count_entry = ctk.CTkEntry(
            count_inner,
            width=250,
            height=38,
            font=ctk.CTkFont(size=14),
            justify="center",
            placeholder_text="Ej: 500"
        )
        self.count_entry.insert(0, "500")
        self.count_entry.pack(side="left", padx=(0, 10))
        
        count_help = ctk.CTkLabel(
            count_inner,
            text="(1 - 10,000)",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        count_help.pack(side="left")
        
        # --- Método de generación ---
        ctk.CTkLabel(
            config_frame,
            text="Método de generación:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=(15, 8))
        
        self.method_var = ctk.StringVar(value="stratified")
        
        method_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        method_frame.pack(fill="x", pady=(0, 10))
        
        # Radio buttons más visibles
        stratified_radio = ctk.CTkRadioButton(
            method_frame,
            text="Estratificado (Recomendado) ⭐",
            variable=self.method_var,
            value="stratified",
            font=ctk.CTkFont(size=12),
            command=self._update_method_info
        )
        stratified_radio.pack(pady=5)
        
        simple_radio = ctk.CTkRadioButton(
            method_frame,
            text="Aleatorio Simple",
            variable=self.method_var,
            value="simple",
            font=ctk.CTkFont(size=12),
            command=self._update_method_info
        )
        simple_radio.pack(pady=5)
        
        # Info del método
        self.method_info = ctk.CTkLabel(
            config_frame,
            text="Respeta la distribución real del mercado (40% Kölbi, 35% Telefónica, 25% Claro)",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            wraplength=700
        )
        self.method_info.pack(pady=(0, 15))
        
        # --- Auto-importar ---
        self.auto_import_var = ctk.BooleanVar(value=True)
        auto_check = ctk.CTkCheckBox(
            config_frame,
            text="✓ Importar automáticamente a la base de datos",
            variable=self.auto_import_var,
            font=ctk.CTkFont(size=12)
        )
        auto_check.pack(pady=(0, 15))
    
    def _build_buttons(self, parent):
        """Botones de acción"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 20))
        
        # Botón Generar (principal)
        self.generate_btn = ctk.CTkButton(
            button_frame,
            text="🎲 Generar Números",
            command=self.generate_numbers,
            height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60",
            text_color="white"
        )
        self.generate_btn.pack(fill="x", pady=(0, 10))
        
        # Botones secundarios
        secondary_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
        secondary_frame.pack(fill="x", pady=(0, 10))
        
        self.download_csv_btn = ctk.CTkButton(
            secondary_frame,
            text="💾 CSV",
            command=lambda: self.download_file('csv'),
            height=38,
            font=ctk.CTkFont(size=12),
            state="disabled"
        )
        self.download_csv_btn.pack(side="left", expand=True, padx=(0, 5))
        
        self.download_json_btn = ctk.CTkButton(
            secondary_frame,
            text="💾 JSON",
            command=lambda: self.download_file('json'),
            height=38,
            font=ctk.CTkFont(size=12),
            state="disabled"
        )
        self.download_json_btn.pack(side="left", expand=True, padx=(0, 5))
        
        self.copy_btn = ctk.CTkButton(
            secondary_frame,
            text="📋 Copiar JSON",
            command=self.copy_to_clipboard,
            height=38,
            font=ctk.CTkFont(size=12),
            state="disabled"
        )
        self.copy_btn.pack(side="left", expand=True)
    
    def _build_results_frame(self, parent):
        """Área de resultados"""
        result_label = ctk.CTkLabel(
            parent,
            text="Resultado:",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        result_label.pack(anchor="w", pady=(0, 8))
        
        # Textbox para resultados
        self.results_text = ctk.CTkTextbox(
            parent,
            font=ctk.CTkFont(size=10),
            wrap="none",
            height=150
        )
        self.results_text.pack(fill="both", expand=True, pady=(0, 10))
        
        # Mensaje inicial
        self.results_text.insert("1.0", "Presiona 'Generar Números' para comenzar...")
        self.results_text.configure(state="disabled")
    
    def _update_method_info(self):
        """Actualiza el texto descriptivo del método"""
        method = self.method_var.get()
        if method == "stratified":
            info = "Respeta la distribución real del mercado (40% Kölbi, 35% Telefónica, 25% Claro)"
        else:
            info = "Distribución completamente aleatoria, sin considerar cuota de mercado"
        self.method_info.configure(text=info)
    
    def generate_numbers(self):
        """Inicia la generación de números"""
        try:
            # Validar entrada
            count_str = self.count_entry.get().strip()
            if not count_str:
                messagebox.showerror("Error", "Ingresa la cantidad de números")
                return
            
            try:
                count = int(count_str)
            except ValueError:
                messagebox.showerror("Error", "La cantidad debe ser un número entero")
                return
            
            if count < 1:
                messagebox.showerror("Error", "La cantidad debe ser mayor a 0")
                return
            
            if count > 10000:
                messagebox.showerror("Error", "La cantidad no puede exceder 10,000")
                return
            
            # Iniciar generación en thread
            self.is_generating = True
            self.generate_btn.configure(state="disabled", text="⏳ Generando...")
            self.results_text.configure(state="normal")
            self.results_text.delete("1.0", "end")
            self.results_text.insert("1.0", f"⏳ Generando {count} números...\n")
            self.results_text.configure(state="disabled")
            
            # Deshabilitar descargas mientras genera
            self.download_csv_btn.configure(state="disabled")
            self.download_json_btn.configure(state="disabled")
            self.copy_btn.configure(state="disabled")
            
            thread = threading.Thread(
                target=self._generate_worker,
                args=(count, self.method_var.get(), self.auto_import_var.get()),
                daemon=True
            )
            thread.start()
            
        except Exception as e:
            logger.error(f"Error en generación: {e}")
            messagebox.showerror("Error", str(e))
            self.generate_btn.configure(state="normal", text="🎲 Generar Números")
            self.is_generating = False
    
    def _generate_worker(self, count, method, auto_import):
        """Worker thread para generar números sin bloquear UI"""
        try:
            response = requests.post(
                f"{self.server_url}/api/generate_contacts",
                json={
                    'count': count,
                    'method': method,
                    'auto_import': auto_import
                },
                headers={'X-API-Key': self.api_key},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.generated_contacts = result.get('contacts', [])
                    self.after(0, self._display_results, result)
                else:
                    error = result.get('error', 'Error desconocido')
                    self.after(0, self._show_error, error)
            else:
                self.after(
                    0,
                    self._show_error,
                    f"Error del servidor: {response.status_code} - {response.text}"
                )
                
        except requests.Timeout:
            self.after(0, self._show_error, "Timeout: la generación tardó demasiado")
        except requests.ConnectionError:
            self.after(0, self._show_error, "Error de conexión al servidor")
        except Exception as e:
            self.after(0, self._show_error, str(e))
        finally:
            self.is_generating = False
    
    def _display_results(self, result):
        """Muestra los resultados de la generación"""
        try:
            stats = result.get('statistics', {})
            
            # Actualizar textbox
            self.results_text.configure(state="normal")
            self.results_text.delete("1.0", "end")
            
            output = "✅ Generación completada!\n\n"
            output += f"Total: {stats.get('total', 0)} números\n"
            output += f"Método: {stats.get('method', 'desconocido').capitalize()}\n\n"
            
            # Distribución por operadora
            output += "Distribución por operadora:\n"
            output += "─" * 50 + "\n"
            
            by_operator = stats.get('by_operator', {})
            for operator in ['Kölbi', 'Telefónica', 'Claro']:
                data = by_operator.get(operator, {})
                count = data.get('count', 0)
                pct = data.get('percentage', 0)
                output += f"  {operator:15} {count:5} ({pct:5.1f}%)\n"
            
            # Info de importación
            if 'import_stats' in result:
                imp = result['import_stats']
                output += f"\n" + "=" * 50 + "\n"
                output += f"📥 Base de datos:\n"
                output += f"  ✓ Importados:  {imp.get('imported', 0)}\n"
                output += f"  ⚠ Duplicados:  {imp.get('duplicates', 0)}\n"
            
            # Primeros números
            output += f"\n" + "─" * 50 + "\n"
            output += "Primeros 5 números:\n\n"
            
            for i, contact in enumerate(self.generated_contacts[:5], 1):
                formatted = contact.get('formatted', contact.get('phone', 'N/A'))
                operator = contact.get('operator', 'N/A')
                output += f"  {i}. {formatted:15} ({operator})\n"
            
            self.results_text.insert("1.0", output)
            self.results_text.configure(state="disabled")
            
            # Habilitar descargas
            self.download_csv_btn.configure(state="normal")
            self.download_json_btn.configure(state="normal")
            self.copy_btn.configure(state="normal")
            self.generate_btn.configure(state="normal", text="🎲 Generar Números")
            
            messagebox.showinfo(
                "✓ Éxito",
                f"Se generaron {stats.get('total', 0)} números correctamente"
            )
            
        except Exception as e:
            logger.error(f"Error mostrando resultados: {e}")
            self._show_error(str(e))
    
    def _show_error(self, error_msg):
        """Muestra mensaje de error"""
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", f"❌ Error:\n{error_msg}")
        self.results_text.configure(state="disabled")
        
        self.generate_btn.configure(state="normal", text="🎲 Generar Números")
        messagebox.showerror("Error", error_msg)
    
    def copy_to_clipboard(self):
        """Copia los datos generados al portapapeles"""
        try:
            if not self.generated_contacts:
                messagebox.showwarning("Advertencia", "No hay números generados")
                return
            
            json_str = json.dumps(
                self.generated_contacts,
                ensure_ascii=False,
                indent=2
            )
            
            self.clipboard_clear()
            self.clipboard_append(json_str)
            self.update()
            
            messagebox.showinfo("✓ Éxito", "JSON copiado al portapapeles")
            
        except Exception as e:
            logger.error(f"Error copiando: {e}")
            messagebox.showerror("Error", f"Error copiando al portapapeles: {e}")
    
    def download_file(self, file_format):
        """Descarga archivo en formato especificado"""
        if not self.generated_contacts:
            messagebox.showwarning("Advertencia", "No hay números generados para descargar")
            return
        
        # Diálogo de guardado
        filename = filedialog.asksaveasfilename(
            defaultextension=f".{file_format}",
            filetypes=[(f"{file_format.upper()} files", f"*.{file_format}")],
            initialfile=f"contactos_{len(self.generated_contacts)}.{file_format}"
        )
        
        if not filename:
            return
        
        try:
            if file_format == 'csv':
                self._save_csv(filename)
            elif file_format == 'json':
                self._save_json(filename)
            
            messagebox.showinfo("✓ Éxito", f"Archivo guardado:\n{filename}")
            
        except Exception as e:
            logger.error(f"Error guardando archivo: {e}")
            messagebox.showerror("Error", f"Error guardando archivo: {e}")
    
    def _save_csv(self, filename):
        """Guarda los contactos en CSV"""
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ['phone', 'formatted', 'operator', 'name']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for contact in self.generated_contacts:
                # Normalizar campos
                row = {
                    'phone': contact.get('phone', ''),
                    'formatted': contact.get('formatted', contact.get('phone', '')),
                    'operator': contact.get('operator', ''),
                    'name': contact.get('name', '')
                }
                writer.writerow(row)
    
    def _save_json(self, filename):
        """Guarda los contactos en JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(
                self.generated_contacts,
                f,
                indent=2,
                ensure_ascii=False
            )
    
    def on_close(self):
        """Maneja el cierre de la ventana"""
        if self.is_generating:
            result = messagebox.askyesno(
                "En progreso",
                "Hay una generación en progreso. ¿Deseas cerrar de todas formas?"
            )
            if not result:
                return
        
        self.destroy()


# ========== INTEGRACIÓN CON call_manager_app.py ==========
# Agregar este método a la clase CallManagerApp:
#
# def open_phone_generator(self):
#     """Abre la ventana de generador de números"""
#     if not hasattr(self, 'generator_window') or not self.generator_window.winfo_exists():
#         self.generator_window = PhoneGeneratorWindow(
#             self,
#             self.server_url,
#             self.api_key
#         )
#         self.generator_window.focus()
#     else:
#         self.generator_window.focus()
#
# Agregar botón en build_ui():
#
# generator_btn = ctk.CTkButton(
#     top,
#     text='📱 Generar CR',
#     command=self.open_phone_generator,
#     width=120
# )
# generator_btn.pack(side='left', padx=4)
