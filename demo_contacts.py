"""
demo_contacts.py - Generar contactos de prueba para demo
"""
import json

# Generar 50 contactos de prueba para Costa Rica
demo_contacts = [
    {"phone": "+506-5001-0001", "name": "Juan García", "status": "NC", "note": "Sin contestar"},
    {"phone": "+506-5001-0002", "name": "María López", "status": "CUELGA", "note": "Cuelga llamadas"},
    {"phone": "+506-5001-0003", "name": "Carlos Ruiz", "status": "SIN_GESTIONAR", "note": "Nuevo"},
    {"phone": "+506-5001-0004", "name": "Ana Martínez", "status": "INTERESADO", "note": "Interesado en servicios"},
    {"phone": "+506-5001-0005", "name": "Pedro Flores", "status": "SERVICIOS_ACTIVOS", "note": "Cliente activo"},
    {"phone": "+506-5001-0006", "name": "Rosa González", "status": "NC", "note": "NC"},
    {"phone": "+506-5001-0007", "name": "Luis Torres", "status": "CUELGA", "note": "Cuelga"},
    {"phone": "+506-5001-0008", "name": "Diego Soto", "status": "SIN_GESTIONAR", "note": "Pendiente"},
    {"phone": "+506-5001-0009", "name": "Elena Ruiz", "status": "INTERESADO", "note": "Posible venta"},
    {"phone": "+506-5001-0010", "name": "Fernando López", "status": "SERVICIOS_ACTIVOS", "note": "VIP"},
    {"phone": "+506-5001-0011", "name": "Gabriela Sánchez", "status": "NC", "note": "Sin respuesta"},
    {"phone": "+506-5001-0012", "name": "Héctor Vargas", "status": "CUELGA", "note": "Rechaza llamadas"},
    {"phone": "+506-5001-0013", "name": "Iris Ramírez", "status": "SIN_GESTIONAR", "note": "Base fría"},
    {"phone": "+506-5001-0014", "name": "Javier Moreno", "status": "INTERESADO", "note": "Cotización pendiente"},
    {"phone": "+506-5001-0015", "name": "Karen Díaz", "status": "SERVICIOS_ACTIVOS", "note": "Renovación próxima"},
]

if __name__ == '__main__':
    # Guardar como JSON para importar
    with open('demo_contacts.json', 'w', encoding='utf-8') as f:
        json.dump(demo_contacts, f, ensure_ascii=False, indent=2)
    
    # Guardar como CSV también
    import csv
    with open('demo_contacts.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['phone', 'name', 'status', 'note'])
        writer.writeheader()
        writer.writerows(demo_contacts)
    
    print(f"✅ Creados {len(demo_contacts)} contactos de prueba")
    print("   📄 demo_contacts.json")
    print("   📄 demo_contacts.csv")
    print("\nPuedes importarlos en la app usando 📥 Importar Excel")
