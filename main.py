import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3

import database
import excel_utils
from logger_utils import logger
from backup_utils import backup_database

from image_utils import (
    import_product_image,
    load_preview_image,
    find_product_image
)

selected_product_id = None
current_photo = None

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
    show_product_image(str(values[1]))

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
    clear_product_image()
    
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
    
def delete_product():
    """ 删除选中的商品 """
    
    global selected_product_id
    
    # 获取选中商品
    selected = product_table.selection()
    
    if not selected:
        messagebox.showwarning(
            "提示",
            "请先选择需要删除的商品"
        )
        return
        
    # 获取商品资料
    item = product_table.item(selected[0])
    values = item["values"]
    
    product_id = int(values[0])
    product_code = values[1]
    product_name = values[2]
    
    # 用户确认
    confirmed = messagebox.askyesno(
        "确认删除",
        f"确定删除以上商品?\n\n"
        f"ID: {product_id}\n"
        f"货号： {product_code}\n"
        f"名称: {product_name}\n\n"
        "删除后无法通过程序撤销!"
    )
    
    if not confirmed:
        return
        
    # 真正执行数据库删除
    try:
        affected = database.delete_product(product_id)
        
    except sqlite3.Error as exc:
        messagebox.showerror(
            "数据库错误",
            f"删除失败: {exc}"
        )
        return
        
    # 检查是否删除成功
    if affected == 0:
        messagebox.showwarning(
            "提示",
            "没有找到需要删除的商品"
        )
        return
        
    # 清除当前编辑状态
    selected_product_id = None
    
    # 清空输入框
    code_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    size_entry.delete(0, tk.END)
    
    # 刷新商品列表
    refresh_products()
    
    messagebox.showinfo(
        "成功",
        f"商品 ID={product_id}已经删除"
    )
    
def new_product():
    """ 切换到新增商品状态 """
    
    global selected_product_id
    
    # 清除当前选中的商品ID
    selected_product_id = None
    
    # 取消商品列表的选择
    selected = product_table.selection()
    
    if selected:
        product_table.selection_remove(*selected)
        
    # 清空输入框
    code_entry.delete(0, tk.END)
    name_entry.delete(0, tk.END)
    size_entry.delete(0, tk.END)
    
    # 将光标放到商品货号输入框
    code_entry.focus_set()
    clear_product_image()
    
def export_excel():
    """ 导出商品资料到 Excel """
    
    # 让用户选择保存位置
    file_path = filedialog.asksaveasfilename(
        title="导出商品资料",
        defaultextension=".xlsx",
        filetypes=[
            ("Excel 文件", "*.xlsx")
        ],
        initialfile = "商品资料.xlsx"
    )
    
    # 用户取消保存
    if not file_path:
        return
        
    try:
        count = excel_utils.export_products(file_path)
        
    except (OSError, ValueError) as exc:
        logger.exception(
            "Excel 导出失败，目标文件：%s",
            file_path
        )
        
        messagebox.showerror(
            "导出失败",
            f"无法保存 Excel 文件: {exc}"
        )
        
        return
        
    messagebox.showinfo(
        "导出成功",
        f"成功导出 {count} 条商品记录。\n\n"
        f"文件位置: {file_path}"
    )
    
def import_excel_preview():
    """ 校验 Excel 并批量导入 SQLite"""
    
    file_path = filedialog.askopenfilename(
        title="选择商品 Excel 文件",
        filetypes=[
            ("Excel 文件", "*.xlsx")
        ]
    )
    
    if not file_path:
        return
        
    try:
        products = excel_utils.preview_import_products(
            file_path
        )
        
    except (OSError, ValueError, Exception) as exc:
        logger.exception(
            "Excel 导入检查失败：%s",
            file_path
        )
        
        messagebox.showerror(
            "Excel 检查失败",
            str(exc)
        )
        return
        
    if not products:
        messagebox.showwarning(
            "提示",
            "Excel 中没有可导入的商品"
        )
        return
        
    # 第二部： 显示导入预览
    preview_lines = []
    
    for code, name, size in products[:10]:
        preview_lines.append(
            f"{code} | {name} | {size}"
        )
        
    preview_text = "\n".join(preview_lines)
    
    if len(products) > 10:
        preview_text += (
            f"\n……其余 {len(products)-10}条未显示"
        )
        
    # 筛选新商品，跳过重复商品
    new_products, duplicate_count = database.filter_new_products(products)
    
    if not new_products:
        messagebox.showinfo(
            "导入结果",
            f"Excel 共 {len(products)}条商品。\n"
            f"重复商品： {duplicate_count}条。\n\n"
            "没有需要新增的商品。"
        )
        return
        
    confirmed = messagebox.askyesno(
        "确认批量导入",
        f"Excel 总记录： {len(products)}条\n"
        f"重复商品：{duplicate_count}条\n"
        f"准备新增：{len(new_products)}条\n\n"
        "是否继续导入新商品？"
    )
    
    if not confirmed:
        return
        
    # 执行导入前，先自动备份数据库
    try:
        backup_path = backup_database()
        
    except Exception as exc:
        messagebox.showerror(
            "备份失败",
            f"数据库自动备份失败，已取消本次导入。\n\n{exc}"
        )
        return
        
    # 第三步: 批量写入数据库
    """
    try:
        count = database.import_products(products)
    """
    try:
        count = database.import_products(new_products)
        
    except Exception as exc:
        logger.exception(
            "SQLite批量导入失败，文件：%s",
            file_path
        )
        messagebox.showerror(
            "导入失败",
            f"数据库写入失败: {exc}"
        )
        return
        
    logger.info(
        "Excel 批量导入成功，新增记录数：%d, 备份文件： %s",
        count,
        backup_path
    )
    
    # 第四部：刷新列表
    refresh_products()
    
    messagebox.showinfo(
        "导入成功",
        f"成功导入 {count} 条商品"
    )
    
def clear_product_image():
    global current_photo
    current_photo = None
    image_label.configure(image="", text="请选择商品查看图片")
    image_path_label.configure(text="")


def show_product_image(code):
    global current_photo
    try:
        photo = load_preview_image(code, max_width=340, max_height=420)
        current_photo = photo
        if photo is None:
            image_label.configure(image="", text="该商品暂无图片")
            image_path_label.configure(text="")
        else:
            image_label.configure(image=photo, text="")
            image_path_label.configure(text=str(find_product_image(code).name))
    except Exception as exc:
        logger.exception("商品图片显示失败，编码：%s", code)
        current_photo = None
        image_label.configure(image="", text="图片加载失败")
        image_path_label.configure(text="")
        messagebox.showerror("图片错误", str(exc))


def import_image():
    code = code_entry.get().strip()
    if not code:
        messagebox.showwarning("提示", "请先输入或选择商品编码")
        return
    file_path = filedialog.askopenfilename(
        title="选择商品图片",
        filetypes=[("图片文件", "*.jpg *.jpeg *.png *.webp")]
    )
    if not file_path:
        return
    try:
        existing = find_product_image(code)
        if existing is not None:
            if not messagebox.askyesno("确认替换", f"编码 {code} 已有图片，确定替换吗？"):
                return
        target = import_product_image(code, file_path)
        show_product_image(code)
        messagebox.showinfo("成功", f"商品图片已导入：\n{target}")
    except Exception as exc:
        logger.exception("商品图片导入失败，编码：%s", code)
        messagebox.showerror("图片导入失败", str(exc))


def main():
    # 初始化数据
    database.init_database()
    
    global product_table
    global code_entry, name_entry, size_entry
    global search_entry
    global image_label, image_path_label
    # global selected_product_id
    
    # 创建主窗口
    root = tk.Tk()
    root.title("服装商品资料管理工具")
    root.geometry("1150x680")
    root.minsize(960, 550)

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
    
    new_button = ttk.Button(
        input_frame,
        text="新建商品",
        command=new_product
    )
    new_button.grid(row=2, column=1, padx=5, pady=8)

    add_button = ttk.Button(
        input_frame,
        text="添加商品",
        command=add_product
    )
    add_button.grid(row=2, column=2, padx=5, pady=8)
    
    update_button = ttk.Button(
        input_frame,
        text="保存修改",
        command=save_product_changes
    )
    update_button.grid(row=3, column=1, padx=5, pady=8)
    
    # 删除按钮
    delete_button = ttk.Button(
        input_frame,
        text="删除商品",
        command=delete_product
    )
    delete_button.grid(row=3,column=2,padx=5,pady=8)
    
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
    
    ttk.Button(
        search_frame,
        text="导出 Excel",
        command=export_excel
    ).pack(side="left", padx=5)
    
    ttk.Button(
        search_frame,
        text="导入 Excel",
        command=import_excel_preview
    ).pack(side="left", padx=5)

    # 商品列表和图片区域并排放置
    content_frame = ttk.Frame(root)
    content_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    list_frame = ttk.LabelFrame(
        content_frame,
        text="商品列表",
        padding=10
    )

    list_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))

    image_frame = ttk.LabelFrame(content_frame, text="商品图片", padding=10)
    image_frame.pack(side="right", fill="y")
    image_label = ttk.Label(image_frame, text="请选择商品查看图片", anchor="center")
    image_label.pack(fill="both", expand=True)
    image_path_label = ttk.Label(image_frame, text="", anchor="center")
    image_path_label.pack(pady=(6, 0))
    ttk.Button(image_frame, text="导入商品图片", command=import_image).pack(pady=(8, 0))

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
    logger.info("ClothingProductTool 程序启动")
    main()