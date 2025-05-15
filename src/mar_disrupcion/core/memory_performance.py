import asyncio
import time
import logging
import random
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
import numpy as np
import json

from .memory_system import AdvancedMemorySystem
from .memory_optimizer import MemoryOptimizer

logger = logging.getLogger(__name__)

class MemoryPerformanceTest:
    """Tests de rendimiento para el sistema de memoria"""
    
    def __init__(self, memory_system: AdvancedMemorySystem):
        self.memory_system = memory_system
        self.optimizer = MemoryOptimizer(memory_system.db_path)
        
    async def run_performance_test(self, num_samples: int = 1000):
        """Ejecuta una batería completa de tests de rendimiento"""
        results = {
            "write_speed": [],
            "read_speed": [],
            "query_speed": [],
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        # Generar datos de prueba
        test_data = self._generate_test_data(num_samples)
        
        # Test de escritura
        start_time = time.time()
        for data in test_data:
            memory_id = await self.memory_system.store_memory(
                content=data["content"],
                category=data["category"],
                importance=data["importance"]
            )
            write_time = time.time() - start_time
            results["write_speed"].append(write_time)
            start_time = time.time()
            
        # Test de lectura
        start_time = time.time()
        categories = list(set(d["category"] for d in test_data))
        for category in categories:
            memories = await self.memory_system.retrieve_memories(
                category=category,
                limit=50,
                min_importance=0.3
            )
            read_time = time.time() - start_time
            results["read_speed"].append(read_time)
            start_time = time.time()
            
            # Contar hits/misses de caché
            cache_stats = self._analyze_cache_performance(memories)
            results["cache_hits"] += cache_stats["hits"]
            results["cache_misses"] += cache_stats["misses"]
            
        # Test de consultas complejas
        query_times = await self._test_complex_queries()
        results["query_speed"] = query_times
        
        # Calcular estadísticas
        stats = self._calculate_statistics(results)
        
        return stats
        
    def _generate_test_data(self, num_samples: int) -> List[Dict]:
        """Genera datos sintéticos para pruebas"""
        categories = ["info", "error", "warning", "debug", "critical"]
        test_data = []
        
        for _ in range(num_samples):
            data = {
                "category": random.choice(categories),
                "content": {
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Test message {random.randint(1, 1000)}",
                    "value": random.random(),
                    "nested": {
                        "field1": random.randint(1, 100),
                        "field2": "test"
                    }
                },
                "importance": random.random()
            }
            test_data.append(data)
            
        return test_data
        
    async def _test_complex_queries(self) -> List[float]:
        """Prueba consultas complejas y mide tiempos"""
        query_times = []
        
        # Test de consultas con joins
        start_time = time.time()
        await self.memory_system.retrieve_memories(
            category="info",
            limit=100,
            min_importance=0.7,
            context_size=5
        )
        query_times.append(time.time() - start_time)
        
        # Test de búsqueda por embedding
        start_time = time.time()
        sample_content = self._generate_test_data(1)[0]["content"]
        embedding = self.memory_system._generate_embedding(sample_content)
        # TODO: Implementar búsqueda por similitud de embedding
        query_times.append(time.time() - start_time)
        
        return query_times
        
    def _analyze_cache_performance(self, memories: List[Dict]) -> Dict:
        """Analiza rendimiento del caché"""
        stats = {"hits": 0, "misses": 0}
        
        for memory in memories:
            if memory["id"] in self.memory_system.priority_cache:
                stats["hits"] += 1
            else:
                stats["misses"] += 1
                
        return stats
        
    def _calculate_statistics(self, results: Dict) -> Dict:
        """Calcula estadísticas de rendimiento"""
        stats = {
            "write_speed": {
                "mean": np.mean(results["write_speed"]),
                "std": np.std(results["write_speed"]),
                "min": min(results["write_speed"]),
                "max": max(results["write_speed"])
            },
            "read_speed": {
                "mean": np.mean(results["read_speed"]),
                "std": np.std(results["read_speed"]),
                "min": min(results["read_speed"]),
                "max": max(results["read_speed"])
            },
            "query_speed": {
                "mean": np.mean(results["query_speed"]),
                "std": np.std(results["query_speed"]),
                "min": min(results["query_speed"]),
                "max": max(results["query_speed"])
            },
            "cache_performance": {
                "hits": results["cache_hits"],
                "misses": results["cache_misses"],
                "hit_ratio": results["cache_hits"] / (results["cache_hits"] + results["cache_misses"])
            }
        }
        
        return stats
        
    async def benchmark_memory_usage(self) -> Dict:
        """Monitorea uso de memoria durante operaciones"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        stats = {
            "initial_memory": process.memory_info().rss,
            "peak_memory": 0,
            "final_memory": 0
        }
        
        # Ejecutar operaciones de prueba
        await self.run_performance_test(num_samples=500)
        
        stats["peak_memory"] = process.memory_info().rss
        stats["final_memory"] = process.memory_info().rss
        
        return stats
