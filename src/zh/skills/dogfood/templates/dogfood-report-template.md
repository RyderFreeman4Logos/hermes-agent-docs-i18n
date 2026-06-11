# 内部测试质量报告

**目标地址：** {target_url}
**日期：** {date}
**测试范围：** {scope_description}
**测试工具：** Hermes Agent（自动化探索性测试）

---

## 执行摘要

| 严重程度 | 数量 |
|----------|-------|
| 🔴 极严重 | {critical_count} |
| 🟠 严重 | {high_count} |
| 🟡 中等 | {medium_count} |
| 🔵 轻微 | {low_count} |
| **总计** | **{total_count}** |

**整体评估：** {one_sentence_assessment}

---

## 存在的问题

<!-- 按严重程度从高到低排列，每个问题重复此部分 -->

### 问题 #{issue_number}：{issue_title}

| 字段 | 值 |
|-------|-------|
| **严重程度** | {severity} |
| **类别** | {category} |
| **出现位置URL** | {url_where_found} |

**问题描述：**
{detailed_description_of_the_issue}

**复现步骤：**
1. {step_1}
2. {step_2}
3. {step_3}

**预期行为：**
{what_should_happen}

**实际行为：**
{what_actually_happens}

**截图：**
MEDIA:{screenshot_path}

**控制台错误信息**（如存在）：
```
{console_error_output}
```

---

<!-- 每个问题部分的结束 -->

## 问题汇总表

| 序号 | 标题 | 严重程度 | 类别 | URL |
|---|-------|----------|----------|-----|
| {n} | {title} | {severity} | {category} | {url} |

## 测试覆盖情况

### 已测试页面
- {list_of_pages_visited}

### 已测试功能
- {list_of_features_exercised}

### 未测试/不在范围之内
- {areas_not_covered_and_why}

### 阻碍因素
- {any_issues_that_prevented_testing_certain_areas}

---

## 备注

{any_additional_observations_or_recommendations}
