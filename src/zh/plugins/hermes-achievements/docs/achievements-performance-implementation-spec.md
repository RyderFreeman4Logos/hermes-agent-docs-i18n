# Hermes 成就系统实现规范（详细版）

本文档为面向实现的详细说明，用于后续的性能优化重构工作。

决策范围：仅保留“成就”标签页的流程结构；移除 `/overview` 页面及顶部横幅区域的集成功能。

---

## A) 当前行为概述

- `evaluate_all()` 函数会执行以下操作：
  - 执行完整的 `scan_sessions()` 扫描
  - 调用 `SessionDB.list_sessions_rich(...)`
  - 针对每个会话调用 `db.get_messages(session_id)` 获取消息数据
  - 对文本及工具内容进行正则分析、聚合处理并最终进行评分计算
- 目前 `/overview` 和 `/achievements` 页面均直接调用 `evaluate_all()` 函数。
- 各个插槽功能（如 `sessions:top`、`analytics:top`）目前均通过调用 `/overview` 来实现相应功能。

由此导致的后果是：需要重复进行完整的计算操作，且各组件之间存在资源竞争问题。

---

## B) 范围缩减/移除的相关变更

1. 移除后端路由：
   - `GET /overview`

2. 移除前端页面中的相关插槽配置：
   - `SummarySlot` 组件
   - `registerSlot("sessions:top")` 函数
   - `registerSlot("analytics:top")` 函数

3. 删除配置文件中的插槽声明：
   - `"slots": ["sessions:top", "analytics:top"]`

4. 保留的内容包括：
   - “成就”标签页的路由及页面结构
   - `/achievements` 接口以及完整的标签页渲染功能

---

## C) 目标内部接口设计

### 1) `SnapshotStore` 接口
职责：
- 在内存中存储最新计算生成的快照数据
- 将快照数据持久化到磁盘或从磁盘加载数据
- 提供快照数据更新时间及过期状态检测功能

存储路径：
- `~/.hermes/plugins/hermes-achievements/scan_snapshot.json`

核心方法（概念性说明）：
- `get()` -> 返回快照数据或 `null`
- `set(snapshot)` -> 设置新的快照数据
- `is_stale(ttl_seconds)` -> 判断快照是否已过期

### 2) `ScanCoordinator` 接口
职责：
- 对计算任务实施单次执行保护机制
- 跟踪扫描任务的执行状态

核心方法：
- `run_if_needed(force: bool = false)` -> 根据需要启动计算任务
- `get_status()` -> 获取当前任务状态

状态字段包括：
- `state`：`idle`（空闲）、`running`（运行中）、`failed`（失败）
- `started_at`、`finished_at`：任务开始时间与结束时间
- `last_error`：上次出现的错误信息
- `run_count`：任务执行次数

### 3) `build_snapshot()` 函数
职责：
- 仅执行一次当前的计算逻辑
- 在首次运行时，执行完整扫描并计算每个会话的贡献值
- 在后续运行时，通过检查点指纹识别出发生变化或新增的会话，仅对这些会话进行处理
- 生成 `/achievements` 页面所需的数据结构

输出内容包括：
- `achievements` 数组，包含各项成就数据
- 计数相关字段
- 可选的 `scan_meta` 元数据

---

## D) 接口行为矩阵（无 `/overview` 页面时）

| 接口地址 | 使用缓存的数据 | 使用过期缓存的数据 | 不使用缓存 | 强制重新扫描 |
|---|---|---|---|---|
| `/achievements` | 返回缓存中的数据 | 返回过期数据并触发后台刷新 | 执行阻塞式的完整扫描 | 无此选项 |
| `/rescan` | 触发数据刷新 | 触发数据刷新 | 触发数据刷新 | 是 |
| `/scan-status` | 仅返回状态信息 | 仅返回状态信息 | 仅返回状态信息 | 仅返回状态信息 |

备注：
- 任何时刻最多只有一个扫描任务处于运行状态。
- 其他调用方要么等待当前正在运行的任务完成，要么根据既定策略接收过期版本的快照数据。

---

## E) 数据结构设计（拟议方案）

```json
{
  "generated_at": 0,
  "is_stale": false,
  "scan_meta": {
    "duration_ms": 0,
    "sessions_scanned": 0,
    "messages_scanned": 0,
    "mode": "full",
    "error": null
  },
  "achievements": [],
  "unlocked_count": 0,
  "discovered_count": 0,
  "secret_count": 0,
  "total_count": 0,
  "error": null
}
```

兼容性指南：
- 保留现有的 `/achievements` 键。
- 添加元数据键，同时不影响现有调用方的使用。

检查点文件（新版本）：
- `~/.hermes/plugins/hermes-achievements/scan_checkpoint.json`

推荐的检查点结构：
```json
{
  "schema_version": 1,
  "generated_at": 0,
  "sessions": {
    "<session_id>": {
      "fingerprint": {
        "updated_at": 0,
        "message_count": 0,
        "hash": "optional"
      },
      "contribution": {
        "metrics": {}
      }
    }
  }
}
```

**备注：**  
- 指纹不匹配 => 仅重新计算该会话的贡献值。  
- 指纹未发生变化 => 直接复用已存储的贡献值。  

---  

## F) 并发契约  

- 所有需要获取最新数据的请求路径都必须通过单次执行协调器处理。  
- 若当前正在执行扫描任务：  
  - 不得启动新的扫描；  
  - 要么等待正在进行的扫描完成（设置时间限制），要么立即提供过时的快照。  
- 锁定范围必须涵盖扫描任务的开始与结束状态转换。  

---  

## G) 错误处理契约  

- 若刷新失败且存在之前的快照：  
  - 返回该旧快照，并标注 `is_stale=true` 及相关的错误元数据。  
- 若刷新失败且不存在之前的快照：  
  - 返回明确的错误响应（当前行为与之一致）。  
- `scan-status` 应始终返回最新的已知状态或错误信息。  

---  

## H) 前端集成契约  

- 成就页面：  
  - 页面加载时仅向 `/achievements` 发送一次请求；  
  - 若快照已过期，可可选地显示后台刷新指示器。  
- 不支持顶部横幅区域集成。  
- 通过取消请求或延迟处理的方式，避免在快速切换页面时产生重复的正在执行中的请求。  

---  

## I) 验证清单  

- [ ] 已移除 `/overview` 路由。  
- [ ] 配置文件中不存在 `sessions:top`/`analytics:top` 类型的字段。  
- [ ] 前端代码中不存在对 `api("/overview")` 的调用。  
- [ ] 多次切换至成就页面时不会触发多次耗时的扫描任务。  
- [ ] 平均冷启动加载时间符合服务级别目标要求。  
- [ ] 解锁总数与重构前的相同历史数据基准值一致。  
- [ ] `/achievements` 的响应格式未出现架构退化问题。  

---  

## J) 后续开发建议的文件存放位置  

- 后端代码修改：`dashboard/plugin_api.py`  
- 可选的分离文件：  
  - `dashboard/perf_snapshot.py`  
  - `dashboard/perf_scan_coordinator.py`  
- 前端请求处理相关代码：`dashboard/dist/index.js`（若有源码则使用源文件）。  
- 插件元数据文件：`dashboard/manifest.json`  
- 持久化运行时文件：  
  - `~/.hermes/plugins/hermes-achievements/state.json`（存储现有的解锁状态）  
  - `~/.hermes/plugins/hermes-achievements/scan_snapshot.json`（存储新生成的快照）  
  - `~/.hermes/plugins/hermes-achievements/scan_checkpoint.json`（存储新生成的扫描检查点）  

---  

## K) 实施后的报告模板  

需记录以下内容：  
- 数据集规模（会话数、消息数、工具调用次数）。  
- `/achievements` 页面的加载时间，分别统计冷启动和热启动情况下的数值。  
- 在多次打开标签页时是否触发了单次执行去重机制。  
- 解锁计数方面出现的任何行为差异。
