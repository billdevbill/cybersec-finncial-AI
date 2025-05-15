import asyncio
from scapy.all import *
import nmap
from typing import Dict, List, Optional
import logging
from concurrent.futures import ThreadPoolExecutor
import json

logger = logging.getLogger(__name__)

from core.metrics import SCAN_DURATION, record_security_alert
from core.config import config, logger

class AdvancedNetworkAnalyzer:
    def __init__(self, timeout: Optional[int] = None, buffer_size: Optional[int] = None, analysis_depth: Optional[int] = None):
        """
        Inicializa el analizador de red avanzado.
        
        Args:
            timeout: Tiempo máximo para análisis (segundos)
            buffer_size: Tamaño del buffer para captura
            analysis_depth: Profundidad del análisis
        """
        try:
            # Obtener configuración de seguridad
            self.timeout = timeout or int(config.get("DEEP_SCAN_TIMEOUT", 120))
            self.buffer_size = buffer_size or int(config.get("PACKET_CAPTURE_BUFFER", 8192))
            self.analysis_depth = analysis_depth or int(config.get("NETWORK_ANALYSIS_DEPTH", 3))
            
            # Configurar métricas
            self.scan_duration = SCAN_DURATION
            self.scan_counter = Counter('network_scans_total', 'Total network scans', ['scan_type', 'status'])
            self.vulnerability_counter = Counter('vulnerabilities_detected', 'Total vulnerabilities detected', ['severity'])
            
            # Inicializar escáner y executor
            self.nmap_scanner = nmap.PortScanner()
            self._executor = ThreadPoolExecutor(max_workers=int(config.get("SCAN_THREADS", 4)))
            
            logger.info("Network Analyzer inicializado",
                       timeout=self.timeout,
                       buffer_size=self.buffer_size,
                       analysis_depth=self.analysis_depth)
                       
        except Exception as e:
            logger.error("Error inicializando Network Analyzer", error=str(e), exc_info=True)
            raise RuntimeError(f"Error inicializando Network Analyzer: {str(e)}")      async def deep_scan(self, target: str) -> Dict:
        """Realiza un análisis profundo de la red y busca vulnerabilidades."""
        scan_start = datetime.now()
        
        try:
            logger.info("Iniciando análisis profundo de red", target=target)
            self.scan_counter.labels(scan_type='deep', status='started').inc()
            
            # Ejecutar escaneos en paralelo
            async with asyncio.TaskGroup() as group:
                port_scan_task = group.create_task(self._port_scan(target))
                vuln_scan_task = group.create_task(self._vulnerability_scan(target))
                traffic_task = group.create_task(self._traffic_analysis(target))
            
            results = {
                'port_scan': port_scan_task.result(),
                'vulnerabilities': vuln_scan_task.result(),
                'traffic_analysis': traffic_task.result()
            }
            
            # Registrar métricas
            scan_duration = (datetime.now() - scan_start).total_seconds()
            self.scan_duration.labels(scan_type='deep').observe(scan_duration)
            self.scan_counter.labels(scan_type='deep', status='completed').inc()
            
            # Registrar vulnerabilidades encontradas
            for vuln in results['vulnerabilities']:
                self.vulnerability_counter.labels(severity=vuln['severity']).inc()
                
            logger.info("Análisis profundo completado",
                       target=target,
                       duration=scan_duration,
                       vuln_count=len(results['vulnerabilities']))
            
            return results
            
        except asyncio.TimeoutError:
            self.scan_counter.labels(scan_type='deep', status='timeout').inc()
            logger.error("Timeout en análisis profundo",
                        target=target,
                        timeout=self.timeout)
            raise TimeoutError(f"El análisis excedió el tiempo límite de {self.timeout} segundos")
            
        except Exception as e:
            self.scan_counter.labels(scan_type='deep', status='error').inc()
            logger.error("Error en análisis profundo",
                        target=target,
                        error=str(e),
                        exc_info=True)
            raise RuntimeError(f"Error en análisis profundo: {str(e)}")
        logger.info("Iniciando análisis profundo", target=target)
        
        try:
            with SCAN_DURATION.labels(scan_type="deep").time():
                tasks = [
                    self._port_scan(target),
                    self._vulnerability_scan(target),
                    self._traffic_analysis(target)
                ]
                results = await asyncio.gather(*tasks)
                consolidated = self._consolidate_results(results)
                
                # Registrar alertas encontradas
                for vuln in consolidated.get("vulnerabilities", []):
                    record_security_alert(
                        severity=vuln.get("severity", "unknown"),
                        alert_type=vuln.get("type", "vulnerability")
                    )
                
                logger.info("Análisis profundo completado", 
                           target=target,
                           vulnerabilities_found=len(consolidated.get("vulnerabilities", [])))
                
                return consolidated
                
        except Exception as e:
            logger.error("Error en análisis profundo",
                        target=target,
                        error=str(e),
                        exc_info=True)
            raise

    async def _port_scan(self, target: str) -> Dict:
        """Escaneo de puertos asíncrono."""
        def _scan():
            return self.nmap_scanner.scan(target, arguments="-sS -sV -O")
        return await asyncio.get_event_loop().run_in_executor(self._executor, _scan)

    async def _vulnerability_scan(self, target: str) -> Dict:
        """Análisis de vulnerabilidades."""
        def _scan():
            return self.nmap_scanner.scan(target, arguments="-sC --script vuln")
        return await asyncio.get_event_loop().run_in_executor(self._executor, _scan)

    async def _traffic_analysis(self, target: str) -> Dict:
        """Análisis de tráfico de red."""
        packets = []
        def packet_callback(pkt):
            if len(packets) < self.buffer_size:
                packets.append(pkt.summary())
        
        try:
            sniff(filter=f"host {target}", prn=packet_callback, 
                  timeout=self.timeout, store=0)
            return {"packets": packets}
        except Exception as e:
            logger.error(f"Error en análisis de tráfico: {e}")
            return {"error": str(e)}

    def _consolidate_results(self, results: List[Dict]) -> Dict:
        """Consolida los resultados de diferentes análisis."""
        return {
            "port_scan": results[0],
            "vulnerabilities": results[1],
            "traffic_analysis": results[2],
            "analysis_timestamp": datetime.now().isoformat()
        }

class ParallelProcessor:
    def __init__(self, batch_size: int = 64):
        self.batch_size = batch_size
        self._executor = ThreadPoolExecutor(max_workers=8)
        
    async def process_batch(self, items: List, processor_func) -> List:
        """Procesa un lote de items en paralelo."""
        batches = [items[i:i + self.batch_size] 
                  for i in range(0, len(items), self.batch_size)]
        
        async def process_single_batch(batch):
            tasks = [self._process_item(item, processor_func) for item in batch]
            return await asyncio.gather(*tasks)
        
        results = []
        for batch in batches:
            batch_results = await process_single_batch(batch)
            results.extend(batch_results)
        return results
    
    async def _process_item(self, item, processor_func):
        """Procesa un único item."""
        try:
            return await asyncio.get_event_loop().run_in_executor(
                self._executor, processor_func, item
            )
        except Exception as e:
            logger.error(f"Error procesando item: {e}")
            return {"error": str(e), "item": item}
