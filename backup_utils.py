import sqlite3
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from logger_utils import logger

from app_paths import DB_PATH, BACKUP_DIR, ensure_directories

ensure_directories()

'''
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "products.db"
BACKUP_DIR = BASE_DIR / "backups"
'''


def backup_database():
    """ 使用 SQLitet 在线备份接口创建数据库备份 """
    
    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True
    )
    
    if not DB_PATH.is_file():
        raise FileNotFoundError(
            f"数据库文件不存在： {DB_PATH}"
        )
        
    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )
    
    # 加随机后缀，避免同一秒内重复备份时覆盖文件
    backup_path = (
        BACKUP_DIR /
        f"products_{timestamp}_{uuid4().hex[:8]}.db"
    )
    
    try:
        with sqlite3.connect(DB_PATH) as source:
            with sqlite3.connect(backup_path) as target:
                source.backup(target)
                
        logger.info(
            "SQLite 数据库备份成功: %s",
            backup_path
        )
        
        return backup_path
        
    except Exception:
        # 备份失败时，清理可能生成的不完整文件
        backup_path.unlink(missing_ok=True)
        
        logger.exception(
            "SQLite 数据库备份失败： %s",
            backup_path
        )
        raise
        