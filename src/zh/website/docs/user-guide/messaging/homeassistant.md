---
title: Home Assistant
description: Control your smart home with Hermes Agent via Home Assistant integration.
sidebar_label: Home Assistant
sidebar_position: 5
---

# 与 Home Assistant 的集成

Hermes Agent 可通过两种方式与 [Home Assistant](https://www.home-assistant.io/) 实现集成：

1. **网关平台** —— 通过 WebSocket 订阅实时状态变化，并对相关事件作出响应  
2. **智能家居工具** —— 提供四种可通过 LLM 调用的工具，借助 REST API 对设备进行查询与控制  

## 设置步骤

### 1. 创建长期有效访问令牌

1. 打开您的 Home Assistant 实例  
2. 进入 **个人资料** 页面（在侧边栏点击您的姓名）  
3. 滚动到 **长期有效访问令牌** 选项  
4. 点击 **创建令牌**，为其指定一个名称，例如 “Hermes Agent”  
5. 复制该令牌内容  

### 2. 配置环境变量

```bash
# Add to ~/.hermes/.env

# Required: your Long-Lived Access Token
HASS_TOKEN=your-long-lived-access-token

# Optional: HA URL (default: http://homeassistant.local:8123)
HASS_URL=http://192.168.1.100:8123
```

:::info
一旦设置了 `HASS_TOKEN`，`homeassistant` 工具集便会自动启用。通过该令牌即可同时激活网关平台及设备控制工具。
:::

### 3. 启动网关

```bash
hermes gateway
```

在 Home Assistant 以及其他消息平台（如 Telegram、Discord 等）旁边，它会作为已连接的平台显示出来。

## 可用工具

Hermes Agent 注册了四种用于智能家居控制的工具：

### `ha_list_entities`

列出 Home Assistant 中的所有实体，可选择按领域或区域进行过滤。

**参数：**
- `domain` *(可选)* — 按实体领域过滤：`light`、`switch`、`climate`、`sensor`、`binary_sensor`、`cover`、`fan`、`media_player` 等。
- `area` *(可选)* — 按区域/房间名称过滤（匹配友好名称）：`living room`、`kitchen`、`bedroom` 等。

**示例：**
```
List all lights in the living room
```

返回实体 ID、状态以及友好的名称。

### `ha_get_state`

获取单个实体的详细状态，包括所有属性（亮度、颜色、温度设定值、传感器读数等）。

**参数：**
- `entity_id` *(必需)* — 需要查询的实体，例如 `light.living_room`、`climate.thermostat`、`sensor.temperature`

**示例：**
```
What's the current state of climate.thermostat?
```

返回值：状态、所有属性以及最后更改/更新的时间戳。

### `ha_list_services`

列出可用于设备控制的可用服务（操作）。显示针对每种设备类型可执行的操作及其接受的参数。

**参数：**
- `domain` *(可选)* — 按领域筛选，例如 `light`、`climate`、`switch`

**示例：**
```
What services are available for climate devices?
```

### `ha_call_service`

调用 Home Assistant 的服务以控制设备。

**参数：**
- `domain` *(必填)* — 服务类型：`light`、`switch`、`climate`、`cover`、`media_player`、`fan`、`scene`、`script`
- `service` *(必填)* — 服务名称：`turn_on`、`turn_off`、`toggle`、`set_temperature`、`set_hvac_mode`、`open_cover`、`close_cover`、`set_volume_level`
- `entity_id` *(可选)* — 目标设备标识，例如 `light.living_room`
- `data` *(可选)* — 以 JSON 对象形式提供的附加参数

**示例：**

```
Turn on the living room lights
→ ha_call_service(domain="light", service="turn_on", entity_id="light.living_room")
```

```
Set the thermostat to 22 degrees in heat mode
→ ha_call_service(domain="climate", service="set_temperature",
    entity_id="climate.thermostat", data={"temperature": 22, "hvac_mode": "heat"})
```

```
Set living room lights to blue at 50% brightness
→ ha_call_service(domain="light", service="turn_on",
    entity_id="light.living_room", data={"brightness": 128, "color_name": "blue"})
```

## 网关平台：实时事件

Home Assistant 网关适配器通过 WebSocket 进行连接，并订阅 `state_changed` 事件。当设备状态发生变化且符合您的过滤条件时，该变化信息会以消息形式被转发给代理。

### 事件过滤

:::warning 必需的配置
默认情况下，**不会转发任何事件**。您必须至少配置 `watch_domains`、`watch_entities` 或 `watch_all` 中的一项才能接收事件。若未设置过滤器，系统会在启动时输出警告，并默默丢弃所有状态变化信息。
:::

您可以在 `~/.hermes/config.yaml` 文件的 Home Assistant 平台 `extra` 部分中，配置代理应接收哪些事件：

```yaml
platforms:
  homeassistant:
    enabled: true
    extra:
      watch_domains:
        - climate
        - binary_sensor
        - alarm_control_panel
        - light
      watch_entities:
        - sensor.front_door_battery
      ignore_entities:
        - sensor.uptime
        - sensor.cpu_usage
        - sensor.memory_usage
      cooldown_seconds: 30
```

| 设置项 | 默认值 | 描述 |
|--------|--------|------|
| `watch_domains` | *(无)* | 仅监控这些实体类型对应的领域（例如 `climate`、`light`、`binary_sensor`） |
| `watch_entities` | *(无)* | 仅监控这些特定的实体 ID |
| `watch_all` | `false` | 设置为 `true` 可接收**所有**状态变化（不建议在大多数场景中使用） |
| `ignore_entities` | *(无)* | 始终忽略这些实体（在领域/实体过滤器之前生效） |
| `cooldown_seconds` | `30` | 同一实体的事件之间至少间隔的秒数 |

:::提示
建议先从一些核心领域开始使用——`climate`、`binary_sensor` 和 `alarm_control_panel` 能实现最实用的自动化功能。根据需求再逐步添加其他领域。可使用 `ignore_entities` 忽略那些干扰较大的传感器，比如 CPU 温度或运行时间计数器。
:::

### 事件格式

状态变化会根据所属领域以易于人类阅读的消息形式呈现：

| 领域 | 格式 |
|------|------|
| `climate` | “HVAC 模式从‘关闭’变为‘制热’（当前温度：21，目标温度：23）” |
| `sensor` | “温度从 21°C 变为 22°C” |
| `binary_sensor` | “触发” / “清除” |
| `light`、`switch`、`fan` | “开启” / “关闭” |
| `alarm_control_panel` | “警报状态从‘离家模式’变为‘已触发’” |
| *(其他领域)* | “从‘旧值’变为‘新值’” |

### Agent 响应

Agent 发送的出站消息会以**Home Assistant 持久通知**的形式传递（通过 `persistent_notification.create` 实现）。这些通知会出现在 HA 的通知面板中，标题为 “Hermes Agent”。

### 连接管理

- **WebSocket** 方式，通过 30 秒的心跳机制实现实时事件传输
- **自动重连**功能，重试间隔依次为：5秒 → 10秒 → 30秒 → 60秒
- **REST API** 用于发送出站通知（使用独立会话以避免与 WebSocket 冲突）
- **授权机制**——HA 发送的事件始终已过授权（无需用户白名单，因为 `HASS_TOKEN` 可用于验证连接）

## 安全性

Home Assistant 工具设置了多项安全限制：

:::警告 被阻止的领域
为防止在 HA 主机上执行任意代码，以下服务领域被**禁止使用**：

- `shell_command` — 任意 Shell 命令
- `command_line` — 可执行命令的传感器/开关
- `python_script` — Python 脚本执行功能
- `pyscript` — 更广泛的脚本集成能力
- `hassio` — 插件控制、主机关机/重启功能
- `rest_command` — 来自 HA 服务器的 HTTP 请求（存在 SSRF 风险）

尝试调用这些领域中的服务将会导致错误。
:::

为防止注入攻击，实体 ID 会经过模式验证，确保其符合 `^[a-z_][a-z0-9_]*\.[a-z0-9_]+$` 的格式要求。

## 实用自动化示例

### 晨间例行程序

```
User: Start my morning routine

Agent:
1. ha_call_service(domain="light", service="turn_on",
     entity_id="light.bedroom", data={"brightness": 128})
2. ha_call_service(domain="climate", service="set_temperature",
     entity_id="climate.thermostat", data={"temperature": 22})
3. ha_call_service(domain="media_player", service="turn_on",
     entity_id="media_player.kitchen_speaker")
```

### 安全检查

```
User: Is the house secure?

Agent:
1. ha_list_entities(domain="binary_sensor")
     → checks door/window sensors
2. ha_get_state(entity_id="alarm_control_panel.home")
     → checks alarm status
3. ha_list_entities(domain="lock")
     → checks lock states
4. Reports: "All doors closed, alarm is armed_away, all locks engaged."
```

### 基于网关事件的响应式自动化

当作为网关平台接入时，该智能体能够对各类事件做出响应：

```
[Home Assistant] Front Door: triggered (was cleared)

Agent automatically:
1. ha_get_state(entity_id="binary_sensor.front_door")
2. ha_call_service(domain="light", service="turn_on",
     entity_id="light.hallway")
3. Sends notification: "Front door opened. Hallway lights turned on."
```

## 故障排除

**环境变量未被识别。**
该适配器会从 `~/.hermes/.env` 文件（在启动时自动合并）或 `config.yaml` 文件中读取凭证。请仔细确认该文件位于当前激活的 Hermes 配置目录下，并且 URL 或令牌周围没有多余的引号。修改文件后需重启网关——环境变量的更改仅在进程启动时才会生效。

**“未找到对话实体”/智能体始终不回复。**
Home Assistant 的对话 API 需要配置好 *Assist* 对话智能体。在 Home Assistant 中，进入 **设置 → 语音助手 → 添加助手**，记下生成的实体 ID（通常为 `conversation.home_assistant` 或 `conversation.openai_<名称>`）。将该实体 ID 设置在适配器的 `conversation_entity` 参数中；某些版本可能不存在默认值。

**REST 认证失败（返回 `401 Unauthorized` 错误）。**
该令牌必须是通过 Home Assistant 的用户配置页面生成的*长期有效访问令牌*（路径为 **设置 → 安全 → 长期有效访问令牌**）。短期的 UI 会话令牌无法使用。同时，请确认基础 URL 包含协议和端口信息（例如 `http://homeassistant.local:8123`），并且从运行 Hermes 的主机上能够访问该地址——执行命令 `curl -H "Authorization: Bearer <token>" <url>/api/` 应该能返回 `{"message": "API running."}`。
