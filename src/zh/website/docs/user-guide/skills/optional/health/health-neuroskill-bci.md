---
title: "Neuroskill Bci"
sidebar_label: "Neuroskill Bci"
description: "Connect to a running NeuroSkill instance and incorporate the user's real-time cognitive and emotional state (focus, relaxation, mood, cognitive load, drowsin..."
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Neuroskill BCI

该技能可连接到正在运行的 NeuroSkill 实例，从而获取用户的实时认知与情绪状态数据（包括专注度、放松程度、情绪状态、认知负荷、困倦感、心率、心率变异性、睡眠阶段以及 40 多项基于脑电图的衍生评分），并将其融入回复内容中。使用时需要配备 BCI 可穿戴设备（如 Muse 2/S 或 OpenBCI），同时本地还需运行 NeuroSkill 桌面应用。

## 技能元数据

| | |
|---|---|
| 来源 | 可选 —— 可通过 `hermes skills install official/health/neuroskill-bci` 命令安装 |
| 路径 | `optional-skills/health/neuroskill-bci` |
| 版本 | `1.0.0` |
| 开发者 | Hermes Agent + Nous Research |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `BCI`、`神经反馈`、`健康`、`专注力`、`脑电图`、`认知状态`、`生物特征`、`Neuroskill` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 所加载的完整技能定义。技能处于激活状态时，智能体将依据这些内容执行相应操作。
:::

# NeuroSkill BCI 集成

通过该技能可将 Hermes 与正在运行的 [NeuroSkill](https://neuroskill.com/) 实例相连，从而从 BCI 可穿戴设备中读取实时的大脑与身体指标数据。利用这些数据，智能体能够给出具备认知洞察力的回复、提出相应的干预建议，并长期追踪用户的心理表现状况。

> **⚠️ 仅限研究用途** —— NeuroSkill 是一款开源研究工具，它并非医疗设备，也未获得 FDA、CE 或其他任何监管机构的认证。切勿将这些指标用于临床诊断或治疗。

如需查看完整的指标参考信息，请参阅 `references/metrics.md`；干预方案详见 `references/protocols.md`；WebSocket/HTTP API 的相关说明则位于 `references/api.md` 中。

---

## 先决条件

- 已安装 **Node.js 20+** 版本（可通过 `node --version` 查看版本）
- 配备已连接的 BCI 设备，且 **NeuroSkill 桌面应用**正在运行中
- **BCI 硬件**：Muse 2、Muse S 或 OpenBCI（支持通过 BLE 传输 4 路脑电图信号、脉搏波信号及惯性测量数据）
- 执行 `npx neuroskill status` 命令时能无错误地返回数据

### 验证设置是否正确
```bash
node --version                    # Must be 20+
npx neuroskill status             # Full system snapshot
npx neuroskill status --json      # Machine-parseable JSON
```

如果执行 `npx neuroskill status` 时出现错误，请告知用户：
- 确保 NeuroSkill 桌面应用已打开
- 确保脑电接口设备已通电并通过蓝牙连接
- 检查信号质量——NeuroSkill 中的指示灯应为绿色（每个电极的数值≥0.7）
- 若出现“命令未找到”的提示，请安装 Node.js 20+ 版本

---

## CLI 参考：`npx neuroskill <command>`

所有命令均支持 `--json`（原始 JSON 格式，可安全传递给管道）和 `--full`（人工总结内容 + JSON 数据）选项。

| 命令 | 描述 |
|------|------|
| `status` | 提供完整的系统状态概览：设备信息、得分、脑电波段、比率值、睡眠状态及历史记录 |
| `session [N]` | 显示单次会话的详细数据，以及前半段/后半段的趋势变化（0表示最新会话） |
| `sessions` | 列出所有日期中记录的所有会话 |
| `search` | 基于近似最近邻算法，搜索具有相似脑电特征的过往时刻 |
| `compare` | 对比不同会话的指标差异，并进行趋势分析 |
| `sleep [N]` | 对睡眠阶段进行分类（清醒期/N1期/N2期/N3期/快速眼动期），并附上分析结果 |
| `label "text"` | 在当前时间点创建带时间戳的注释 |
| `search-labels "query"` | 基于语义向量对过往注释进行搜索 |
| `interactive "query"` | 执行跨模态的4层图搜索（文本 → 脑电信号 → 注释） |
| `listen` | 实时流式传输事件数据（默认时长为5秒，可通过 `--seconds N` 参数自定义） |
| `umap` | 对会话嵌入向量进行3D UMAP投影可视化 |
| `calibrate` | 打开校准窗口并开始创建个人配置文件 |
| `timer` | 启动专注计时器（提供番茄工作法、深度工作、短时专注等多种预设模式） |
| `notify "title" "body"` | 通过 NeuroSkill 应用向操作系统发送通知 |
| `raw '{json}'` | 将原始 JSON 数据直接传递给服务器 |

### 全局参数
| 参数 | 描述 |
|------|------|
| `--json` | 输出原始 JSON 格式的数据（不含 ANSI 格式字符，可安全传递给管道） |
| `--full` | 提供人工总结内容 + 彩色标注的 JSON 数据 |
| `--port <N>` | 覆盖服务器端口设置（默认为自动检测，通常为8375） |
| `--ws` | 强制使用 WebSocket 传输协议 |
| `--http` | 强制使用 HTTP 传输协议 |
| `--k <N>` | 近邻搜索的数量（适用于 search 和 search-labels 命令） |
| `--seconds <N>` | listen 命令的运行时长（默认为5秒） |
| `--trends` | 显示各会话的指标趋势变化（适用于 sessions 命令） |
| `--dot` | 生成 Graphviz DOT 格式的输出文件（适用于 interactive 命令） |

---

## 1. 检查当前状态

### 获取实时指标数据
```bash
npx neuroskill status --json
```

为确保解析的准确性，请始终使用 `--json` 参数。默认输出形式为带颜色标注、便于人类阅读的文本。

### 响应中的关键字段

`scores` 对象包含了所有实时指标（除非另有说明，数值范围为 0–1）：

```jsonc
{
  "scores": {
    "focus": 0.70,           // β / (α + θ) — sustained attention
    "relaxation": 0.40,      // α / (β + θ) — calm wakefulness
    "engagement": 0.60,      // active mental investment
    "meditation": 0.52,      // alpha + stillness + HRV coherence
    "mood": 0.55,            // composite from FAA, TAR, BAR
    "cognitive_load": 0.33,  // frontal θ / temporal α · f(FAA, TBR)
    "drowsiness": 0.10,      // TAR + TBR + falling spectral centroid
    "hr": 68.2,              // heart rate in bpm (from PPG)
    "snr": 14.3,             // signal-to-noise ratio in dB
    "stillness": 0.88,       // 0–1; 1 = perfectly still
    "faa": 0.042,            // Frontal Alpha Asymmetry (+ = approach)
    "tar": 0.56,             // Theta/Alpha Ratio
    "bar": 0.53,             // Beta/Alpha Ratio
    "tbr": 1.06,             // Theta/Beta Ratio (ADHD proxy)
    "apf": 10.1,             // Alpha Peak Frequency in Hz
    "coherence": 0.614,      // inter-hemispheric coherence
    "bands": {
      "rel_delta": 0.28, "rel_theta": 0.18,
      "rel_alpha": 0.32, "rel_beta": 0.17, "rel_gamma": 0.05
    }
  }
}
```

此外还包括：`device`（状态、电池电量、固件版本）、`signal_quality`（每个电极的数值范围为0–1）、`session`（持续时间、训练轮数）、`embeddings`、`labels`、`sleep`汇总信息以及历史记录。

### 解读输出结果

需解析JSON格式的数据，并将各项指标转化为自然语言进行描述。绝不能仅呈现原始数字，而应为其赋予实际意义：

**正确做法：**
> “您目前的专注度为0.70，处于高度专注状态。心率稳定在68次/分钟，且FAA值呈正值，说明您有较强的学习动力。现在是处理复杂任务的绝佳时机。”

**错误做法：**
> “专注度：0.70，放松度：0.40，心率：68”

关键解读阈值（完整指南请参阅`references/metrics.md`）：
- **专注度 > 0.70** → 处于最佳专注状态，应予以保持
- **专注度 < 0.40** → 建议休息或调整策略
- **困倦度 > 0.60** → 存在疲劳风险，可能出现短暂睡眠
- **放松度 < 0.30** → 需要采取减压措施
- **认知负荷持续 > 0.70** → 建议倾诉心事或休息
- **TBR > 1.5** → 脑电波以θ波为主，执行控制能力下降
- **FAA < 0** → 出现消极情绪或注意力分散——建议重新平衡FAA值
- **SNR < 3 dB** → 信号质量不佳，建议重新调整电极位置

---

## 2. 会话分析

### 单次会话详情分解
```bash
npx neuroskill session --json         # most recent session
npx neuroskill session 1 --json       # previous session
npx neuroskill session 0 --json | jq '{focus: .metrics.focus, trend: .trends.focus}'
```

返回包含**上半段与下半段趋势**（`"up"`、`"down"`、`"flat"`）的完整指标数据。
可利用此信息描述会话的演变过程：

> “您的专注度起初为0.64，到会话结束时上升至0.76，呈现出明显的上升趋势。
> 认知负荷则从0.38降至0.28，说明随着您逐渐进入状态，该任务变得更加自动化。”

### 列出所有会话
```bash
npx neuroskill sessions --json
npx neuroskill sessions --trends      # show per-session metric trends
```

## 3. 历史检索

### 神经网络相似度检索
```bash
npx neuroskill search --json                    # auto: last session, k=5
npx neuroskill search --k 10 --json             # 10 nearest neighbors
npx neuroskill search --start <UTC> --end <UTC> --json
```

通过基于128维ZUNA嵌入的HNSW近似最近邻搜索，找出在特征上具有相似性的历史时刻。该功能可输出距离统计信息、时间分布（一天中的具体时段）以及最匹配的若干日期。

当用户提出以下问题时可使用此功能：
- “我上一次处于这种状态是在什么时候？”
- “帮我找到我最专注的时段。”
- “我通常在下午什么时间精力衰退？”

### 语义标签搜索
```bash
npx neuroskill search-labels "deep focus" --k 10 --json
npx neuroskill search-labels "stress" --json | jq '[.results[].EXG_metrics.tbr]'
```

该功能利用向量嵌入技术（Xenova/bge-small-en-v1.5）对标签文本进行检索，进而返回匹配的标签及其在标注时对应的EXG指标。 

### 跨模态图搜索
```bash
npx neuroskill interactive "deep focus" --json
npx neuroskill interactive "deep focus" --dot | dot -Tsvg > graph.svg
```

四层图结构：查询 → 文本标签 → EXG点 → 相邻标签。可通过`--k-text`、`--k-EXG`以及`--reach <minutes>`参数对相关参数进行调优。

---

## 4. 会话对比功能
```bash
npx neuroskill compare --json                   # auto: last 2 sessions
npx neuroskill compare --a-start <UTC> --a-end <UTC> --b-start <UTC> --b-end <UTC> --json
```

该功能会为约50项指标返回包含绝对变化值、百分比变化率以及变化方向的指标差异数据。此外，它还会提供`insights.improved[]`和`insights.declined[]`数组、两次会话的睡眠阶段信息，以及UMAP任务的编号。

在解读这些对比数据时，应结合具体情境进行说明——不仅要提及数值变化，还需分析趋势：
> “昨天您有两次专注时间段表现优异（上午10点和下午2点）。而今天则从上午11点左右开始出现一次仍持续中的专注时段。虽然今天的整体专注度更高，但压力峰值更为频繁——您的压力指数上升了15%，而疲劳感也更多次出现负向波动。”

```bash
# Sort metrics by improvement percentage
npx neuroskill compare --json | jq '.insights.deltas | to_entries | sort_by(.value.pct) | reverse'
```

## 5. 睡眠数据
```bash
npx neuroskill sleep --json                     # last 24 hours
npx neuroskill sleep 0 --json                   # most recent sleep session
npx neuroskill sleep --start <UTC> --end <UTC> --json
```

返回按睡眠阶段划分的详细数据（时间间隔为5秒），并附有相关分析结果：
- **阶段代码**：0=清醒期，1=N1期，2=N2期，3=N3期（深度睡眠），4=REM期
- **分析指标**：效率百分比、入睡延迟分钟数、REM睡眠延迟分钟数、各阶段持续时间次数
- **健康标准**：N3期占比15–25%，REM期占比20–25%，睡眠效率>85%，入睡时间<20分钟

```bash
npx neuroskill sleep --json | jq '.summary | {n3: .n3_epochs, rem: .rem_epochs}'
npx neuroskill sleep --json | jq '.analysis.efficiency_pct'
```

当用户提及睡眠、疲劳或恢复相关内容时，请使用此标签。
```bash
npx neuroskill label "breakthrough"
npx neuroskill label "studying algorithms"
npx neuroskill label "post-meditation"
npx neuroskill label --json "focus block start"   # returns label_id
```

系统会自动标记以下时刻：
- 用户报告取得突破或获得新见解
- 用户开始执行新的任务类型（例如“切换到代码审查”）
- 用户完成一项重要的工作流程
- 用户要求您标记当前时刻
- 发生显著的状态变化（进入/离开某个流程）

这些标签会被存储在数据库中并建立索引，以便日后通过 `search-labels` 以及 `interactive` 命令进行检索。 

---

## 7. 实时流处理
```bash
npx neuroskill listen --seconds 30 --json
npx neuroskill listen --seconds 5 --json | jq '[.[] | select(.event == "scores")]'
```

在指定时间内持续传输实时 WebSocket 事件（EXG、PPG、IMU、得分及标签数据）。该功能需要 WebSocket 连接（不支持通过 `--http` 参数使用）。

适用于需要持续监控的场景，或希望在协议运行过程中实时观察各项指标的变化。
```bash
npx neuroskill umap --json                      # auto: last 2 sessions
npx neuroskill umap --a-start <UTC> --a-end <UTC> --b-start <UTC> --b-end <UTC> --json
```

基于 GPU 加速的 ZUNA 嵌入向量 3D UMAP 可视化投影。`separation_score` 值用于指示两次脑电活动的神经差异程度：
- **> 1.5** → 两次脑电活动在神经层面存在显著差异（代表不同的脑状态）
- **< 0.5** → 两次脑电活动所对应的脑状态十分相似

---

## 9. 主动状态感知

### 会话开始时检查
在每次会话开始时，如果用户提及自己正在佩戴设备或询问当前状态，系统可可选地执行状态检测：
```bash
npx neuroskill status --json
```

插入简短的状态概要：
> “快速状态检查：专注力为0.62，放松程度为0.55，且您的FAA值呈正值——表明您有较强的任务投入动机。这是个不错的开端。”

### 何时主动提及状态信息

仅在以下情况才提及认知状态：
- 用户明确询问（如“我现在的状态如何？”、“帮我检查一下专注力”）
- 用户表示难以集中注意力、感到压力或疲劳
- 达到临界阈值（嗜睡程度>0.70，专注力持续<0.30）
- 用户即将进行需要高度认知能力的任务，并询问是否已做好准备

**切勿**为了报告各项指标而打断用户的当前状态。如果专注力>0.75，应保持当前会话的连贯性——此时最恰当的做法是保持沉默。

---

## 10. 建议使用相关方案

当各项指标表明有需求时，可从 `references/protocols.md` 中推荐相应的方案。在开始之前务必先征得用户同意——绝不能打断用户的当前状态：

> “过去15分钟内您的专注力持续下降，TBR值也已超过1.5——这可能是θ脑波占主导且出现精神疲劳的迹象。需要我为您演示一下θ-β神经反馈训练吗？这是一种时长为90秒的练习，通过有节奏的计数和呼吸来抑制θ脑波并提升β脑波活动。”

常见触发场景：
- **专注力<0.40，TBR>1.5** → 采用θ-β神经反馈训练或箱式呼吸法
- **放松程度<0.30，压力指数较高** → 采用心脏协调训练或4-7-8呼吸法
- **认知负荷持续>0.70** → 采用认知负荷卸载法（思维倾倒法）
- **嗜睡程度>0.60** → 采用超日节律重置法或清醒重置法
- **FAA值<0（呈负值）** → 需进行FAA值平衡调整
- **处于心流状态（专注力>0.75，投入度>0.70）** → 不要打断
- **静止状态严重且头痛指数较高** → 采用颈部放松训练序列
- **RMSSD值较低（<25毫秒）** → 采用迷走神经调节法

---

## 11. 其他工具

### 专注力计时器
```bash
npx neuroskill timer --json
```
启动专注计时器窗口，提供番茄工作法（25/5）、深度工作模式（50/10）以及短时专注模式（15/5）等多种预设选项。

### 校准设置
```bash
npx neuroskill calibrate
npx neuroskill calibrate --profile "Eyes Open"
```
打开校准窗口。在信号质量较差或用户希望建立个性化基准值时非常有用。

### 操作系统通知
```bash
npx neuroskill notify "Break Time" "Your focus has been declining for 20 minutes"
```

### 原始 JSON 直传功能
```bash
npx neuroskill raw '{"command":"status"}' --json
```
对于尚未映射到 CLI 子命令的任何服务器命令。

---

## 错误处理

| 错误信息 | 可能原因 | 解决方案 |
|---------|---------|----------|
| `npx neuroskill status` 卡住 | NeuroSkill 应用未运行 | 启动 NeuroSkill 桌面应用 |
| `device.state: "disconnected"` | BCI 设备未连接 | 检查蓝牙连接及设备电池状态 |
| 所有评分均为 0 | 电极接触不良 | 调整头带位置并湿润电极 |
| `signal_quality` 值 < 0.7 | 电极松动 | 调整电极贴合度并清洁电极接触面 |
| SNR < 3 dB | 信号噪声较大 | 减少头部移动并检查周围环境 |
| `command not found: npx` | 未安装 Node.js | 安装 Node.js 20 及以上版本 |

---

## 使用示例

**“我目前的表现如何？”**
```bash
npx neuroskill status --json
```
→ 自然地解读各项分数，说明专注度、放松程度、情绪状态以及任何值得注意的比率（如 FAA、TBR）。仅当数据指标表明有必要时，才提出相应的建议。

**“我无法集中注意力”**
```bash
npx neuroskill status --json
```
→ 检查各项指标是否能够佐证这一情况（高θ值、低β值、TBR持续上升以及较高的困倦度）。  
→ 若指标确实如此，则从 `references/protocols.md` 中推荐合适的干预方案。  
→ 若各项指标均正常，那么问题可能出在动机层面而非神经层面。  

**“对比我今天的专注力与昨日”**
```bash
npx neuroskill compare --json
```
→ 不仅要分析数据数值，更要解读背后的趋势。需指出哪些方面有所改善，哪些方面出现下滑，以及可能的原因。

**“我上一次进入心流状态是在何时？”**
```bash
npx neuroskill search-labels "flow" --json
npx neuroskill search --json
```
→ 报告时间戳、相关指标，以及根据标签所显示的用户当时正在进行的操作。

**“我的睡眠质量如何？”**
```bash
npx neuroskill sleep --json
```
→ 报告睡眠结构数据（N3期占比、REM期占比及睡眠效率），并与健康标准进行对比，同时标注可能出现的问题（如清醒时长过长、REM期过短等）。

**“记住这一刻——我刚刚有了重大突破！”**
```bash
npx neuroskill label "breakthrough"
```
→ 确认标签已保存。如需，可记录当前的指标数值以便记住当前状态。
