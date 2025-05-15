import sqlite3
from pathlib import Path
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MemoryOptimizer:
    """Optimizador del sistema de memoria y base de datos"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._create_indexes()
        
    def _create_indexes(self):
        """Crea índices adicionales para optimizar consultas"""
        with sqlite3.connect(str(self.db_path)) as conn:
            # Índice compuesto para búsquedas por categoría y timestamp
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_cat_time 
                ON memories(category, timestamp)
            """)
            
            # Índice compuesto para búsquedas por importancia y timestamp
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_imp_time
                ON memories(importance, timestamp) 
            """)
            
            # Índice para búsquedas por last_accessed
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_last_accessed
                ON memories(last_accessed)
            """)
            
            # Índice para relaciones
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_relations
                ON memory_relations(source_id, target_id, strength)
            """)
            
            logger.info("Índices de optimización creados")
            
    async def optimize_queries(self):
        """Optimiza la base de datos y recolecta estadísticas"""
        with sqlite3.connect(str(self.db_path)) as conn:
            # Analizar tablas
            conn.execute("ANALYZE memories")
            conn.execute("ANALYZE memory_relations")
            
            # Recolectar estadísticas
            cursor = conn.execute("ANALYZE sqlite_master")
            stats = cursor.fetchall()
            
            logger.info(f"Estadísticas de la base de datos actualizadas: {len(stats)} tablas analizadas")
            
    async def vacuum_database(self):
        """Limpia y optimiza el espacio de la base de datos"""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("VACUUM")
            logger.info("Base de datos optimizada y compactada")
            
    async def clean_old_memories(self, retention_days: int = 30):
        """Elimina memorias antiguas basado en el período de retención"""
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            with sqlite3.connect(str(self.db_path)) as conn:
                # Eliminar memorias antiguas
                cursor = conn.execute(
                    """
                    DELETE FROM memories 
                    WHERE timestamp < ? AND importance < 0.8
                    """, 
                    (cutoff_date,)
                )
                
                # Limpiar relaciones huérfanas
                conn.execute(
                    """
                    DELETE FROM memory_relations
                    WHERE source_id NOT IN (SELECT id FROM memories)
                    OR target_id NOT IN (SELECT id FROM memories)
                    """
                )
                
                deleted_count = cursor.rowcount
                logger.info(f"Eliminadas {deleted_count} memorias antiguas")
                
        except Exception as e:
            logger.error(f"Error limpiando memorias antiguas: {e}")
            raise
