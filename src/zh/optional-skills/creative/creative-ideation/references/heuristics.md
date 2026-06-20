# 路由策略

用于选择生成方法的决策树。请从上至下阅读，第一个匹配项即为最佳选择。

## 阶段信号——用户当前处于哪个阶段？

| 信号 | 方法 |
|---|---|
| 空白页面，无主题领域 | 约束调度（`full-prompt-library.md`） |
| 有主题领域，无具体项目 | 按领域路由（见下一节） |
| 已有一个创意，希望获得更多变体 | `methods/scamper.md` |
| 需要快速生成大量创意 | `methods/volume-generation.md` |
| 创意过于保守 | `methods/lateral-provocations.md` |
| 有众多创意，需从中筛选 | `methods/premortem-and-inversion.md` |
| 已有创意，希望进一步优化 | `methods/creative-discipline.md`（Tharp的“纪律法则”） |
| 项目进行到中途陷入瓶颈 | `methods/oblique-strategies.md` |
| “这个创意行得通吗？” | `methods/premortem-and-inversion.md` + `methods/compression-progress.md` |

## 主题领域信号

| 主题领域 | 方法 |
|---|---|
| 具有形式美要求的虚构作品 | `methods/oulipo.md` |
| 具有叙事结构的作品 | `methods/story-skeletons.md` |
| 散文/非虚构类内容 | `methods/defamiliarization.md` + `methods/compression-progress.md` |
| 诗歌 | `methods/oulipo.md` 或 `methods/chance-and-remix.md` |
| 歌词/歌曲创作 | `methods/oblique-strategies.md` + `methods/chance-and-remix.md` |
| 音乐/声音艺术 | `methods/oblique-strategies.md`（其起源领域） |
| 视觉艺术/雕塑/装置艺术 | `methods/oblique-strategies.md`, `methods/creative-discipline.md`（LeWitt理论） |
| 表演艺术/戏剧 | `methods/defamiliarization.md`（Brecht理论） |
| 场地特定型创作 | `methods/derive-and-mapping.md` |
| 工程发明 | `methods/triz-principles.md` |
| 软件架构设计 | `methods/pattern-languages.md` |
| 算法/数据结构 | `methods/polya.md` + `methods/first-principles.md` |
| 公民参与/政策制定 | `methods/leverage-points.md` |
| 组织架构设计 | `methods/leverage-points.md` + `methods/pattern-languages.md` |
| 研究/选题确定 | `methods/compression-progress.md` |
| 解决已知问题 | `methods/polya.md` + `methods/first-principles.md` |
| 产品战略/功能设计理由 | `methods/jobs-to-be-done.md` |
| 从零开始创建新项目 | `full-prompt-library.md` “解决自身需求” + `methods/jobs-to-be-done.md` |
| 职业规划/学习方向选择 | `methods/derive-and-mapping.md` + `methods/compression-progress.md` |
| 习惯养成/自律训练 | `methods/creative-discipline.md` |

## 情绪/风格信号

| 用户需求 | 方法 |
|---|---|
| 追求优美/优雅的风格 | `methods/compression-progress.md` |
| 喜欢怪异/奇特的风格 | `methods/pataphysics.md`, `methods/chance-and-remix.md` |
| 需要实用/可行的方案 | `methods/triz-principles.md`, `methods/jobs-to-be-done.md`, “解决自身需求” |
| 希望内容有趣/富有趣味性 | `methods/oulipo.md`, `methods/oblique-strategies.md` |
| 需要严肃/严谨的成果 | `methods/polya.md`, `methods/first-principles.md`, `methods/compression-progress.md` |
| 希望内容具有个人化/亲密感 | `methods/creative-discipline.md`, `methods/derive-and-mapping.md` |
| 涉及政治/干预类主题 | `methods/leverage-points.md`, `methods/chance-and-remix.md`（解构重组手法） |
| 需要批判性/颠覆性的视角 | `methods/defamiliarization.md`, `methods/pataphysics.md` |

## 何时叠加使用多种方法（较少见）

大多数情况下只需使用一种方法。仅在以下情形才考虑叠加：

- **领域专用方法 + 刺激性策略**：当仅依靠领域约束容易产生可预测结果时，可结合OuLiPo规则与de Bono的PO法。
- **生成创意 + 筛选优化**：先通过“疯狂8点法”生成大量创意，再对其中前三项进行事前分析。
- **自由发散 + 模式映射**：先进行自由发散，再通过亲和力映射法进行筛选。
- **理论分析 + 实践应用**：先用TRIZ找出矛盾点，再用仿生学方法寻找解决方案。

**反模式**：叠加三种及以上方法。这会变成流程化操作，而非真正的创意生成过程。

## 边界情况处理

- **输入的提示过于模糊，无法匹配任何路径** → 采用最接近的约束条件进行调度。
- **用户要求推荐方法而非创意** → 提出2–3种候选方法，由用户选择具体使用哪种，不要擅自默认。
- **主题领域过于宽泛**（如“AI创意”“创业点子”“习惯追踪工具”等） → 强制使用`methods/lateral-provocations.md`或`methods/pataphysics.md`，而非最常规的方法。应拒绝前5个创意，而非仅3个。
- **重复提出相同问题** → 更换生成方法。方法的不同会导致创意分布的差异。
- **用户感到沮丧，认为所有创意都很糟糕** → 停止继续生成创意。可使用`methods/creative-discipline.md`（Cleese的开放模式或Tharp的刮擦法）。有时正确的做法是停止创意生成。
- **用户希望被劝阻不要开始某个项目** → 采用事前分析法和逆向思维法。有时最合适的答案就是“不要这么做”。

## 反模式清单

1. 当用户提供了明确的领域信号时，仍默认使用约束调度。应先阅读这些信号。
2. 在没有初始创意的情况下直接使用SCAMPER法。SCAMPER法是用于优化已有创意，而非从无到有地生成创意。
3. 将TRIZ方法用于艺术或社会问题。该方法的适用场景主要是物理/工程领域。
4. 在单一创作者主导的项目中使用“杠杆点”分析法。这种做法过于复杂——Meadows理论更适合多主体系统。
5. 为显得高深而选择最复杂的 方法。大多数情况下，约束调度法就已足够。
6. 为了弥补选择不当而叠加多种方法。错误的组合依然不会产生更好的结果。
7. 当用户仅要求方向指导时，就直接生成完整作品。应等待用户明确选择具体方案后再进行生成。
