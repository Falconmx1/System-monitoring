"""Módulo para sistema de alertas"""

import smtplib
import requests
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertSystem:
    """Sistema de alertas para notificaciones"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.alerts_history = []
    
    def send_email(self, subject: str, body: str) -> bool:
        """Envía alerta por email"""
        try:
            email_config = self.config.get('alerts', {}).get('email', {})
            if not email_config.get('enabled', False):
                return False
            
            msg = MIMEMultipart()
            msg['From'] = email_config['username']
            msg['To'] = email_config['to']
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email enviado a {email_config['to']}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            return False
    
    def send_slack(self, message: str) -> bool:
        """Envía alerta a Slack"""
        try:
            slack_config = self.config.get('alerts', {}).get('slack', {})
            if not slack_config.get('enabled', False):
                return False
            
            payload = {'text': message}
            response = requests.post(
                slack_config['webhook_url'],
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                logger.info("Alerta enviada a Slack")
                return True
            else:
                logger.error(f"Error en Slack: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error enviando a Slack: {e}")
            return False
    
    def send_webhook(self, data: Dict[str, Any]) -> bool:
        """Envía alerta por webhook"""
        try:
            webhook_config = self.config.get('alerts', {}).get('webhook', {})
            if not webhook_config.get('enabled', False):
                return False
            
            response = requests.post(
                webhook_config['url'],
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code in [200, 201, 202]:
                logger.info("Alerta enviada a webhook")
                return True
            else:
                logger.error(f"Error en webhook: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error enviando a webhook: {e}")
            return False
    
    def process_alerts(self, alerts: Dict[str, bool], metrics: Dict[str, Any]) -> None:
        """Procesa las alertas y envía notificaciones"""
        triggered = [key for key, value in alerts.items() if value]
        
        if not triggered:
            return
        
        # Construir mensaje
        message = f"🚨 *ALERTA DEL SISTEMA* 🚨\n"
        message += f"Host: {metrics.get('hostname', 'Unknown')}\n"
        message += f"Timestamp: {metrics.get('timestamp', 'N/A')}\n\n"
        
        for alert in triggered:
            if alert == 'cpu':
                message += f"⚠️ CPU: {metrics['cpu']['percent']}% (Umbral: {self.config.get('thresholds', {}).get('cpu', 80)}%)\n"
            elif alert == 'memory':
                message += f"⚠️ MEMORIA: {metrics['memory']['percent']}% (Umbral: {self.config.get('thresholds', {}).get('memory', 85)}%)\n"
            elif alert == 'disk':
                disk = metrics['disk'][0] if metrics['disk'] else None
                if disk:
                    message += f"⚠️ DISCO: {disk['percent']}% (Umbral: {self.config.get('thresholds', {}).get('disk', 90)}%)\n"
        
        # Registrar historial
        self.alerts_history.append({
            'timestamp': metrics['timestamp'],
            'alerts': triggered,
            'message': message
        })
        
        # Enviar por todos los canales configurados
        self.send_email("ALERTA - Sistema de Monitoreo", message)
        self.send_slack(message)
        self.send_webhook({
            'event': 'alert',
            'alerts': triggered,
            'metrics': metrics
        })
        
        logger.info(f"Alertas procesadas: {triggered}")
