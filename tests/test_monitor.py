"""Pruebas unitarias para el módulo de monitoreo"""

import unittest
from src.monitor import SystemMonitor


class TestSystemMonitor(unittest.TestCase):
    
    def setUp(self):
        self.monitor = SystemMonitor()
    
    def test_get_cpu(self):
        cpu = self.monitor.get_cpu()
        self.assertIn('percent', cpu)
        self.assertIn('cores', cpu)
        self.assertIsInstance(cpu['percent'], (int, float))
    
    def test_get_memory(self):
        mem = self.monitor.get_memory()
        self.assertIn('percent', mem)
        self.assertIn('total', mem)
        self.assertIn('available', mem)
    
    def test_get_disk(self):
        disks = self.monitor.get_disk()
        self.assertIsInstance(disks, list)
        if disks:
            self.assertIn('device', disks[0])
            self.assertIn('percent', disks[0])
    
    def test_get_network(self):
        net = self.monitor.get_network()
        self.assertIn('bytes_sent', net)
        self.assertIn('bytes_recv', net)
    
    def test_format_bytes(self):
        self.assertEqual(self.monitor._format_bytes(1024), "1.00 KB")
        self.assertEqual(self.monitor._format_bytes(1048576), "1.00 MB")
        self.assertEqual(self.monitor._format_bytes(0), "0.00 B")


if __name__ == '__main__':
    unittest.main()
