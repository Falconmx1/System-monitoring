"""Utilidades varias"""

import json
import csv
import yaml
from typing import Dict, Any, List
from datetime import datetime
import os


def export_json(data: Dict[str, Any], filename: str = None) -> str:
    """Exporta datos a JSON"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"export_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    return filename


def export_csv(data: Dict[str, Any], filename: str = None) -> str:
    """Exporta datos a CSV (versión simplificada)"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"export_{timestamp}.csv"
    
    # Extraer métricas principales
    flat_data = {
        'timestamp': data.get('timestamp'),
        'hostname': data.get('hostname'),
        'cpu_percent': data.get('cpu', {}).get('percent'),
        'memory_percent': data.get('memory', {}).get('percent'),
        'memory_used': data.get('memory', {}).get('used'),
        'memory_available': data.get('memory', {}).get('available'),
    }
    
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=flat_data.keys())
        writer.writeheader()
        writer.writerow(flat_data)
    
    return filename


def load_config(config_path: str = 'config.yaml') -> Dict[str, Any]:
    """Carga configuración desde archivo YAML"""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"⚠️ Archivo de configuración {config_path} no encontrado. Usando valores por defecto.")
        return {}
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
        return {}


def save_config(config: Dict[str, Any], config_path: str = 'config.yaml') -> bool:
    """Guarda configuración en archivo YAML"""
    try:
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        return True
    except Exception as e:
        print(f"❌ Error guardando configuración: {e}")
        return False


def get_terminal_size():
    """Obtiene el tamaño de la terminal"""
    try:
        import shutil
        return shutil.get_terminal_size()
    except:
        return None


def clear_screen():
    """Limpia la pantalla de la terminal"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')
