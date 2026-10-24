from app_paths import(
    DATA_ROOT,
    DB_DIR,
    IMAGE_DIR,
    LOG_DIR,
    BACKUP_DIR,
    ensure_directories
)

def main():
    ensure_directories()
    
    print("用户数据目录：", DATA_ROOT)
    print("数据库目录：", DB_DIR)
    print("图片目录：", IMAGE_DIR)
    print("日志目录：", LOG_DIR)
    print("备份目录：", BACKUP_DIR)
    
    for directory in (
        DB_DIR,
        IMAGE_DIR,
        LOG_DIR,
        BACKUP_DIR
    ):
        assert directory.is_dir()
        
    print("测试通过：用户数据目录创建成功")
    
if __name__ == "__main__":
    main()