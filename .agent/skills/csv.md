---
name: csv-data-analysis
description: "Use when the user asks to analyze, validate, aggregate, visualize, or explain a local CSV dataset. Check columns, calculate metrics with Python, execute scripts, and report only verified results."
---

# CSV 数据分析工作流

## 工作步骤

1. 确认 CSV 路径，读取表头，不假设列名。
2. 检查必需列、缺失值、负数和无法解析的数值。
3. 明确计算口径，例如销售额 = units × price。
4. 使用 `write_file` 写入 `/analysis.py`。
5. 使用 `run_python` 执行 `/analysis.py`；不要把未运行的推算当成结果。
6. 输出关键数字、计算方法、脚本执行状态和数据限制。
7. 对分组汇总与全量汇总做一致性校验。

`run_python` 的工作目录是 `src/langchain/.agent/skills`，不是 CSV 文件所在目录。
分析项目自带的样例数据时，使用 `Path(__file__).resolve().parents[2] / "data_analysis" / "sales.csv"`；
分析用户指定的文件时，使用用户确认的项目内路径，不要假设当前工作目录。

## CSV 读取模板

```python
import csv
from collections import defaultdict
from pathlib import Path

required = {"region", "product", "units", "price"}
csv_path = Path(__file__).resolve().parents[2] / "data_analysis" / "sales.csv"
with csv_path.open(newline="", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    missing = required - set(reader.fieldnames or [])
    if missing:
        raise ValueError(f"缺少列：{sorted(missing)}")

    by_product = defaultdict(float)
    by_region = defaultdict(float)
    total = 0.0

    for line_number, row in enumerate(reader, start=2):
        try:
            units = float(row["units"])
            price = float(row["price"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"第 {line_number} 行数值无效") from exc

        revenue = units * price
        total += revenue
        by_product[row["product"]] += revenue
        by_region[row["region"]] += revenue

assert abs(sum(by_product.values()) - total) < 1e-9
assert abs(sum(by_region.values()) - total) < 1e-9
```

## 错误处理

- 文件不存在：报告真实路径，不伪造数据。
- 缺少列：列出缺失列并停止聚合。
- 数值错误：报告行号和原始值。
- 脚本失败：读取 `stderr`，修正后重新执行。
- 汇总不一致：检查重复行、解析逻辑、分组键和金额口径。

## 输出格式

1. 已验证结论。
2. 关键数字表格。
3. 计算口径。
4. 脚本执行结果。
5. 数据限制和假设。
