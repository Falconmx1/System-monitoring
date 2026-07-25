"""Punto de entrada principal"""

import sys
import os
import time
import argparse
from src.monitor import SystemMonitor
from src.alerts import AlertSystem
from src.utils import load_config, export_json, export_csv, clear_screen
from src.web_server import start_server
import threading
import keyboard
import json


def run_cli(config):
    """Ejecuta el modo CLI"""
    monitor = SystemMonitor()
    alert_system = AlertSystem(config)
    thresholds = config.get('thresholds', {})
    interval = config.get('interval', 5)
    
    print("🖥️ System Monitoring Tool - CLI Mode")
    print("Presiona 'q' para salir, 'e' para exportar datos\n")
    
    running = True
    while running:
        # Obtener métricas
        metrics = monitor.get_all_metrics()
        
        # Mostrar en pantalla
        clear_screen()
        print(monitor.format_metrics(metrics))
        
        # Verificar alertas
        if thresholds:
            alerts = monitor.check_thresholds(metrics, thresholds)
            if any(alerts.values()):
                alert_system.process_alerts(alerts, metrics)
                print("\n🔔 ¡ALERTAS ACTIVADAS!")
        
        # Esperar input o intervalo
        if keyboard.is_pressed('q'):
            running = False
            break
        elif keyboard.is_pressed('e'):
            export_json(metrics)
            export_csv(metrics)
            print("\n✅ Datos exportados a JSON y CSV")
            time.sleep(1)
        
        time.sleep(interval)


def run_web(config):
    """Ejecuta el modo web"""
    web_config = config.get('web', {})
    host = web_config.get('host', '0.0.0.0')
    port = web_config.get('port', 5000)
    debug = web_config.get('debug', False)
    
    print(f"🌐 Iniciando servidor web en http://{host}:{port}")
    print("Presiona Ctrl+C para detener")
    
    start_server(host=host, port=port, debug=debug)


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='System Monitoring Tool')
    parser.add_argument('--web', action='store_true', help='Iniciar en modo web')
    parser.add_argument('--port', type=int, default=5000, help='Puerto para el servidor web')
    parser.add_argument('--config', type=str, default='config.yaml', help='Archivo de configuración')
    args = parser.parse_args()
    
    # Cargar configuración
    config = load_config(args.config)
    if args.port:
        config.setdefault('web', {})['port'] = args.port
    
    try:
        if args.web:
            run_web(config)
        else:
            run_cli(config)
    except KeyboardInterrupt:
        print("\n\n👋 Saliendo del programa...")
        sys.exit(0)
    except Exception as e:
        print(f"
