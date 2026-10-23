import sqlite3
from pathlib import Path

# 项目所在目录
BASE_DIR = Path(__file__).resolve().parent

# 数据存储目录
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# SQLite 数据库文件
DB_PATH = DATA_DIR / "products.db"

def get_connection():
    """连接数据库"""
    return sqlite3.connect(DB_PATH)
    
def init_database():
    """首次运行时创建商品"""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                name TEXT NOT NULL,
                size TEXT NOT NULL Default ''
            )
        """)
        
def add_product(code, name, size):
    """ 新增商品记录"""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO products (code, name, size)
            VALUES (?, ?, ?)
            """,
            (code, name, size)
        )
        return cursor.lastrowid
        
def get_all_products():
    """ 读取所有商品记录 """
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT id, code, name, size
            FROM products
            ORDER BY id DESC
        """)
        return cursor.fetchall()
        
def search_products(keyword):
    """ 根据货号或商品名称查询商品 """
    with get_connection() as conn:
        cursor = conn.execute("""
            select id,code,name,size
            FROM products
            WHERE code LIKE ? OR name LIKE ?
            ORDER BY id DESC
            """,
            (f"%{keyword}%", f"%{keyword}%")
        )
        
        return cursor.fetchall()
        
def update_product(product_id, code, name, size):
    """ 根据商品ID 修改商品资料 """
    
    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE products
            SET code = ?, name = ?, size = ?
            WHERE id = ?
            """,
            (code, name, size, product_id)
        )
        
        return cursor.rowcount
        
def delete_product(product_id):
    """ 根据商品ID 删除数据记录 """
    
    with get_connection() as conn:
        cursor = conn.execute(
            """
            DELETE FROM products
            WHERE id = ?
            """,
            (product_id,)
        )
        
        return cursor.rowcount
        
def import_products(products):
    """ 批量导入商品，使用SQLite 事务保证完整性 """
    
    if not products:
        return 0
        
    # 检查传入的数据
    for index, product in enumerate(products, start=1):
        if len(product) != 3:
            raise ValueError(
                f"第 {index} 条商品字段数量不正确"
            )
            
        code, name, size = product
        
        if not isinstance(code, str) or not code.strip():
            raise ValueError(
                f"第 {index} 条商品货号不能为空"
            )
            
        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                f"第 {index} 条商品名称不能为空"
            )
            
    # 使用单个数据库事务
    with get_connection() as conn:
        
        cursor = conn.executemany(
            """
            INSERT INTO products (code, name, size)
            VALUES (?, ?, ?)
            """,
            products
        )
        return cursor.rowcount