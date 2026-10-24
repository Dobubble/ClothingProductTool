import sqlite3
import tempfile
from pathlib import Path

def test_transaction_rollback():
    """ 测试 SQLite 批量插入失败后的事务回滚 """
    
    # 创建临时数据库
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "test.db"
        
        conn = sqlite3.connect(db_path)
        
        try:
            # 创建测试表
            conn.execute("""
                CREATE TABLE products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT NOT NULL,
                    name TEXT NOT NULL,
                    size TEXT NOT NULL DEFAULT ''
                )
            """)
            conn.commit()
            
            # 准备3条测试数据
            # 第二条 name 为None，违反NOT NULL约束
            
            products = [
                ("ROLL001", "正常商品A", "M"),
                ("ROLL002", None, "L"),
                ("ROLL003", "正常商品C", "XL")
            ]
            
            try:
                # 开始事务
                with conn:
                    conn.executemany(
                        """
                        INSERT INTO products (code, name, size)
                        VALUES (?, ?, ?)
                        """,
                        products
                    )
                print("测试失败：错误数据被成功写入")
                
            except sqlite3.IntegrityError as exc:
                print("成功捕获数据库异常:", exc)
                
            # 检查数据库记录数量
            count = conn.execute(
                "SELECT COUNT(*) FROM products"
            ).fetchone()[0]
            
            print("数据库剩余记录数：", count)
            
            if count == 0:
                print("测试通过：事务已完整回滚")
            else:
                print("测试失败：数据库存在部分写入")
                
        finally:
            conn.close()
            
if __name__ == "__main__":
    test_transaction_rollback()