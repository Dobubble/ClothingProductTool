import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

import database

selected_product_id = None

def select_product(event=None):
    
    global selected_product_id
    """ 选中商品后，将商品信息填入输入框"""
    
    selected = product_table.selection()
    
    if not selected:
        selected_product_id = None
        return
        
    # 获取选中的第一条记录
    item = product_table.item(selected[0])
    
    #
    values = item["values"]
    
    # 保存选中商品的ID
    selected_product_id = int(values[0])
    
    code_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    size_entry.delete(0, tk.END)
    
    code_entry.insert(0, values[1])
    name_entry.insert(0, values[2])
    size_entry.insert(0, values[3])

def search_product():
    """ 根据输入的关键词查询商品 """
    keyword = search_entry.get().strip()
    
    if not keyword:
        refresh_products()
        return
    
    products = database.search_products(keyword)
    
    # 清空商品列表
    for item in product_table.get_children():
        product_table.delete(item)
        
    # 显示查询结果
    for product in products:
        product_table.insert(
            "",
            "end",
            iid=str(product[0]),
            values = product
        )

def refresh_products():
    
    global selected_product_id
    
    """ 从数据库读取并显示所有商品"""
    
    # 清空当前编辑状态
    selected_product_id = None
    
    # 清空商品列表
    for item in product_table.get_children():
        product_table.delete(item)
    
    # 读取数据库
    products = database.get_all_products()
    
    # 显示商品
    for product in products:
        product_table.insert(
            "",
            "end",
            iid = str(product[0]),
            values=product
        )
    
    

def add_product():
    if product_table.selection():
        messagebox.showwarning(
            "提示",
            "当前已选中商品。添加新商品前，请先取消列表选择"
        )
        return
    
    """将输入的商品信息添加到列表"""
    code = code_entry.get().strip()
    name = name_entry.get().strip()
    size = size_entry.get().strip()
    
    if not code or not name:
        messagebox.showwarning(
            "提示",
            "商品货号和商品名称不能为空。"
        )
        return
        
    try:
        database.add_product(code, name, size)
    
    except sqlite3.Error as exc:
        messagebox.showerror(
            "数据库错误",
            f"保存失败: {exc}"
        )
        return
    
    # 更新列表
    refresh_products()
    
    code_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    size_entry.delete(0, tk.END)
    
    code_entry.focus()
    
def save_product_changes():
    
    global selected_product_id
    """ 保存选中商品的修改 """
    
    # 必须先选择商品
    if selected_product_id is None:
        messagebox.showwarning(
            "提示",
            "请先选择需要修改的商品"
        )
        return
        
    # 读取输入框内容
    code = code_entry.get().strip()
    name = name_entry.get().strip()
    size = size_entry.get().strip()
    
    if not code or not name:
        messagebox.showwarning(
            "提示",
            "商品货号和名称不能为空"
        )
        return
        
    try:
        affected = database.update_product(
            selected_product_id,
            code,
            name,
            size
        )
        
    except sqlite3.Error as exc:
        messagebox.showerror(
            "数据库错误",
            f"修改失败：{exc}"
        )
        return
    
    if affected == 0:
        messagebox.showwarning(
            "提示",
            "商品不存在，可能已经被删除"
        )
        refresh_products()
        selected_product_id = None
        return
        
    # 清楚选择状态
    selected_product_id = None
    
    # 刷新商品列表
    refresh_products()
    
    # 清空输入框
    code_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    size_entry.delete(0, tk.END)
    
    messagebox.showinfo(
        "成功",
        "商品修改成功"
    )
    
def main():
    # 初始化数据
    database.init_database()
    
    global product_table
    global code_entry, name_entry, size_entry
    global search_entry
    # global selected_product_id
    
    # 创建主窗口
    root = tk.Tk()
    root.title("服装商品资料管理工具")
    root.geometry("800x500")
    root.minsize(650, 400)

    # 输入区域
    input_frame = ttk.LabelFrame(
        root,
        text="商品资料录入",
        padding=12
    )

    input_frame.pack(fill="x", padx=12, pady=12)

    ttk.Label(input_frame, text="商品货号:").grid(
        row=0, column=0, padx=5, pady=8
    )
    code_entry = ttk.Entry(input_frame, width=20)
    code_entry.grid(row=0, column=1, padx=5, pady=8)

    ttk.Label(input_frame, text="商品名称：").grid(
        row=0, column=2, padx=5, pady=8
    )
    name_entry = ttk.Entry(input_frame, width=20)
    name_entry.grid(row=0, column=3, padx=5, pady=8)

    ttk.Label(input_frame, text="尺码:").grid(
        row=1, column=0, padx=5, pady=8
    )
    size_entry=ttk.Entry(input_frame, width=20)
    size_entry.grid(row=1, column=1, padx=5, pady=8)

    add_button = ttk.Button(
        input_frame,
        text="添加商品",
        command=add_product
    )
    add_button.grid(row=1, column=3, padx=5, pady=8)
    
    update_button = ttk.Button(
        input_frame,
        text="保存修改",
        command=save_product_changes
    )
    update_button.grid(row=2, column=3, padx=5, pady=8)
    
    # 商品搜索区域
    search_frame = ttk.LabelFrame(
        root,
        text="商品查询",
        padding=10
    )
    search_frame.pack(fill="x", padx=12, pady=(0, 12))
    
    ttk.Label(
        search_frame,
        text="货号或名称:"
    ).pack(side="left", padx=5)
    
    search_entry = ttk.Entry(search_frame, width=30)
    search_entry.pack(side="left", padx=5)
    
    ttk.Button(
        search_frame,
        text="查询",
        command = search_product
    ).pack(side="left", padx=5)
    
    ttk.Button(
        search_frame,
        text="显示全部",
        command=refresh_products
    ).pack(side="left", padx=5)

    # 商品列表
    list_frame = ttk.LabelFrame(
        root,
        text="商品列表",
        padding=10
    )

    list_frame.pack(
        fill="both",
        expand=True,
        padx=12,
        pady=(0,12)
    )

    product_table = ttk.Treeview(
        list_frame,
        columns=("id", "code", "name", "size"),
        show="headings"
    )
    
    product_table.heading("id", text="ID")
    product_table.heading("code", text="商品货号")
    product_table.heading("name", text="商品名称")
    product_table.heading("size", text="尺码")

    product_table.column("id", width=60)
    product_table.column("code", width=180)
    product_table.column("name", width=280)
    product_table.column("size", width=120)

    product_table.pack(fill="both", expand=True)
    
    product_table.bind(
        "<<TreeviewSelect>>",
        select_product
    )
    # 启动程序
    refresh_products()
    root.mainloop()

if __name__ == "__main__":
    main()