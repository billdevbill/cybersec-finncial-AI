import sqlite3
import shutil
from pathlib import Path 
import logging
from datetime import datetime
import json
import gzip
import asyncio
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class MemoryBackup:
    """Sistema de respaldo para la base de datos de memoria"""
    
    def __init__(self, db_path: Path, backup_dir: Optional[Path] = None):
        self.db_path = db_path
        self.backup_dir = backup_dir or db_path.parent / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
    async def create_backup(self, compress: bool = True) -> Path:
        """Crea un backup completo de la base de datos"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"memory_backup_{timestamp}.db"
            backup_path = self.backup_dir / backup_name
            
            # Crear backup
            with sqlite3.connect(str(self.db_path)) as src_conn:
                # Backup en memoria primero
                memory_conn = sqlite3.connect(":memory:")
                src_conn.backup(memory_conn)
                
                # Guardar a archivo
                with sqlite3.connect(str(backup_path)) as dest_conn:
                    memory_conn.backup(dest_conn)
                    
            # Comprimir si es necesario
            if compress:
                compressed_path = backup_path.with_suffix(".db.gz")
                with open(backup_path, "rb") as f_in:
                    with gzip.open(compressed_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
                backup_path.unlink()  # Eliminar archivo sin comprimir
                backup_path = compressed_path
                
            logger.info(f"Backup creado en: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Error creando backup: {e}")
            raise
            
    async def restore_backup(self, backup_path: Path) -> bool:
        """Restaura la base de datos desde un backup"""
        try:
            # Descomprimir si es necesario
            if backup_path.suffix == ".gz":
                temp_path = backup_path.with_suffix("")
                with gzip.open(backup_path, "rb") as f_in:
                    with open(temp_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
                backup_path = temp_path
                
            # Crear backup temporal del actual
            temp_backup = await self.create_backup()
            
            try:
                # Restaurar desde backup
                with sqlite3.connect(str(backup_path)) as src_conn:
                    with sqlite3.connect(str(self.db_path)) as dest_conn:
                        src_conn.backup(dest_conn)
                        
                logger.info(f"Base de datos restaurada desde: {backup_path}")
                
                # Limpiar archivo temporal si era comprimido
                if backup_path != temp_path:
                    temp_path.unlink()
                    
                return True
                
            except Exception as e:
                # Restaurar backup temporal en caso de error
                logger.error(f"Error restaurando, revirtiendo cambios: {e}")
                await self.restore_backup(temp_backup)
                return False
                
        except Exception as e:
            logger.error(f"Error en proceso de restauración: {e}")
            raise
            
    async def schedule_backups(self, interval_hours: int = 24):
        """Programa backups automáticos periódicos"""
        while True:
            try:
                await self.create_backup()
                # Limpiar backups antiguos (mantener últimos 7)
                await self._cleanup_old_backups(keep=7)
                await asyncio.sleep(interval_hours * 3600)
            except Exception as e:
                logger.error(f"Error en backup programado: {e}")
                await asyncio.sleep(3600)  # Esperar 1 hora y reintentar
                
    async def _cleanup_old_backups(self, keep: int = 7):
        """Limpia backups antiguos manteniendo solo los más recientes"""
        try:
            backups = sorted(
                self.backup_dir.glob("memory_backup_*.db*"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            # Mantener solo los más recientes
            for backup in backups[keep:]:
                backup.unlink()
                logger.info(f"Backup antiguo eliminado: {backup}")
                
        except Exception as e:
            logger.error(f"Error limpiando backups antiguos: {e}")
            raise
