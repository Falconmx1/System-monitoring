"""Servidor web para dashboard"""

from flask import Flask, render_template_string, jsonify
from monitor.core import SystemMonitor
import json
import threading
import time
from typing import Dict, Any

app = Flask(__name__)
monitor = SystemMonitor()
cache = {}
cache_lock = threading.Lock()


# HTML Template para el dashboard
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>System Monitor Dashboard</title>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="5">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a2e; color: #eee; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { text-align: center; color: #00d2ff; margin-bottom: 30px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { background: #16213e; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .card h3 { color: #00d2ff; margin-bottom: 15px; border-bottom: 1px solid #333; padding-bottom: 10px; }
        .metric { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #1a1a2e; }
        .metric .label { color: #aaa; }
        .metric .value { font-weight: bold; }
        .value.good { color: #4caf50; }
        .value.warning { color: #ff9800; }
        .value.danger { color: #f44336; }
        .bar { height: 20px; background: #1a1a2e; border-radius: 10px; margin: 10px 0; overflow: hidden; }
        .bar-fill { height: 100%; border-radius: 10px; transition: width 0.5s; }
        .bar-fill.good { background: #4caf50; }
        .bar-fill.warning { background: #ff9800; }
        .bar-fill.danger { background: #f44336; }
        .footer { text-align: center; margin-top: 30px; color: #666; font-size: 14px; }
        .process-list { max-height: 200px; overflow-y: auto; }
        .process-item { padding: 4px 0; border-bottom: 1px solid #1a1a2e; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🖥️ System Monitor Dashboard</h1>
        <div class="grid">
            <div class="card">
                <h3>💻 CPU</h3>
                <div class="metric"><span class="label">Uso:</span><span class="value" id="cpu-percent">{{ cpu.percent }}%</span></div>
                <div class="bar"><div class="bar-fill {{ 'good' if cpu.percent < 70 else 'warning' if cpu.percent < 85 else 'danger' }}" style="width: {{ cpu.percent }}%"></div></div>
                <div class="metric"><span class="label">Núcleos:</span><span class="value">{{ cpu.cores }}</span></div>
                <div class="metric"><span class="label">Frecuencia:</span><span class="value">{{ cpu.frequency.current if cpu.frequency else 'N/A' }} MHz</span></div>
            </div>
            
            <div class="card">
                <h3>🧠 Memoria</h3>
                <div class="metric"><span class="label">Uso:</span><span class="value" id="memory-percent">{{ memory.percent }}%</span></div>
                <div class="bar"><div class="bar-fill {{ 'good' if memory.percent < 75 else 'warning' if memory.percent < 90 else 'danger' }}" style="width: {{ memory.percent }}%"></div></div>
                <div class="metric"><span class="label">Usado:</span><span class="value">{{ (memory.used / (1024**3)) | round(2) }} GB</span></div>
                <div class="metric"><span class="label">Disponible:</span><span class="value">{{ (memory.available / (1024**3)) | round(2) }} GB</span></div>
                <div class="metric"><span class="label">Total:</span><span class="value">{{ (memory.total / (1024**3)) | round(2) }} GB</span></div>
            </div>
            
            <div class="card">
                <h3>💾 Disco</h3>
                <div class="metric"><span class="label">Uso:</span><span class="value" id="disk-percent">{{ disk[0].percent if disk else 0 }}%</span></div>
                <div class="bar"><div class="bar-fill {{ 'good' if (disk[0].percent if disk else 0) < 80 else 'warning' if (disk[0].percent if disk else 0) < 90 else 'danger' }}" style="width: {{ disk[0].percent if disk else 0 }}%"></div></div>
                <div class="metric"><span class="label">Usado:</span><span class="value">{{ (disk[0].used / (1024**3)) | round(2) if disk else 0 }} GB</span></div>
                <div class="metric"><span class="label">Libre:</span><span class="value">{{ (disk[0].free / (1024**3)) | round(2) if disk else 0 }} GB</span></div>
                <div class="metric"><span class="label">Total:</span><span class="value">{{ (disk[0].total / (1024**3)) | round(2) if disk else 0 }} GB</span></div>
            </div>
            
            <div class="card">
                <h3>🌐 Red</h3>
                <div class="metric"><span class="label">Enviado:</span><span class="value">{{ (network.bytes_sent / (1024**2)) | round(2) if network else 0 }} MB</span></div>
                <div class="metric"><span class="label">Recibido:</span><span class="value">{{ (network.bytes_recv / (1024**2)) | round(2) if network else 0 }} MB</span></div>
                <div class="metric"><span class="label">Paquetes enviados:</span><span class="value">{{ network.packets_sent if network else 0 }}</span></div>
                <div class="metric"><span class="label">Paquetes recibidos:</span><span class="value">{{ network.packets_recv if network else 0 }}</span></div>
            </div>
            
            <div class="card" style="grid-column: span 2;">
                <h3>📋 Top Procesos</h3>
                <div class="process-list">
                {% for proc in processes %}
                    <div class="process-item">
                        <span>{{ loop.index }}. {{ proc.name }}</span>
                        <span style="float: right;">CPU: {{ proc.cpu_percent | round(1) }}% | MEM: {{ proc.memory_percent | round(1) }}%</span>
                    </div>
                {% endfor %}
                </div>
            </div>
        </div>
        <div class="footer">
            Host: {{ hostname }} | Sistema: {{ system }} | Última actualización: {{ timestamp }}
        </div>
    </div>
</body>
</html>
"""


def update_cache():
    """Actualiza el caché de métricas en segundo plano"""
    global cache
    while True:
        try:
            metrics = monitor.get_all_metrics()
            with cache_lock:
                cache = metrics
        except Exception as e:
            print(f"Error actualizando caché: {e}")
        time.sleep(2)  # Actualizar cada 2 segundos


@app.route('/')
def dashboard():
    """Renderiza el dashboard"""
    with cache_lock:
        metrics = cache.copy() if cache else monitor.get_all_metrics()
    
    if not metrics:
        return "Error cargando métricas", 500
    
    return render_template_string(DASHBOARD_TEMPLATE, **metrics)


@app.route('/api/metrics')
def api_metrics():
    """Endpoint API para métricas en JSON"""
    with cache_lock:
        metrics = cache.copy() if cache else monitor.get_all_metrics()
    return jsonify(metrics)


def start_server(host='0.0.0.0', port=5000, debug=False):
    """Inicia el servidor web"""
    # Iniciar hilo de actualización
    thread = threading.Thread(target=update_cache, daemon=True)
    thread.start()
    
    # Iniciar servidor
    app.run(host=host, port=port, debug=debug)
