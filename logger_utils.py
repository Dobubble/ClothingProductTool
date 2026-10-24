import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app_paths import LOG_DIR, ensure_directories

ensure_directories()

'''
# 项目根目录
BASE_DIR = Path(__file__).resolve().parent

# 日志目录
LOG_DIR = BASE_DIR / "logs"
'''

# 日志文件
LOG_FILE = LOG_DIR / "app.log"

def setup_logger():
    """ 初始化程序日志系统 """
    
    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )
    
    logger = logging.getLogger("ClothingProductTool")
    
    logger.setLevel(logging.INFO)
    
    # 避免重复添加日志处理器
    if logger.handlers:
        return logger
        
    # 文件日志，最大1MB，保留3分历史
    handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    
    # 日志格式
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | "
        "%(module)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger
    
# 供其他模块直接使用
logger = setup_logger()