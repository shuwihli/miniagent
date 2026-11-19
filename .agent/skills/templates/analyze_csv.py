"""CSV 分析脚本模板。复制到工作目录后修改 REQUIRED_COLUMNS。"""

import csv
from collections import defaultdict
from pathlib import Path

REQUIRED_COLUMNS = {"region", "product", "units", "price"}

csv_path = Path(__file__).resolve().parents[2] / "data_analysis" / "sales.csv"
with csv_path.open(newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
    if missing:
        raise ValueError(f"缺少列：{sorted(missing)}")

    by_product = defaultdict(float)
    by_region = defaultdict(float)
    total = 0.0
    row_count = 0

    for line_number, row in enumerate(reader, start=2):
        try:
            units = float(row["units"])
            price = float(row["price"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"第 {line_number} 行数值无效：{row}") from exc

        if units < 0 or price < 0:
            raise ValueError(f"第 {line_number} 行存在负数：{row}")

        revenue = units * price
        total += revenue
        by_product[row["product"]] += revenue
        by_region[row["region"]] += revenue
        row_count += 1

print(f"记录数：{row_count}")
print(f"总销售额：{total:,.2f}")
print("按产品：", dict(sorted(by_product.items())))
print("按地区：", dict(sorted(by_region.items())))
assert abs(sum(by_product.values()) - total) < 1e-9
assert abs(sum(by_region.values()) - total) < 1e-9
print("校验通过：两种汇总都等于总销售额")
