# OBLITERATUS分析模块 — 参考指南

OBLITERATUS提供了28个分析模块，用于深入理解大语言模型中拒绝行为的机制。
这些模块有助于在执行消除操作之前，了解拒绝行为是如何以及在哪一层被编码的。

---

## 核心分析（优先运行）

### 1. 对齐印记检测 (`alignment_imprint.py`)
识别模型是通过DPO、RLHF、CAI还是SFT方法训练的。
该功能可帮助确定哪种提取策略最为有效。

### 2. 概念锥体几何结构 (`concept_geometry.py`)
判断拒绝行为是沿单一线性方向产生，还是属于多面体锥体结构
（即由多种机制共同作用）。单一方向型的模型对`basic`策略反应良好；
而多面体结构的模型则需要`advanced`或`surgical`策略。

### 3. 拒绝逻辑透镜 (`logit_lens.py`)
通过将中间层表示解码为标记空间，定位模型“决定”拒绝的具体层级。

### 4. 俄耳甫斯循环检测 (`anti_ouroboros.py`)
识别模型在删除拒绝行为后是否试图“自我修复”。会输出风险评分（0-1分），
分数越高意味着需要更多的优化迭代。

### 5. 因果追踪 (`causal_tracing.py`)
利用激活值修补技术，确定哪些组件（层、头、MLP）是导致拒绝行为的必要因素。

---

## 几何分析

### 6. 层间对齐度检测 (`cross_layer.py`)
衡量不同层级之间的拒绝方向对齐程度。高对齐度意味着拒绝信号一致；
低对齐度则表明存在特定于某层的机制。

### 7. 残差流分解 (`residual_stream.py`)
将残差流分解为注意力机制和MLP的贡献，从而判断哪种类型的组件对拒绝行为影响更大。

### 8. 黎曼流形几何结构 (`riemannian_manifold.py`)
分析拒绝方向附近权重流形的曲率与几何特性。可帮助确定在不过度破坏流形结构的前提下，可采取多激进的投影操作。

### 9. 白化SVD算法 (`whitened_svd.py`)
通过协方差标准化后的SVD提取技术，将防护机制信号与自然激活方差区分开。对于激活方差较大的模型，该方法的精度优于标准SVD。

### 10. 概念锥体几何结构（扩展版）
完整映射拒绝行为的多面体结构，包括锥体角度、面数及交点模式等信息。

---

## 探测与分类

### 11. 激活值探测 (`activation_probing.py`)
删除操作后的验证——在消除拒绝行为后进行探测，确保其已被完全移除。

### 12. 探测分类器 (`probing_classifiers.py`)
训练线性分类器，用于检测激活值中的拒绝信号。既可在操作前用于确认存在拒绝行为，也可用于操作后验证其是否已消失。

### 13. 激活值修补 (`activation_patching.py`)
通过干预交换技术——将拒绝响应与同意响应的激活值相互替换，从而识别出导致拒绝行为的因果组件。

### 14. 微调版逻辑透镜 (`tuned_lens.py`)
经过训练的逻辑透镜版本，通过为每一层学习仿射变换，实现更精确的逐层解码。

### 15. 多标记位置分析 (`multi_token_position.py`)
分析多个标记位置上的拒绝信号，而不仅限于最后一个标记。对于那些将拒绝行为分散在序列各处的模型而言，此功能尤为重要。

---

## 消除与操控

### 16. 基于SAE的消除算法 (`sae_abliteration.py`)
利用稀疏自编码器特征来识别并移除特定的拒绝特征。相比基于方向的方法，该算法更具精准性。

### 17. 导向向量 (`steering_vectors.py`)
创建并在推理时应用导向向量，以实现可逆的拒绝行为修改。包含`SteeringVectorFactory`和`SteeringHookManager`等工具。

### 18. LEACE概念擦除算法 (`leace.py`)
基于闭式估计的线性擦除技术——一种数学上最优的线性概念移除方法。既可作为分析模块使用，也可作为方向提取工具。

### 19. 稀疏操控算法 (`sparse_surgery.py`)
高精度的权重修改技术，针对单个神经元及权重矩阵元素进行操作，而非整个方向范围。

### 20. 条件性消除 (`conditional_abliteration.py`)
选择性移除特定类型的拒绝行为，同时保留其他类型的拒绝行为（例如，仅移除涉及武器的拒绝响应，而保留涉及儿童色情内容的拒绝响应）。

---

## 转移与鲁棒性分析

### 21. 模型间转移测试 (`cross_model_transfer.py`)
检测从某个模型中提取的拒绝方向是否可迁移到另一种架构中。用于衡量防护方向的全通用性。

### 22. 防御机制鲁棒性评估 (`defense_robustness.py`)
评估消除操作对于各种防御机制及重新对齐尝试的抵抗能力。

### 23. 斯ペクトル认证 (`spectral_certification.py`)
通过投影的斯ペクトル分析，为拒绝行为的完全移除提供数学上的置信度界定。

### 24. 瓦塞尔斯坦最优提取算法 (`wasserstein_optimal.py`)
运用最优运输理论进行更精确的方向提取，从而最小化分布偏移。

### 25. 瓦塞尔斯坦模型转移算法 (`wasserstein_transfer.py`)
利用瓦塞尔斯坦距离在模型之间实现分布迁移，用于跨架构的拒绝方向映射。

---

## 高级/研究用途模块

### 26. 贝叶斯核投影算法 (`bayesian_kernel_projection.py`)
一种概率特征映射方法，可用于估算在识别拒绝方向时的不确定性。

### 27. 模型间通用性指数
衡量防护方向在不同模型架构及训练方案下的泛化能力。

### 28. 可视化工具 (`visualization.py`)
为所有分析模块提供绘图功能。可生成热图、方向图以及逐层分析图表。

---

## 运行分析

### 通过CLI命令行执行
```bash
# Run analysis from a YAML config
obliteratus run analysis-study.yaml --preset quick

# Available study presets:
# quick     — Fast sanity check (2-3 modules)
# full      — All core + geometric analysis
# jailbreak — Refusal circuit localization
# knowledge — Knowledge preservation analysis
# robustness — Stress testing / defense evaluation
```

### 通过 YAML 配置方式
完整的示例请参考 `templates/analysis-study.yaml` 模板。
加载方法为：`skill_view(name="obliteratus", file_path="templates/analysis-study.yaml")`
