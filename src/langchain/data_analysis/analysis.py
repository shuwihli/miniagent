import csv
import os
from collections import defaultdict

required = {"region", "product", "units", "price"}
# 使用脚本所在目录的相对路径，避免 Windows 主机上绝对路径解析问题
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sales.csv")

with open(path, newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    missing = required - set(reader.fieldnames or [])
    if missing:
        raise ValueError(f"缺少列：{sorted(missing)}")

    by_product = defaultdict(float)
    by_region = defaultdict(float)
    by_product_units = defaultdict(float)
    total = 0.0
    rows = 0

    for line_number, row in enumerate(reader, start=2):
        try:
            units = float(row["units"])
            price = float(row["price"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"第 {line_number} 行数值无效: {row}") from exc
        if units < 0 or price < 0:
            raise ValueError(f"第 {line_number} 行存在负数: {row}")

        revenue = units * price
        total += revenue
        rows += 1
        by_product[row["product"]] += revenue
        by_product_units[row["product"]] += units
        by_region[row["region"]] += revenue

assert abs(sum(by_product.values()) - total) < 1e-9
assert abs(sum(by_region.values()) - total) < 1e-9

print(f"数据行数: {rows}")
print(f"总销售额: {total:,.2f}")
print()

print("== 各产品销售额 (units x price) ==")
for product, revenue in sorted(by_product.items(), key=lambda kv: -kv[1]):
    share = revenue / total * 100
    print(f"{product}: {revenue:,.2f}  (units={by_product_units[product]:.0f}, 占比 {share:.1f}%)")

top_product, top_revenue = max(by_product.items(), key=lambda kv: kv[1])
print()
print(f"销售额最高产品: {top_product} -> {top_revenue:,.2f}")

print()
print("== 各地区销售额 ==")
for region, revenue in sorted(by_region.items(), key=lambda kv: -kv[1]):
    share = revenue / total * 100
    print(f"{region}: {revenue:,.2f}  (占比 {share:.1f}%)")

print()
print(f"校验: 产品汇总={sum(by_product.values()):,.2f} 地区汇总={sum(by_region.values()):,.2f} 总计={total:,.2f}")
