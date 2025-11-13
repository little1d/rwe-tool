# Case 1 — JAKi vs Non-JAKi AMD 风险 Workflow

> Mock 数据：`data/mock/case1_jaki_vs_nonjaki.csv`

## 目标

比较首次接受 JAKi 治疗与非 JAKi 治疗的自身免疫性疾病患者，在 12 个月随访期内发生 AMD（年龄相关性黄斑变性）的风险。

## 输入要素

- **索引事件**：首次使用 JAKi 或非 JAKi 的日期，纳入年龄 ≥ 40 岁且有连续参保。
- **基线期**：索引前 6 个月（本 mock 数据已满足），记录协变量 `baseline_smd_score` 等。
- **随访期**：索引后最长 12 个月（表中 `followup_days`、`event_day`）。
- **终点**：AMD 发生（二元 `amd_event`），以及事件发生天数。

## 建议 Workflow

1. **意图解析 / Study Draft**  
   - 读取 QWEN.md 或用户输入，生成“暴露 vs 对照 + 生存分析”todo 列表。  
   - 输出需跟用户确认：索引定义、基线限定、排除条件、主要终点。

2. **Cohort 构建与基线检查**  
   - 从 mock CSV 读取全部记录，按 `cohort` 分出暴露组/对照组。  
   - 计算关键协变量（年龄、sex、baseline_smd_score）的摘要统计，并输出 SMD，用于评估是否需要匹配/加权。

3. **事件分析**  
   - 计算每组累计 AMD 事件数、发生率（事件数/人年）。  
   - 使用 Kaplan-Meier 或贝叶斯泊松模型估计发生率比；本样例可用简单的对数排名或 Poisson rate ratio。

4. **可视化与报告**  
   - 生成 cohort attrition 表（即 CSV 记录即可）。  
   - 绘制累计发生率曲线或柱状图比较事件率。  
   - 输出简要 narrative：样本量、事件数、估计的风险差异。

## Mock 数据说明

- 数据规模 12 人，JAKi 6 人、Non-JAKi 6 人。  
- JAKi 组仅 1 例 AMD，Non-JAKi 有 4 例，故期望分析结论显示 Non-JAKi 风险更高。  
- `baseline_smd_score` 可用于评估组间不平衡（Non-JAKi 略高）。
