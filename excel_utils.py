from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

import database

def export_products(file_path):
    """ 将数据库中的商品导出围殴 Excel"""
    
    # 读取全部商品
    products = database.get_all_products()
    
    # 创建Excel工作簿
    wb = Workbook()
    ws = wb.active
    ws.title = "商品资料"
    
    # 写入表头
    headers = ["ID", "商品货号", "商品名称", "尺码"]
    ws.append(headers)
    
    # 写入商品数据
    for product in products:
        ws.append(product)
        
    # 设置表头样式
    for cell in ws[1]:
        cell.font = Font(
            bold=True,
            color="FFFFFF"
        )
        cell.fill = PatternFill(
            "solid",
            fgColor="4472C4"
        )
        cell.alignment = Alignment(
            horizontal = "center"
        )
        
    # 设置列宽
    widths = [10, 22, 35, 15]
    
    for index, width in enumerate(widths, start=1):
        column_letter = get_column_letter(index)
        ws.column_dimensions[column_letter].width=width
        
    # 冻结第一行
    ws.freeze_panes = "A2"
    
    # 设置自动筛选
    ws.auto_filter.ref = ws.dimensions
    
    # 保存Excel文件
    wb.save(file_path)
    
    return len(products)