
import shutil
import sqlite3
from contextlib import closing
from pathlib import Path

from app_paths import (
    DATA_ROOT,
    DB_PATH,
    IMAGE_DIR,
    LOG_DIR,
    BACKUP_DIR,
    ensure_directories,
)

SOURCE_ROOT = Path(__file__).resolve().parent
SOURCE_DB = SOURCE_ROOT / "data" / "products.db"


def count_products(path):
    uri = path.resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as conn:
        result = conn.execute(
            "PRAGMA integrity_check"
        ).fetchone()[0]
        if result != "ok":
            raise RuntimeError(f"数据库完整性异常：{result}")
        return conn.execute(
            "SELECT COUNT(*) FROM products"
        ).fetchone()[0]


def migrate_database():
    if not SOURCE_DB.is_file():
        raise FileNotFoundError(
            f"原始数据库不存在：{SOURCE_DB}"
        )

    source_count = count_products(SOURCE_DB)

    if DB_PATH.exists():
        target_count = count_products(DB_PATH)
        print("目标数据库已存在，未覆盖。")
        print("原始商品数：", source_count)
        print("目标商品数：", target_count)
        if source_count != target_count:
            print("警告：两个数据库商品数量不同，请人工检查。")
        return

    # 先写入临时文件，成功后再改名
    temp_path = DB_PATH.with_name("products_migrating.tmp")

    if temp_path.exists():
        raise RuntimeError(
            f"存在上次迁移的临时文件，请先检查：{temp_path}"
        )

    try:
        source_uri = SOURCE_DB.resolve().as_uri() + "?mode=ro"
        with closing(
            sqlite3.connect(source_uri, uri=True)
        ) as source:
            with closing(
                sqlite3.connect(temp_path)
            ) as target:
                source.backup(target)

        target_count = count_products(temp_path)

        if source_count != target_count:
            raise RuntimeError("迁移前后商品数量不一致")

        temp_path.replace(DB_PATH)

        print("数据库迁移成功，商品数量：", target_count)
    finally:
        temp_path.unlink(missing_ok=True)


def copy_directory(source, target):
    if not source.is_dir():
        print("源目录不存在，跳过：", source)
        return

    copied = 0
    skipped = 0

    for file in source.rglob("*"):
        if not file.is_file():
            continue

        relative = file.relative_to(source)
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)

        if destination.exists():
            skipped += 1
            continue

        # 排除 SQLite 临时附属文件
        if file.name.endswith(("-wal", "-shm", "-journal")):
            continue

        with file.open("rb") as src:
            try:
                with destination.open("xb") as dst:
                    shutil.copyfileobj(src, dst)
            except FileExistsError:
                skipped += 1
                continue

        copied += 1

    print(
        f"{source.name}：复制 {copied} 个，"
        f"跳过已有文件 {skipped} 个"
    )


def main():
    print("ClothingProductTool 用户数据迁移")
    print("源目录：", SOURCE_ROOT)
    print("目标目录：", DATA_ROOT)

    ensure_directories()

    migrate_database()

    copy_directory(SOURCE_ROOT / "images", IMAGE_DIR)
    copy_directory(SOURCE_ROOT / "logs", LOG_DIR)
    copy_directory(SOURCE_ROOT / "backups", BACKUP_DIR)

    print("迁移程序执行完成。原始文件未删除。")


if __name__ == "__main__":
    main()
