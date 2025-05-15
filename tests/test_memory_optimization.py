import pytest
import asyncio
import logging
from pathlib import Path
from datetime import datetime, timedelta
import shutil

from src.mar_disrupcion.core.memory_system import AdvancedMemorySystem
from src.mar_disrupcion.core.memory_optimizer import MemoryOptimizer
from src.mar_disrupcion.core.memory_backup import MemoryBackup
from src.mar_disrupcion.core.memory_performance import MemoryPerformanceTest

logger = logging.getLogger(__name__)

@pytest.fixture
async def memory_system():
    """Fixture para el sistema de memoria de prueba"""
    config = {
        "memory": {
            "retention_period": 3600,
            "context_depth": 5,
            "confidence_threshold": 0.7,
            "cache_size": 1024
        },
        "neural": {
            "learning_rate": 0.001,
            "lstm_hidden_size": 256,
            "lstm_num_layers": 2,
            "dropout_rate": 0.2
        }
    }
    
    # Usar base de datos temporal para pruebas
    test_db = Path("test_memory.db")
    system = AdvancedMemorySystem(config, db_path=str(test_db))
    
    yield system
    
    # Limpiar después de las pruebas
    if test_db.exists():
        test_db.unlink()

@pytest.mark.asyncio
async def test_memory_optimization(memory_system):
    """Test de optimización del sistema de memoria"""
    optimizer = MemoryOptimizer(memory_system.db_path)
    
    # Probar creación de índices
    await optimizer.optimize_queries()
    await optimizer.vacuum_database()
    
    # Verificar que no hay errores en consultas optimizadas
    memories = await memory_system.retrieve_memories("test", limit=10)
    assert isinstance(memories, list)
    
    # Probar limpieza de memorias antiguas
    await optimizer.clean_old_memories(retention_days=1)

@pytest.mark.asyncio
async def test_backup_system(memory_system):
    """Test del sistema de backup"""
    backup_dir = Path("test_backups")
    backup_system = MemoryBackup(memory_system.db_path, backup_dir)
    
    try:
        # Crear algunos datos de prueba
        await memory_system.store_memory(
            content={"test": "data"},
            category="test",
            importance=0.8
        )
        
        # Crear backup
        backup_path = await backup_system.create_backup()
        assert backup_path.exists()
        
        # Modificar datos originales
        await memory_system.store_memory(
            content={"test": "modified"},
            category="test",
            importance=0.9
        )
        
        # Restaurar backup
        success = await backup_system.restore_backup(backup_path)
        assert success
        
        # Verificar restauración
        memories = await memory_system.retrieve_memories("test")
        assert len(memories) == 1
        assert memories[0]["content"]["test"] == "data"
        
    finally:
        # Limpiar archivos de prueba
        if backup_dir.exists():
            shutil.rmtree(backup_dir)

@pytest.mark.asyncio
async def test_performance_monitoring(memory_system):
    """Test del sistema de monitoreo de rendimiento"""
    perf_test = MemoryPerformanceTest(memory_system)
    
    # Ejecutar pruebas de rendimiento
    stats = await perf_test.run_performance_test(num_samples=100)
    
    # Verificar métricas
    assert "write_speed" in stats
    assert "read_speed" in stats
    assert "query_speed" in stats
    assert "cache_performance" in stats
    
    # Verificar métricas de caché
    cache_stats = await memory_system.get_cache_metrics()
    assert "hits" in cache_stats
    assert "misses" in cache_stats
    assert "hit_ratio" in cache_stats
    
    # Verificar benchmark de memoria
    memory_stats = await perf_test.benchmark_memory_usage()
    assert memory_stats["initial_memory"] > 0
    assert memory_stats["peak_memory"] >= memory_stats["initial_memory"]

@pytest.mark.asyncio
async def test_cache_integration(memory_system):
    """Test de integración del sistema de caché"""
    # Insertar datos de prueba
    test_data = {"test": "cache_data"}
    memory_id = await memory_system.store_memory(
        content=test_data,
        category="test",
        importance=0.9
    )
    
    # Verificar recuperación desde caché
    cached_data = await memory_system.get_from_cache(memory_id)
    assert cached_data == test_data
    
    # Verificar métricas de caché
    metrics = await memory_system.get_cache_metrics()
    assert metrics["hits"] > 0
    
    # Probar limpieza de caché
    await memory_system.clear_cache()
    metrics = await memory_system.get_cache_metrics()
    assert metrics["size"] == 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
