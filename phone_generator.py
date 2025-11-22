#!/usr/bin/env python3
"""
phone_generator.py - Generador de números telefónicos Costa Rica realistas
Basado en datos de operadores: Kölbi (40%), Telefónica (35%), Claro (25%)

Uso:
    from phone_generator import generate_cr_phones
    
    phones = generate_cr_phones(count=100, method='stratified')
    # Retorna: [{'number': '61234567', 'operator': 'Kölbi', 'formatted': '6123-4567'}, ...]
"""

import random
from typing import List, Dict, Literal

# Rangos de operadores Costa Rica
BANKS = {
    'telefonica': [
        {'min': 6000, 'max': 6100, 'weight': 0.20},
        {'min': 6100, 'max': 6200, 'weight': 0.20},
        {'min': 6200, 'max': 6300, 'weight': 0.20},
        {'min': 6300, 'max': 6400, 'weight': 0.20},
        {'min': 6400, 'max': 6500, 'weight': 0.20}
    ],
    'claro': [
        {'min': 7002, 'max': 7101, 'weight': 0.33},
        {'min': 7102, 'max': 7201, 'weight': 0.33},
        {'min': 7202, 'max': 7301, 'weight': 0.34}
    ],
    'ice': [  # Kölbi
        {'min': 8300, 'max': 8399, 'weight': 0.10},
        {'min': 8400, 'max': 8499, 'weight': 0.10},
        {'min': 8500, 'max': 8599, 'weight': 0.10},
        {'min': 8600, 'max': 8699, 'weight': 0.10},
        {'min': 8700, 'max': 8799, 'weight': 0.10},
        {'min': 8800, 'max': 8899, 'weight': 0.10},
        {'min': 8900, 'max': 8999, 'weight': 0.10},
        {'min': 8000, 'max': 8099, 'weight': 0.10},
        {'min': 8100, 'max': 8199, 'weight': 0.10},
        {'min': 8200, 'max': 8299, 'weight': 0.10}
    ]
}

# Distribución de mercado (porcentajes reales)
OPERATOR_DISTRIBUTION = {
    'Kölbi': 0.40,
    'Telefónica': 0.35,
    'Claro': 0.25
}

# Mapeo de operador a clave de banco
OPERATOR_TO_BANK = {
    'Kölbi': 'ice',
    'Telefónica': 'telefonica',
    'Claro': 'claro'
}


def generate_cr_phones(
    count: int = 500,
    method: Literal['stratified', 'simple', 'random'] = 'stratified'
) -> List[Dict[str, str]]:
    """
    Generar números telefónicos de Costa Rica realistas.
    
    Args:
        count: Cantidad de números a generar (default: 500)
        method: Método de generación:
            - 'stratified': Respetar distribución de mercado (recomendado)
            - 'simple': Dividir equitativamente entre operadores
            - 'random': Puramente aleatorio
    
    Returns:
        Lista de dicts con keys: 'number', 'operator', 'formatted'
        
    Example:
        >>> phones = generate_cr_phones(100, method='stratified')
        >>> phones[0]
        {'number': '81234567', 'operator': 'Kölbi', 'formatted': '8123-4567'}
    """
    generated_phones = []
    used_numbers = set()

    # Calcular distribución por operadora
    if method == 'stratified':
        # Respetar distribución real de mercado
        counts_by_op = {
            'Kölbi': int(count * OPERATOR_DISTRIBUTION['Kölbi']),
            'Telefónica': int(count * OPERATOR_DISTRIBUTION['Telefónica']),
            'Claro': int(count * OPERATOR_DISTRIBUTION['Claro'])
        }
        
        # Ajustar redondeo para llegar exactamente al total
        current_total = sum(counts_by_op.values())
        if current_total < count:
            counts_by_op['Kölbi'] += (count - current_total)
    
    elif method == 'simple':
        # Dividir equitativamente
        counts_by_op = {
            'Kölbi': count // 3,
            'Telefónica': count // 3,
            'Claro': count // 3 + (count % 3)
        }
    
    else:  # random
        # Aleatorio puro
        counts_by_op = {
            'Kölbi': random.randint(count // 4, count // 2),
            'Telefónica': random.randint(count // 4, count // 2),
            'Claro': 0
        }
        counts_by_op['Claro'] = count - counts_by_op['Kölbi'] - counts_by_op['Telefónica']

    # Generar números para cada operadora
    for operator, op_count in counts_by_op.items():
        op_key = OPERATOR_TO_BANK.get(operator, 'ice')
        op_banks = BANKS.get(op_key, [])
        
        if not op_banks:
            continue
        
        # Preparar pesos para random.choices
        weights = [b['weight'] for b in op_banks]
        
        for _ in range(op_count):
            attempts = 0
            while attempts < 100:
                # Seleccionar rango basado en peso
                selected_bank = random.choices(op_banks, weights=weights, k=1)[0]
                
                # Generar primeros 4 dígitos (prefijo)
                first_four = random.randint(selected_bank['min'], selected_bank['max'])
                
                # Generar últimos 4 dígitos
                last_four = random.randint(0, 9999)
                
                # Formular número (8 dígitos sin separadores)
                phone_number = f"{first_four:04d}{last_four:04d}"
                
                # Validar que no existe duplicado
                if phone_number not in used_numbers:
                    used_numbers.add(phone_number)
                    generated_phones.append({
                        'number': phone_number,
                        'operator': operator,
                        'formatted': f"{phone_number[:4]}-{phone_number[4:]}"
                    })
                    break
                
                attempts += 1
            
            # Si no pudo generar único después de 100 intentos, saltar
            if attempts >= 100:
                continue

    return generated_phones


def validate_cr_phone(phone_number: str) -> tuple[bool, str]:
    """
    Validar que un número telefónico es válido para Costa Rica.
    
    Args:
        phone_number: Número a validar (puede tener formato o sin format)
    
    Returns:
        Tuple (is_valid, operator_name or error_message)
    
    Example:
        >>> validate_cr_phone('8123-4567')
        (True, 'Kölbi')
        >>> validate_cr_phone('invalid')
        (False, 'Número no válido para Costa Rica')
    """
    import re
    
    # Limpiar número (remover formato)
    cleaned = re.sub(r'\D', '', phone_number)
    
    # Validar largo (8 dígitos)
    if len(cleaned) != 8:
        return False, "Número debe tener 8 dígitos"
    
    # Validar que son dígitos
    if not cleaned.isdigit():
        return False, "Número debe contener solo dígitos"
    
    first_four = int(cleaned[:4])
    
    # Verificar contra rangos conocidos
    for operator, op_banks in [('Kölbi', BANKS['ice']), 
                                ('Telefónica', BANKS['telefonica']), 
                                ('Claro', BANKS['claro'])]:
        for bank in op_banks:
            if bank['min'] <= first_four <= bank['max']:
                return True, operator
    
    return False, "Número no coincide con operadores conocidos"


if __name__ == '__main__':
    # Test del módulo
    print("🎲 Generando 50 números telefónicos Costa Rica...\n")
    
    phones = generate_cr_phones(count=50, method='stratified')
    
    # Agrupar por operador
    by_operator = {}
    for phone in phones:
        op = phone['operator']
        if op not in by_operator:
            by_operator[op] = []
        by_operator[op].append(phone)
    
    # Mostrar resumen
    for operator, numbers in by_operator.items():
        print(f"\n{operator}: {len(numbers)} números ({len(numbers)/len(phones)*100:.1f}%)")
        for num in numbers[:3]:
            print(f"  - {num['formatted']} ({num['number']})")
        if len(numbers) > 3:
            print(f"  ... y {len(numbers)-3} más")
    
    # Test de validación
    print("\n\n🔍 Testing validación:")
    test_numbers = ['8123-4567', '6200-5000', '7100-2000', '9999-9999']
    for num in test_numbers:
        valid, info = validate_cr_phone(num)
        status = "✅" if valid else "❌"
        print(f"{status} {num}: {info}")
