import csv
from collections import defaultdict
from pathlib import Path

required = {"region", "product", "units", "price"}
csv_path = Path(__file__).resolve().parents[2] / "data_analysis" / "sales.csv"

print("CSV 路径:", csv_path)
print("文件存在:", csv_path.exists())
if not csv_path.exists():
    raise SystemExit("文件不存在，停止分析")

with csv_path.open(newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    fieldnames = reader.fieldnames or []
    print("表头:", fieldnames)
    missing = required - set(fieldnames)
    if missing:
        raise SystemExit(f"缺少列：{sorted(missing)}")

    by_product = defaultdict(float)
    by_region = defaultdict(float)
    total = 0.0
    rows = 0
    bad = []
    negatives = []

    for line_number, row in enumerate(reader, start=2):
        rows += 1
        try:
            units = float(row["units"])
            price = float(row["price"])
        except (TypeError, ValueError):
            bad.append((line_number, row.get("units"), row.get("price")))
            continue
        if units < 0 or price < 0:
            negatives.append((line_number, units, price))
        revenue = units * price
        total += revenue
        by_product[row["product"]] += revenue
        by_region[row["region"]] += revenue

print("数据行数:", rows)
print("无法解析的行:", bad)
print("含负数的行:", negatives)

print("\n总销售额: %.2f" % total)
print("按产品分组合计: %.2f" % sum(by_product.values()))
print("按地区分组合计: %.2f" % sum(by_region.values()))
print("分组一致性(产品):", abs(sum(by_product.values()) - total) < 1e-9)
print("分组一致性(地区):", abs(sum(by_region.values()) - total) < 1e-9)

print("\n--- 按产品 ---")
for k, v in sorted(by_product.items(), key=lambda x: -x[1]):
    print(f"{k}: {v:.2f}  ({v/total*100:.1f}%)")

print("\n--- 按地区 ---")
for k, v in sorted(by_region.items(), key=lambda x: -x[1]):
    print(f"{k}: {v:.2f}  ({v/total*100:.1f}%)")
