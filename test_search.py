import database

keyword = input("请输入商品货号或名称: ").strip()

products = database.search_products(keyword)

print("查询结果： ")

for product in products:
    print(product)
    
print(f"共找到 {len(products)}条商品")