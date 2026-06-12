# NeuroSkill WebSocket与HTTP API参考文档

NeuroSkill会运行一个本地服务器（默认端口为**8375**），该服务器可通过mDNS（`_skill._tcp`）被发现。它同时提供了WebSocket和HTTP接口。 

---

## 服务器发现

```bash
# Auto-discovery (built into the CLI — usually just works)
npx neuroskill status --json

# Manual port discovery
NEURO_PORT=$(lsof -i -n -P | grep neuroskill | grep LISTEN | awk '{print $9}' | cut -d: -f2 | head -1)
echo "NeuroSkill on port: $NEURO_PORT"
```

CLI会自动检测端口。如需手动指定，可使用`--port <N>`选项进行覆盖。

---

## HTTP REST接口

### 通用命令隧道
```bash
# POST / — accepts any command as JSON
curl -s -X POST http://127.0.0.1:8375/ \
  -H "Content-Type: application/json" \
  -d '{"command":"status"}'
```

### 便捷接口
| 方法 | 接口地址 | 描述 |
|------|----------|------|
| GET | `/v1/status` | 系统状态 |
| GET | `/v1/sessions` | 列出会话 |
| POST | `/v1/label` | 创建标签 |
| POST | `/v1/search` | 基于ANN的搜索功能 |
| POST | `/v1/compare` | A/B对比测试 |
| POST | `/v1/sleep` | 睡眠阶段检测 |
| POST | `/v1/notify` | 操作系统级通知 |
| POST | `/v1/say` | 文本转语音功能 |
| POST | `/v1/calibrate` | 启动校准流程 |
| POST | `/v1/timer` | 启动专注计时器 |
| GET | `/v1/dnd` | 查询勿扰模式状态 |
| POST | `/v1/dnd` | 强制开启/关闭勿扰模式 |
| GET | `/v1/calibrations` | 列出所有校准配置文件 |
| POST | `/v1/calibrations` | 创建新的校准配置文件 |
| GET | `/v1/calibrations/{id}` | 获取指定ID的配置文件 |
| PATCH | `/v1/calibrations/{id}` | 更新配置文件内容 |
| DELETE | `/v1/calibrations/{id}` | 删除配置文件 |

---

## WebSocket事件（广播）

连接到 `ws://127.0.0.1:8375/` 即可接收实时事件：

### EXG（原始脑电图数据）
```json
{"event": "EXG", "electrode": 0, "samples": [12.3, -4.1, ...], "timestamp": 1740412800.512}
```

### 光电容积脉搏波描记法
```json
{"event": "PPG", "channel": 0, "samples": [...], "timestamp": 1740412800.512}
```

### 惯性测量单元
```json
{"event": "IMU", "ax": 0.01, "ay": -0.02, "az": 9.81, "gx": 0.1, "gy": -0.05, "gz": 0.02}
```

### 分数（计算指标）
```json
{
  "event": "scores",
  "focus": 0.70, "relaxation": 0.40, "engagement": 0.60,
  "rel_delta": 0.28, "rel_theta": 0.18, "rel_alpha": 0.32,
  "rel_beta": 0.17, "hr": 68.2, "snr": 14.3
}
```

### EXG频带（频谱分析）
```json
{"event": "EXG-bands", "channels": [...], "faa": 0.12}
```

### 标签
```json
{"event": "label", "label_id": 42, "text": "meditation start", "created_at": 1740413100}
```

### 设备状态
```json
{"event": "muse-status", "state": "connected"}
```

## JSON响应格式

### `status`
```jsonc
{
  "command": "status", "ok": true,
  "device": {
    "state": "connected",     // "connected" | "connecting" | "disconnected"
    "name": "Muse-A1B2",
    "battery": 73,
    "firmware": "1.3.4",
    "EXG_samples": 195840,
    "ppg_samples": 30600,
    "imu_samples": 122400
  },
  "session": {
    "start_utc": 1740412800,
    "duration_secs": 1847,
    "n_epochs": 369
  },
  "signal_quality": {
    "tp9": 0.95, "af7": 0.88, "af8": 0.91, "tp10": 0.97
  },
  "scores": {
    "focus": 0.70, "relaxation": 0.40, "engagement": 0.60,
    "meditation": 0.52, "mood": 0.55, "cognitive_load": 0.33,
    "drowsiness": 0.10, "hr": 68.2, "snr": 14.3, "stillness": 0.88,
    "bands": { "rel_delta": 0.28, "rel_theta": 0.18, "rel_alpha": 0.32, "rel_beta": 0.17, "rel_gamma": 0.05 },
    "faa": 0.042, "tar": 0.56, "bar": 0.53, "tbr": 1.06,
    "apf": 10.1, "coherence": 0.614, "mu_suppression": 0.031
  },
  "embeddings": { "today": 342, "total": 14820, "recording_days": 31 },
  "labels": { "total": 58, "recent": [{"id": 42, "text": "meditation start", "created_at": 1740413100}] },
  "sleep": { "total_epochs": 1054, "wake_epochs": 134, "n1_epochs": 89, "n2_epochs": 421, "n3_epochs": 298, "rem_epochs": 112, "epoch_secs": 5 },
  "history": { "total_sessions": 63, "recording_days": 31, "current_streak_days": 7, "total_recording_hours": 94.2, "longest_session_min": 187, "avg_session_min": 89 }
}
```

### `sessions`
```jsonc
{
  "command": "sessions", "ok": true,
  "sessions": [
    { "day": "20260224", "start_utc": 1740412800, "end_utc": 1740415510, "n_epochs": 541 },
    { "day": "20260223", "start_utc": 1740380100, "end_utc": 1740382665, "n_epochs": 513 }
  ]
}
```

### `session`（单次会话详情）
```jsonc
{
  "ok": true,
  "metrics": { "focus": 0.70, "relaxation": 0.40, "n_epochs": 541 /* ... ~50 metrics */ },
  "first":   { "focus": 0.64 /* first-half averages */ },
  "second":  { "focus": 0.76 /* second-half averages */ },
  "trends":  { "focus": "up", "relaxation": "down" /* "up" | "down" | "flat" */ }
}
```

### `compare`（A/B对比功能）
```jsonc
{
  "command": "compare", "ok": true,
  "insights": {
    "deltas": {
      "focus": { "a": 0.62, "b": 0.71, "abs": 0.09, "pct": 14.5, "direction": "up" },
      "relaxation": { "a": 0.45, "b": 0.38, "abs": -0.07, "pct": -15.6, "direction": "down" }
    },
    "improved": ["focus", "engagement"],
    "declined": ["relaxation"]
  },
  "sleep_a": { /* sleep summary for session A */ },
  "sleep_b": { /* sleep summary for session B */ },
  "umap": { "job_id": "abc123" }
}
```

### `search`（基于近似最近邻的相似度搜索）
```jsonc
{
  "command": "search", "ok": true,
  "result": {
    "results": [{
      "neighbors": [{ "distance": 0.12, "metadata": {"device": "Muse-A1B2", "date": "20260223"} }]
    }],
    "analysis": {
      "distance_stats": { "mean": 0.15, "min": 0.08, "max": 0.42 },
      "temporal_distribution": { /* hour-of-day distribution */ },
      "top_days": [["20260223", 5], ["20260222", 3]]
    }
  }
}
```

### `sleep`（睡眠阶段检测）
```jsonc
{
  "command": "sleep", "ok": true,
  "summary": { "total_epochs": 1054, "wake_epochs": 134, "n1_epochs": 89, "n2_epochs": 421, "n3_epochs": 298, "rem_epochs": 112, "epoch_secs": 5 },
  "analysis": { "efficiency_pct": 87.3, "onset_latency_min": 12.5, "rem_latency_min": 65.0, "bouts": { /* wake/n3/rem bout counts and durations */ } },
  "epochs": [{ "utc": 1740380100, "stage": 0, "rel_delta": 0.15, "rel_theta": 0.22, "rel_alpha": 0.38, "rel_beta": 0.20 }]
}
```

### `label`
```json
{"command": "label", "ok": true, "label_id": 42}
```

### `search-labels`（语义搜索）
```jsonc
{
  "command": "search-labels", "ok": true,
  "results": [{
    "text": "deep focus block",
    "EXG_metrics": { "focus": 0.82, "relaxation": 0.35, "engagement": 0.75, "hr": 65.0, "mood": 0.60 },
    "EXG_start": 1740412800, "EXG_end": 1740412805,
    "created_at": 1740412802,
    "similarity": 0.92
  }]
}
```

### `umap`（3D投影）
```jsonc
{
  "command": "umap", "ok": true,
  "result": {
    "points": [{ "x": 1.23, "y": -0.45, "z": 2.01, "session": "a", "utc": 1740412800 }],
    "analysis": {
      "separation_score": 1.84,
      "inter_cluster_distance": 2.31,
      "intra_spread_a": 0.82, "intra_spread_b": 0.94,
      "centroid_a": [1.23, -0.45, 2.01],
      "centroid_b": [-0.87, 1.34, -1.22]
    }
  }
}
```

## 实用的 `jq` 代码片段

```bash
# Get just focus score
npx neuroskill status --json | jq '.scores.focus'

# Get all band powers
npx neuroskill status --json | jq '.scores.bands'

# Check device battery
npx neuroskill status --json | jq '.device.battery'

# Get signal quality
npx neuroskill status --json | jq '.signal_quality'

# Find improving metrics after a session
npx neuroskill session 0 --json | jq '[.trends | to_entries[] | select(.value == "up") | .key]'

# Sort comparison deltas by improvement
npx neuroskill compare --json | jq '.insights.deltas | to_entries | sort_by(.value.pct) | reverse'

# Get sleep efficiency
npx neuroskill sleep --json | jq '.analysis.efficiency_pct'

# Find closest neural match
npx neuroskill search --json | jq '[.result.results[].neighbors[]] | sort_by(.distance) | .[0]'

# Extract TBR from labeled stress moments
npx neuroskill search-labels "stress" --json | jq '[.results[].EXG_metrics.tbr]'

# Get session timestamps for manual compare
npx neuroskill sessions --json | jq '{start: .sessions[0].start_utc, end: .sessions[0].end_utc}'
```

## 数据存储

- **本地数据库**：`~/.skill/YYYYMMDD/`（SQLite + HNSW索引）
- **ZUNA嵌入向量**：128维向量，训练周期为5秒
- **标签数据**：存储在SQLite中，并通过bge-small-en-v1.5嵌入向量进行索引
- **所有数据均保存在本地**——不会上传至任何外部服务器
