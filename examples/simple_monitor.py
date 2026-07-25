"""Ejemplo simple de uso del monitor"""

from src.monitor import SystemMonitor
import time

def main():
    monitor = SystemMonitor()
    
    print("🔍 Monitoreo simple - 5 iteraciones\n")
    
    for i in range(5):
        metrics = monitor.get_all_metrics()
        
        print(f"📊 Iteración {i+1}")
        print(f"  CPU: {metrics['cpu']['percent']}%")
        print(f"  Memoria: {metrics['memory']['percent']}%")
        print(f"  Procesos: {len(metrics['processes'])} activos")
        print("-" * 30)
        
        time.sleep(2)

if __name__ == "__main__":
    main()
