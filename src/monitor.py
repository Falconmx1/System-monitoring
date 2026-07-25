"""Módulo para monitoreo del sistema"""

import psutil
import platform
import time
from datetime import datetime
from typing import Dict, List, Any


class SystemMonitor:
    """Clase principal para monitoreo del sistema"""
    
    def __init__(self):
        self.system = platform.system()
        self.node = platform.node()
        
    def get_cpu(self) -> Dict[str, Any]:
        """Obtiene métricas de CPU"""
        return {
            "percent": psutil.cpu_percent(interval=1),
            "cores": psutil.cpu_count(),
            "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            "per_cpu": psutil.cpu_percent(interval=0.5, percpu=True)
        }
    
    def get_memory(self) -> Dict[str, Any]:
        """Obtiene métricas de memoria"""
        mem = psutil.virtual_memory()
        return {
            "total": mem.total,
            "available": mem.available,
            "percent": mem.percent,
            "used": mem.used,
            "free": mem.free
        }
    
    def get_disk(self) -> List[Dict[str, Any]]:
        """Obtiene métricas de discos"""
        disks = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent
                })
            except PermissionError:
                continue
        return disks
    
    def get_network(self) -> Dict[str, Any]:
        """Obtiene métricas de red"""
        net = psutil.net_io_counters()
        return {
            "bytes_sent": net.bytes_sent,
            "bytes_recv": net.bytes_recv,
            "packets_sent": net.packets_sent,
            "packets_recv": net.packets_recv,
            "errin": net.errin,
            "errout": net.errout,
            "dropin": net.dropin,
            "dropout": net.dropout
        }
    
    def get_processes(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Obtiene los procesos con mayor uso de CPU"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Ordenar por uso de CPU y obtener top N
        processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        return processes[:top_n]
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Obtiene todas las métricas del sistema"""
        return {
            "timestamp": datetime.now().isoformat(),
            "system": self.system,
            "hostname": self.node,
            "cpu": self.get_cpu(),
            "memory": self.get_memory(),
            "disk": self.get_disk(),
            "network": self.get_network(),
            "processes": self.get_processes()
        }
    
    def format_metrics(self, metrics: Dict[str, Any]) -> str:
        """Formatea las métricas para mostrar en CLI"""
        output = []
        output.append(f"\n{'='*60}")
        output.append(f"📊 SYSTEM MONITOR - {metrics['hostname']} ({metrics['system']})")
        output.append(f"🕐 {metrics['timestamp']}")
        output.append(f"{'='*60}")
        
        # CPU
        cpu = metrics['cpu']
        output.append(f"\n💻 CPU:")
        output.append(f"  Uso: {cpu['percent']}%")
        output.append(f"  Núcleos: {cpu['cores']}")
        
        # Memoria
        mem = metrics['memory']
        output.append(f"\n🧠 MEMORIA:")
        output.append(f"  Uso: {mem['percent']}%")
        output.append(f"  Usado: {self._format_bytes(mem['used'])}")
        output.append(f"  Disponible: {self._format_bytes(mem['available'])}")
        output.append(f"  Total: {self._format_bytes(mem['total'])}")
        
        # Disco (primer disco)
        if metrics['disk']:
            disk = metrics['disk'][0]
            output.append(f"\n💾 DISCO ({disk['device']}):")
            output.append(f"  Uso: {disk['percent']}%")
            output.append(f"  Usado: {self._format_bytes(disk['used'])}")
            output.append(f"  Libre: {self._format_bytes(disk['free'])}")
        
        # Red
        net = metrics['network']
        output.append(f"\n🌐 RED:")
        output.append(f"  Enviado: {self._format_bytes(net['bytes_sent'])}")
        output.append(f"  Recibido: {self._format_bytes(net['bytes_recv'])}")
        
        # Procesos
        output.append(f"\n📋 TOP PROCESOS:")
        for i, proc in enumerate(metrics['processes'][:5], 1):
            output.append(f"  {i}. {proc.get('name', 'N/A')} - CPU: {proc.get('cpu_percent', 0):.1f}% | MEM: {proc.get('memory_percent', 0):.1f}%")
        
        output.append(f"\n{'='*60}")
        return "\n".join(output)
    
    @staticmethod
    def _format_bytes(bytes_val: int) -> str:
        """Formatea bytes a formato legible"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.2f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.2f} PB"
    
    def check_thresholds(self, metrics: Dict[str, Any], thresholds: Dict[str, int]) -> Dict[str, bool]:
        """Verifica si las métricas superan los umbrales"""
        alerts = {}
        
        if 'cpu' in thresholds:
            alerts['cpu'] = metrics['cpu']['percent'] > thresholds['cpu']
        
        if 'memory' in thresholds:
            alerts['memory'] = metrics['memory']['percent'] > thresholds['memory']
        
        if 'disk' in thresholds and metrics['disk']:
            alerts['disk'] = metrics['disk'][0]['percent'] > thresholds['disk']
        
        return alerts
