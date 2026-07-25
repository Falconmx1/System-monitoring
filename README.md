# System Monitoring Tool

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg)

Herramienta multiplataforma para monitoreo de sistemas Windows y Linux. Muestra CPU, memoria, disco, red y procesos en tiempo real. Interfaz CLI y web con alertas configurables. Ideal para administradores y DevOps.

## ✨ Características

- 📊 **Monitoreo en tiempo real**: CPU, Memoria, Disco, Red, Procesos
- 🖥️ **Multiplataforma**: Compatible con Windows y Linux
- 🎛️ **Múltiples interfaces**: CLI interactiva y Dashboard web
- 🔔 **Alertas configurables**: Email, Slack, Webhooks
- 💾 **Exportación de datos**: CSV y JSON
- ⚡ **Ligero y fácil de desplegar**

## 🚀 Inicio Rápido

```bash
# Clonar repositorio
git clone https://github.com/Falconmx1/System-monitoring.git
cd System-monitoring

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar (modo CLI)
python src/main.py

# O ejecutar servidor web
python src/main.py --web --port 5000

📋 Requisitos
Python 3.8 o superior

pip (gestor de paquetes)

🔧 Configuración
Copia config.example.yaml a config.yaml y ajusta los parámetros:
cp config.example.yaml config.yaml

📖 Uso
Modo CLI
python src/main.py
# Presiona 'q' para salir
# Presiona 'e' para exportar datos

Modo Web
python src/main.py --web
# Abre http://localhost:5000 en tu navegador

Alertas
Las alertas se disparan cuando las métricas superan los umbrales configurados en config.yaml.
