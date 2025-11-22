# 💻 EJEMPLOS DE CÓDIGO - Sistema de Rastreo de Tiempo

## Índice de Ejemplos

1. [Inicialización Básica](#inicialización-básica)
2. [Rastrear una Llamada Única](#rastrear-una-llamada-única)
3. [Integración en Loop](#integración-en-loop)
4. [Callback para UI](#callback-para-ui)
5. [Obtener Historial](#obtener-historial)
6. [Queries en Base de Datos](#queries-en-base-de-datos)
7. [Reportes y Análisis](#reportes-y-análisis)
8. [Manejo de Errores](#manejo-de-errores)
9. [Exportar Datos](#exportar-datos)
10. [Dashboard Personalizado](#dashboard-personalizado)

---

## Inicialización Básica

### Opción 1: Usar la instancia global

```python
# client/call_manager_app.py ya lo hace:
from call_tracking import initialize_tracker

tracker = initialize_tracker(
    base_url="http://localhost:5000",
    api_key="dev-key-change-in-production"
)
```

### Opción 2: Crear instancia directa

```python
from call_tracking import CallTracker

tracker = CallTracker(
    base_url="http://localhost:5000",
    api_key="dev-key-change-in-production"
)
```

### Opción 3: Obtener la instancia global

```python
from call_tracking import get_tracker

# Si ya fue inicializada
tracker = get_tracker()

# Si aún no fue inicializada, falla
try:
    tracker = get_tracker()
except RuntimeError:
    print("Primero llamar initialize_tracker()")
```

---

## Rastrear una Llamada Única

### Flujo Completo Básico

```python
def make_call_to_customer(customer_id, phone_number):
    """Ejemplo: Hacer una llamada y rastrear duración"""
    
    from call_tracking import get_tracker
    tracker = get_tracker()
    
    try:
        # 1. Iniciar rastreo
        print(f"Llamando a {phone_number}...")
        call_id = tracker.start_call(
            contact_id=customer_id,
            contact_phone=phone_number
        )
        
        if not call_id:
            print("Error: No se pudo iniciar rastreo")
            return False
        
        print(f"Rastreo iniciado: {call_id}")
        
        # 2. Ejecutar llamada (tu código aquí)
        call_provider_manager.make_call(phone_number)
        
        # 3. Simular conversación
        time.sleep(30)  # En realidad sería mientras habla
        
        # 4. Finalizar rastreo
        metrics = tracker.end_call(
            status="COMPLETED",
            notes="Cliente satisfecho"
        )
        
        if metrics:
            print(f"✅ Llamada finalizada")
            print(f"   Duración: {metrics['duration_seconds']}s")
            print(f"   Nuevo promedio: {metrics['new_average']}s")
            return True
        else:
            print("Error finalizando llamada")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
```

---

## Integración en Loop

### Procesar Múltiples Llamadas

```python
def process_call_queue(customer_list):
    """Procesar lista de clientes y rastrear todas las llamadas"""
    
    from call_tracking import get_tracker
    tracker = get_tracker()
    
    results = []
    
    for customer in customer_list:
        customer_id = customer['id']
        phone = customer['phone']
        name = customer['name']
        
        print(f"\nLlamando a {name}...")
        
        # Iniciar
        call_id = tracker.start_call(
            contact_id=customer_id,
            contact_phone=phone
        )
        
        if not call_id:
            print(f"⚠️ No se pudo iniciar rastreo para {name}")
            continue
        
        try:
            # Simular llamada (en realidad sería make_call)
            import time
            duration = random.randint(60, 300)  # 1-5 minutos
            time.sleep(min(duration // 10, 10))  # Escalar para demo
            
            # Finalizar
            metrics = tracker.end_call("COMPLETED")
            
            if metrics:
                results.append({
                    'name': name,
                    'phone': phone,
                    'duration': metrics['duration_seconds'],
                    'status': 'SUCCESS'
                })
                print(f"✅ {name}: {metrics['duration_seconds']}s")
        
        except Exception as e:
            tracker.end_call("FAILED")
            results.append({
                'name': name,
                'phone': phone,
                'duration': 0,
                'status': 'FAILED'
            })
            print(f"❌ {name}: {e}")
    
    return results
```

---

## Callback para UI

### Actualizar Label en Tiempo Real

```python
import customtkinter as ctk
from call_tracking import CallTracker

class CallTimerUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Call Timer Demo")
        self.geometry("400x200")
        
        # Label para mostrar tiempo
        self.lbl_timer = ctk.CTkLabel(
            self,
            text="00:00",
            font=("Consolas", 48, "bold"),
            text_color="#2ecc71"
        )
        self.lbl_timer.pack(pady=20)
        
        # Label para estado
        self.lbl_status = ctk.CTkLabel(
            self,
            text="Listo",
            font=("Segoe UI", 14)
        )
        self.lbl_status.pack()
        
        # Botones
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=20)
        
        btn_start = ctk.CTkButton(
            btn_frame,
            text="Iniciar Llamada",
            command=self.start_call,
            width=150
        )
        btn_start.pack(side="left", padx=10)
        
        btn_stop = ctk.CTkButton(
            btn_frame,
            text="Finalizar",
            command=self.end_call,
            width=150,
            fg_color="red"
        )
        btn_stop.pack(side="left", padx=10)
        
        # Inicializar tracker
        from call_tracking import initialize_tracker
        self.tracker = initialize_tracker(
            "http://localhost:5000",
            "dev-key-change-in-production"
        )
        
        # Registrar callback
        self.tracker.set_timer_callback(self._on_timer_update)
    
    def start_call(self):
        """Iniciar llamada"""
        call_id = self.tracker.start_call(
            contact_id="demo_contact",
            contact_phone="+506-5123-4567"
        )
        
        if call_id:
            self.lbl_status.configure(text="📞 Llamada activa...")
        else:
            self.lbl_status.configure(text="❌ Error iniciando")
    
    def end_call(self):
        """Finalizar llamada"""
        metrics = self.tracker.end_call("COMPLETED")
        
        if metrics:
            duration = metrics['duration_seconds']
            self.lbl_status.configure(
                text=f"✅ Duración: {duration}s"
            )
        else:
            self.lbl_status.configure(text="❌ Error finalizando")
    
    def _on_timer_update(self, duration_seconds, formatted_time):
        """Callback que se ejecuta cada segundo"""
        
        # Cambiar color según duración
        if duration_seconds > 300:  # > 5 minutos
            color = "#e74c3c"  # Rojo
        elif duration_seconds > 120:  # > 2 minutos
            color = "#f39c12"  # Amarillo
        else:
            color = "#2ecc71"  # Verde
        
        # Actualizar UI
        self.lbl_timer.configure(
            text=formatted_time,
            text_color=color
        )

if __name__ == "__main__":
    app = CallTimerUI()
    app.mainloop()
```

---

## Obtener Historial

### Historial Local

```python
def show_local_history():
    """Mostrar historial de sesiones locales"""
    
    from call_tracking import get_tracker
    tracker = get_tracker()
    
    # Obtener últimas 10 sesiones
    history = tracker.get_session_history(limit=10)
    
    print("\n📞 HISTORIAL LOCAL DE LLAMADAS\n")
    print(f"{'Call ID':<40} {'Contact':<20} {'Duración':<10} {'Estado':<12}")
    print("-" * 82)
    
    for session in history:
        call_id = session['call_id'][:30] + "..." if len(session['call_id']) > 30 else session['call_id']
        contact = session['contact_id'][:20] if session['contact_id'] else "—"
        duration = f"{session['duration_seconds']}s"
        status = session['status']
        
        print(f"{call_id:<40} {contact:<20} {duration:<10} {status:<12}")

# Ejecutar
show_local_history()
```

### Historial en Servidor

```python
import requests

def get_server_history(start_date="2024-11-22", end_date="2024-11-22"):
    """Obtener historial completo del servidor"""
    
    headers = {
        'X-API-Key': 'dev-key-change-in-production'
    }
    
    response = requests.get(
        'http://localhost:5000/api/calls/log',
        params={
            'start_date': start_date,
            'end_date': end_date,
            'limit': 100
        },
        headers=headers
    )
    
    if response.status_code == 200:
        calls = response.json()
        
        print(f"\n📞 HISTORIAL DEL SERVIDOR ({len(calls)} llamadas)\n")
        print(f"{'Usuario':<20} {'Teléfono':<15} {'Duración':<10} {'Estado':<12} {'Hora':<10}")
        print("-" * 67)
        
        total_duration = 0
        
        for call in calls:
            user = call.get('user_id', '—')[:20]
            phone = call.get('contact_phone', '—')[:15]
            duration = call.get('duration_seconds', 0)
            status = call.get('status', '—')
            
            # Parsear hora
            start_time = call.get('start_time', '')
            if start_time:
                from datetime import datetime
                try:
                    dt = datetime.fromisoformat(start_time)
                    time_str = dt.strftime("%H:%M:%S")
                except:
                    time_str = "—"
            else:
                time_str = "—"
            
            duration_str = f"{duration}s"
            total_duration += duration
            
            print(f"{user:<20} {phone:<15} {duration_str:<10} {status:<12} {time_str:<10}")
        
        print("-" * 67)
        hours = total_duration // 3600
        minutes = (total_duration % 3600) // 60
        print(f"TOTAL: {hours}h {minutes}m ({total_duration}s)")
        
        return calls
    else:
        print(f"❌ Error: {response.status_code}")
        return []

# Ejecutar
calls = get_server_history()
```

---

## Queries en Base de Datos

### Queries SQL Directas (para análisis avanzado)

```python
from server import Session, CallLog, UserMetrics
from sqlalchemy import func
from datetime import datetime, timedelta

# Conexión a BD
db = Session()

# 1. Total de llamadas hoy
today = datetime.utcnow().date()
today_calls = db.query(CallLog).filter(
    func.date(CallLog.start_time) == today
).count()
print(f"Llamadas hoy: {today_calls}")

# 2. Duración promedio hoy
avg_today = db.query(func.avg(CallLog.duration_seconds)).filter(
    func.date(CallLog.start_time) == today
).scalar()
print(f"Duración promedio hoy: {avg_today}s")

# 3. Top 5 agentes por llamadas (hoy)
top_agents = db.query(
    CallLog.user_id,
    func.count(CallLog.id).label('call_count'),
    func.avg(CallLog.duration_seconds).label('avg_duration')
).filter(
    func.date(CallLog.start_time) == today
).group_by(
    CallLog.user_id
).order_by(
    func.count(CallLog.id).desc()
).limit(5).all()

print("\n🏆 TOP 5 AGENTES HOY:")
for user_id, count, avg_dur in top_agents:
    print(f"  {user_id}: {count} llamadas, {avg_dur:.0f}s promedio")

# 4. Llamadas fallidas
failed_calls = db.query(CallLog).filter(
    CallLog.status.in_(['FAILED', 'DROPPED'])
).count()
print(f"\nLlamadas fallidas: {failed_calls}")

# 5. Mayor llamada del día
longest_call = db.query(CallLog).filter(
    func.date(CallLog.start_time) == today
).order_by(
    CallLog.duration_seconds.desc()
).first()

if longest_call:
    print(f"Llamada más larga: {longest_call.duration_seconds}s ({longest_call.contact_phone})")

# Cerrar conexión
db.close()
```

---

## Reportes y Análisis

### Generar Reporte de Rendimiento

```python
import json
from datetime import datetime, timedelta

def generate_daily_report(date_str="2024-11-22"):
    """Generar reporte completo del día"""
    
    import requests
    
    headers = {'X-API-Key': 'dev-key-change-in-production'}
    
    # Obtener todas las llamadas del día
    response = requests.get(
        'http://localhost:5000/api/calls/log',
        params={
            'start_date': date_str,
            'end_date': date_str,
            'limit': 500
        },
        headers=headers
    )
    
    if response.status_code != 200:
        return None
    
    calls = response.json()
    
    # Analizar datos
    report = {
        'date': date_str,
        'total_calls': len(calls),
        'total_duration_seconds': 0,
        'avg_duration': 0,
        'successful_calls': 0,
        'failed_calls': 0,
        'success_rate': 0,
        'by_user': {},
        'by_status': {}
    }
    
    # Procesar cada llamada
    for call in calls:
        duration = call.get('duration_seconds', 0)
        status = call.get('status', 'UNKNOWN')
        user_id = call.get('user_id', 'UNKNOWN')
        
        # Totales
        report['total_duration_seconds'] += duration
        
        # Por estado
        if status == 'COMPLETED':
            report['successful_calls'] += 1
        else:
            report['failed_calls'] += 1
        
        # Por usuario
        if user_id not in report['by_user']:
            report['by_user'][user_id] = {
                'calls': 0,
                'duration': 0,
                'success': 0,
                'failed': 0
            }
        
        report['by_user'][user_id]['calls'] += 1
        report['by_user'][user_id]['duration'] += duration
        if status == 'COMPLETED':
            report['by_user'][user_id]['success'] += 1
        else:
            report['by_user'][user_id]['failed'] += 1
        
        # Por estado
        if status not in report['by_status']:
            report['by_status'][status] = 0
        report['by_status'][status] += 1
    
    # Calcular promedios
    if report['total_calls'] > 0:
        report['avg_duration'] = report['total_duration_seconds'] // report['total_calls']
        report['success_rate'] = (report['successful_calls'] / report['total_calls']) * 100
    
    return report

# Usar
report = generate_daily_report("2024-11-22")

print(f"\n📊 REPORTE DIARIO - {report['date']}\n")
print(f"Total de llamadas: {report['total_calls']}")
print(f"Llamadas exitosas: {report['successful_calls']}")
print(f"Llamadas fallidas: {report['failed_calls']}")
print(f"Tasa de éxito: {report['success_rate']:.1f}%")
print(f"Duración total: {report['total_duration_seconds']}s")
print(f"Duración promedio: {report['avg_duration']}s")

print(f"\n👥 POR USUARIO:")
for user_id, stats in report['by_user'].items():
    success_rate = (stats['success'] / stats['calls'] * 100) if stats['calls'] > 0 else 0
    avg = stats['duration'] // stats['calls'] if stats['calls'] > 0 else 0
    print(f"  {user_id}:")
    print(f"    Llamadas: {stats['calls']} (éxito: {stats['success']}, fallidas: {stats['failed']})")
    print(f"    Duración promedio: {avg}s")
    print(f"    Tasa de éxito: {success_rate:.1f}%")
```

---

## Manejo de Errores

### Patrones de Error Comunes

```python
from call_tracking import CallTracker, get_tracker
import requests

def robust_call_tracking():
    """Ejemplo con manejo robusto de errores"""
    
    try:
        tracker = get_tracker()
    except RuntimeError:
        print("❌ CallTracker no inicializado")
        return False
    
    # 1. Iniciar llamada con retry
    max_retries = 3
    call_id = None
    
    for attempt in range(max_retries):
        try:
            call_id = tracker.start_call(
                contact_id="contact_123",
                contact_phone="+506-5123-4567"
            )
            
            if call_id:
                print(f"✅ Llamada iniciada en intento {attempt + 1}")
                break
        
        except requests.exceptions.ConnectionError:
            print(f"⚠️ Error de conexión, reintentando... ({attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                import time
                time.sleep(2 ** attempt)  # Exponential backoff
        
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            break
    
    if not call_id:
        print("❌ No se pudo iniciar llamada después de varios intentos")
        return False
    
    # 2. Finalizar con validación
    try:
        metrics = tracker.end_call("COMPLETED")
        
        if not metrics:
            print("⚠️ Llamada finalizada pero no se obtuvieron métricas")
            return False
        
        # Validar respuesta
        if 'duration_seconds' not in metrics:
            print("⚠️ Respuesta incompleta del servidor")
            return False
        
        duration = metrics['duration_seconds']
        
        if duration < 0:
            print(f"⚠️ Duración inválida: {duration}s")
            return False
        
        if duration == 0:
            print("⚠️ Duración es 0, verificar sincronización de tiempo")
        
        print(f"✅ Llamada completada en {duration}s")
        return True
    
    except Exception as e:
        print(f"❌ Error finalizando llamada: {e}")
        # Intentar registrar como fallida
        try:
            tracker.end_call("FAILED")
        except:
            pass
        return False
```

---

## Exportar Datos

### Exportar a CSV

```python
import csv
import requests
from datetime import datetime

def export_calls_to_csv(filename="calls_export.csv", start_date="2024-11-22"):
    """Exportar historial de llamadas a CSV"""
    
    headers = {'X-API-Key': 'dev-key-change-in-production'}
    
    # Obtener datos del servidor
    response = requests.get(
        'http://localhost:5000/api/calls/log',
        params={
            'start_date': start_date,
            'end_date': start_date,
            'limit': 1000
        },
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Error obteniendo datos: {response.status_code}")
        return False
    
    calls = response.json()
    
    # Escribir CSV
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Call ID',
                'Usuario',
                'Teléfono',
                'Duración (seg)',
                'Estado',
                'Fecha',
                'Hora Inicio',
                'Hora Fin'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for call in calls:
                start_time = call.get('start_time', '')
                end_time = call.get('end_time', '')
                
                # Parsear tiempos
                if start_time:
                    try:
                        dt = datetime.fromisoformat(start_time)
                        date_str = dt.strftime("%Y-%m-%d")
                        time_start = dt.strftime("%H:%M:%S")
                    except:
                        date_str = ""
                        time_start = ""
                else:
                    date_str = ""
                    time_start = ""
                
                if end_time:
                    try:
                        dt = datetime.fromisoformat(end_time)
                        time_end = dt.strftime("%H:%M:%S")
                    except:
                        time_end = ""
                else:
                    time_end = ""
                
                writer.writerow({
                    'Call ID': call.get('call_id', '')[:20],
                    'Usuario': call.get('user_id', ''),
                    'Teléfono': call.get('contact_phone', ''),
                    'Duración (seg)': call.get('duration_seconds', 0),
                    'Estado': call.get('status', ''),
                    'Fecha': date_str,
                    'Hora Inicio': time_start,
                    'Hora Fin': time_end
                })
        
        print(f"✅ Datos exportados a {filename}")
        return True
    
    except Exception as e:
        print(f"❌ Error escribiendo CSV: {e}")
        return False

# Usar
export_calls_to_csv("llamadas_2024-11-22.csv")
```

---

## Dashboard Personalizado

### Crear Dashboard Simple en Terminal

```python
def show_live_metrics():
    """Mostrar métricas en vivo en la terminal"""
    
    import requests
    import os
    import time
    
    headers = {'X-API-Key': 'dev-key-change-in-production'}
    
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("\n" + "=" * 60)
        print("📊 DASHBOARD EN VIVO - CallManager Metrics")
        print("=" * 60)
        print(f"Actualizado: {time.strftime('%H:%M:%S')}\n")
        
        # Obtener métricas
        try:
            response = requests.get(
                'http://localhost:5000/metrics/personal',
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                metrics = response.json()
                
                print(f"👤 Usuario: {metrics.get('username', '—')}")
                print(f"🔑 Role: {metrics.get('role', '—')}\n")
                
                calls_made = metrics.get('calls_made', 0)
                calls_success = metrics.get('calls_success', 0)
                calls_failed = metrics.get('calls_failed', 0)
                aht = metrics.get('avg_call_duration', 0)
                success_rate = metrics.get('success_rate', 0)
                
                print("📞 LLAMADAS:")
                print(f"   Total: {calls_made}")
                print(f"   Exitosas: {calls_success} ({success_rate:.1f}%)")
                print(f"   Fallidas: {calls_failed}")
                
                print(f"\n⏱️  DURACIONES:")
                mins = aht // 60
                secs = aht % 60
                print(f"   Promedio: {mins}m {secs}s")
                
                print("\n" + "-" * 60)
                print("Presiona Ctrl+C para salir | Actualiza cada 5 segundos")
                print("-" * 60)
        
        except Exception as e:
            print(f"❌ Error: {e}")
        
        try:
            time.sleep(5)
        except KeyboardInterrupt:
            print("\n👋 Dashboard cerrado")
            break

# Usar
if __name__ == "__main__":
    show_live_metrics()
```

---

## Conclusión

Estos ejemplos cubren los casos de uso más comunes:

✅ Inicialización y setup
✅ Rastreo de llamadas individuales
✅ Procesamiento en batch
✅ Integración con UI
✅ Historial y reportes
✅ Análisis avanzado
✅ Exportación de datos
✅ Manejo de errores
✅ Dashboards personalizados

**¡Todos listos para copiar y adaptar a tu código!**
