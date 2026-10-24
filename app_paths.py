import os
from pathlib import Path

# Python 源代码所在目录
APP_DIR = Path(__file__).resolve().parent

# Windows 用户数据根目录
LOCAL_APPDATA = os.environ.get("LOCALAPPDATA")

if LOCAL_APPDATA:
    DATA_ROOT = (
        Path(LOCAL_APPDATA) / "ClothingProductTool"
    )
else:
    # 非Windows开发环境备用路径
    DATA_ROOT = Path.home() / ".ClothingProductTool"
    
DB_DIR = DATA_ROOT / "data"
IMAGE_DIR = DATA_ROOT / "images"
LOG_DIR = DATA_ROOT / "logs"
BACKUP_DIR = DATA_ROOT / "backups"

DB_PATH = DB_DIR / "products.db"

def ensure_directories():
    """ 创建用户数据目录 """
    for directory in (
        DB_DIR,
        IMAGE_DIR,
        LOG_DIR,
        BACKUP_DIR
    ):
        directory.mkdir(
            parents=True,
            exist_ok=True
        )