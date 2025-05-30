import numpy as np
import torch
import pickle
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
import logging
import time
from cachetools import TTLCache

logger = logging.getLogger(__name__)

class AdvancedMemorySystem:
    def __init__(
        self,
        config: Dict,
        db_path: Optional[str] = None
    ):
        """
        Inicializa el sistema de memoria avanzado.
        
        Args:
            config: Diccionario con la configuración del sistema
            db_path: Ruta opcional a la base de datos. Si no se proporciona,
                    se usa la ruta por defecto en la carpeta memory.
        """
        # Cargar configuración
        memory_config = config["memory"]
        neural_config = config["neural"]
        
        # Configuración de memoria
        self.retention_period = memory_config["retention_period"]
        self.context_depth = memory_config["context_depth"]
        self.confidence_threshold = memory_config["confidence_threshold"]
        self.cache_size = memory_config["cache_size"]
        
        # Configuración de la red neuronal
        self.learning_rate = neural_config["learning_rate"]
        self.lstm_hidden_size = neural_config["lstm_hidden_size"]
        self.lstm_num_layers = neural_config["lstm_num_layers"]
        self.dropout_rate = neural_config["dropout_rate"]
        
        # Sistema de caché mejorado con TTL y prioridad
        self.priority_cache = TTLCache(
            maxsize=self.cache_size,
            ttl=self.retention_period,
            timer=time.time
        )
        self.cache_priorities = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Inicializar métricas de caché
        self.cache_metrics = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "size": 0
        }
        
        # Configuración LSTM
        self.neural_memory = torch.nn.LSTM(
            input_size=512,
            hidden_size=self.lstm_hidden_size,
            num_layers=self.lstm_num_layers,
            dropout=self.dropout_rate,
            batch_first=True
        )
        
        # Optimizador
        self.optimizer = torch.optim.Adam(
            self.neural_memory.parameters(),
            lr=self.learning_rate
        )
        
        # Inicializar base de datos
        self.db_path = Path("memory/system_memory.db")
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
        
        logger.info("Sistema de memoria avanzado inicializado")
    
    def _init_database(self):
        """Inicializa la base de datos de memoria persistente."""
        with sqlite3.connect(str(self.db_path)) as conn:
            # Tabla principal de memorias
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    category TEXT,
                    content BLOB,
                    importance REAL,
                    timestamp DATETIME,
                    last_accessed DATETIME,
                    access_count INTEGER,
                    embedding BLOB
                )
            """)
            
            # Tabla de relaciones entre memorias
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_relations (
                    source_id TEXT,
                    target_id TEXT,
                    relation_type TEXT,
                    strength REAL,
                    PRIMARY KEY (source_id, target_id),
                    FOREIGN KEY (source_id) REFERENCES memories(id),
                    FOREIGN KEY (target_id) REFERENCES memories(id)
                )
            """)
            
            # Índices para optimización
            conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON memories(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)")
    
    async def store_memory(
        self,
        content: Any,
        category: str,
        importance: float = 0.5,
        related_to: Optional[str] = None
    ) -> str:
        """Almacena una nueva memoria con sistema de prioridad y relaciones."""
        try:
            memory_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
            
            # Generar embedding para el contenido
            embedding = self._generate_embedding(content)
            
            # Codificar contenido y embedding
            encoded_content = pickle.dumps(content)
            encoded_embedding = pickle.dumps(embedding)
            
            with sqlite3.connect(str(self.db_path)) as conn:
                # Almacenar memoria
                conn.execute(
                    """
                    INSERT INTO memories 
                    (id, category, content, importance, timestamp, 
                    last_accessed, access_count, embedding)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (memory_id, category, encoded_content, importance,
                     datetime.now(), datetime.now(), 0, encoded_embedding)
                )
                
                # Establecer relación si existe
                if related_to:
                    conn.execute(
                        """
                        INSERT INTO memory_relations 
                        (source_id, target_id, relation_type, strength)
                        VALUES (?, ?, 'related', ?)
                        """,
                        (memory_id, related_to, importance)
                    )
            
            # Actualizar caché si es importante
            if importance > self.confidence_threshold:
                self._update_cache(memory_id, content, importance)
            
            return memory_id
            
        except Exception as e:
            logger.error(f"Error almacenando memoria: {e}")
            raise
    
    async def retrieve_memories(
        self,
        category: str,
        limit: int = 10,
        min_importance: float = 0.0,
        context_size: Optional[int] = None
    ) -> List[Dict]:
        """Recupera memorias con contexto y relaciones."""
        try:
            current_time = datetime.now()
            retention_limit = current_time - timedelta(seconds=self.retention_period)
            context_size = context_size or self.context_depth
            
            with sqlite3.connect(str(self.db_path)) as conn:
                # Obtener memorias principales
                cursor = conn.execute(
                    """
                    SELECT id, content, importance, timestamp, access_count, embedding
                    FROM memories
                    WHERE category = ? 
                    AND importance >= ?
                    AND timestamp >= ?
                    ORDER BY importance DESC, last_accessed DESC
                    LIMIT ?
                    """,
                    (category, min_importance, retention_limit, limit)
                )
                
                memories = []
                for row in cursor.fetchall():
                    memory_id, content, importance, timestamp, access_count, embedding = row
                    
                    # Decodificar contenido y embedding
                    decoded_content = pickle.loads(content)
                    decoded_embedding = pickle.loads(embedding)
                    
                    # Obtener memorias relacionadas
                    related_cursor = conn.execute(
                        """
                        SELECT m.* FROM memories m
                        JOIN memory_relations r ON m.id = r.target_id
                        WHERE r.source_id = ?
                        ORDER BY r.strength DESC
                        LIMIT ?
                        """,
                        (memory_id, context_size)
                    )
                    
                    related_memories = [
                        {
                            "id": r[0],
                            "content": pickle.loads(r[2]),
                            "importance": r[3]
                        }
                        for r in related_cursor.fetchall()
                    ]
                    
                    # Actualizar estadísticas de acceso
                    conn.execute(
                        """
                        UPDATE memories 
                        SET last_accessed = ?, access_count = access_count + 1
                        WHERE id = ?
                        """,
                        (current_time, memory_id)
                    )
                    
                    memories.append({
                        "id": memory_id,
                        "content": decoded_content,
                        "importance": importance,
                        "timestamp": timestamp,
                        "access_count": access_count + 1,
                        "embedding": decoded_embedding,
                        "related_memories": related_memories
                    })
            
            return memories
            
        except Exception as e:
            logger.error(f"Error recuperando memorias: {e}")
            raise
    
    def _update_cache(self, memory_id: str, content: Any, importance: float):
        """Actualiza el caché con sistema de prioridad y métricas"""
        try:
            if len(self.priority_cache) >= self.cache_size:
                # Política de reemplazo basada en importancia y antigüedad
                min_priority_key = min(
                    self.cache_priorities.items(),
                    key=lambda x: (x[1], self.priority_cache.get(x[0], {}).get("last_accessed", 0))
                )[0]
                
                # Registrar evicción
                self.cache_metrics["evictions"] += 1
                
                del self.priority_cache[min_priority_key]
                del self.cache_priorities[min_priority_key]
            
            current_time = time.time()
            self.priority_cache[memory_id] = {
                "content": content,
                "last_accessed": current_time
            }
            self.cache_priorities[memory_id] = importance
            self.cache_metrics["size"] = len(self.priority_cache)
            
        except Exception as e:
            logger.error(f"Error actualizando caché: {e}")
            raise
    
    async def get_from_cache(self, memory_id: str) -> Optional[Any]:
        """Intenta recuperar una memoria desde el caché"""
        try:
            if memory_id in self.priority_cache:
                self.cache_metrics["hits"] += 1
                cache_entry = self.priority_cache[memory_id]
                cache_entry["last_accessed"] = time.time()
                return cache_entry["content"]
            
            self.cache_metrics["misses"] += 1
            return None
            
        except Exception as e:
            logger.error(f"Error accediendo al caché: {e}")
            return None
    
    async def get_cache_metrics(self) -> Dict:
        """Retorna métricas actuales del sistema de caché"""
        return {
            **self.cache_metrics,
            "hit_ratio": self.cache_metrics["hits"] / 
                        (self.cache_metrics["hits"] + self.cache_metrics["misses"])
            if (self.cache_metrics["hits"] + self.cache_metrics["misses"]) > 0 
            else 0
        }
    
    async def clear_cache(self):
        """Limpia el caché y reinicia métricas"""
        self.priority_cache.clear()
        self.cache_priorities.clear()
        self.cache_metrics = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "size": 0
        }
        logger.info("Caché limpiado y métricas reiniciadas")
    
    def _generate_embedding(self, content: Any) -> np.ndarray:
        """Genera embedding para el contenido usando el modelo neuronal."""
        try:
            # Convertir contenido a tensor
            if isinstance(content, dict):
                tensor = torch.tensor(list(content.values()), dtype=torch.float32)
            elif isinstance(content, list):
                tensor = torch.tensor(content, dtype=torch.float32)
            else:
                tensor = torch.tensor([hash(str(content))], dtype=torch.float32)
            
            # Redimensionar para LSTM
            tensor = tensor.view(1, -1, 512)
            
            # Generar embedding
            with torch.no_grad():
                output, (h_n, c_n) = self.neural_memory(tensor)
                return h_n[-1].numpy()
                
        except Exception as e:
            logger.error(f"Error generando embedding: {e}")
            raise
    
    async def train_on_memories(
        self,
        category: str,
        epochs: int = 150,
        batch_size: int = 64
    ):
        """Entrena el sistema neuronal con memorias existentes."""
        try:
            memories = await self.retrieve_memories(
                category,
                limit=1000,
                min_importance=0.5
            )
            
            if not memories:
                logger.warning(f"No hay memorias para entrenar en categoría: {category}")
                return
            
            # Preparar datos
            X = torch.tensor([
                m["embedding"]
                for m in memories
            ], dtype=torch.float32)
            
            logger.info(f"Iniciando entrenamiento con {len(X)} memorias")
            
            for epoch in range(epochs):
                total_loss = 0
                for i in range(0, len(X), batch_size):
                    batch = X[i:i + batch_size]
                    
                    self.optimizer.zero_grad()
                    output, (h_n, c_n) = self.neural_memory(batch)
                    
                    # Pérdida de reconstrucción
                    loss = torch.nn.functional.mse_loss(output, batch)
                    loss.backward()
                    self.optimizer.step()
                    
                    total_loss += loss.item()
                
                if (epoch + 1) % 10 == 0:
                    avg_loss = total_loss/len(X)
                    logger.info(f"Epoch {epoch + 1}/{epochs}, Loss: {avg_loss:.4f}")
            
            logger.info("Entrenamiento completado")
            
        except Exception as e:
            logger.error(f"Error en entrenamiento: {e}")
            raise
