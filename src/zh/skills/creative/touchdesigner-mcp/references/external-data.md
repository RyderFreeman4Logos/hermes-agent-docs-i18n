# 外部数据引用

网络与设备 I/O — HTTP 请求、WebSockets、MQTT、串行通信、TCP、UDP。关于 MIDI/OSC 的具体用法，请参阅 `midi-osc.md` 文档。

常见的生产环境需求包括：
- API 轮询 / webhook 数据接收
- 实时数据流处理（传感器数据、市场数据、聊天信息）
- 物联网设备控制（Arduino、ESP32、智能灯等）
- 应用程序间消息传递
- 托管小型 TD 端 HTTP 服务器以实现远程控制

---

## Web DAT — HTTP 请求

```python
web = root.create(webDAT, 'api_call')
web.par.url = 'https://api.example.com/v1/status'
web.par.fetchmethod = 'get'           # 'get' | 'post' | 'put' | 'delete'
web.par.format = 'auto'                # 'auto' | 'text' | 'json'
web.par.timeout = 5.0
```

**触发请求：**

`webDAT` 在 cook 环境下不会自动获取数据。需手动明确触发：

```python
web.par.fetch.pulse()
```

或者通过 CHOP 值变化时的表达式来实现（使用 chopExecuteDAT——详情请参阅 `dat-scripting.md`）。

**身份验证标头：**

可以使用 `webclientDAT`（更为灵活），也可以通过 headers DAT 设置 `webDAT` 标头。

```python
web_headers = root.create(tableDAT, 'headers')
web_headers.appendRow(['Authorization', 'Bearer YOUR_TOKEN'])
web_headers.appendRow(['Accept', 'application/json'])
web.par.headers = web_headers.path
```

**解析 JSON 响应：**

```python
import json

def onTableChange(dat):
    response = dat.text          # raw response body
    data = json.loads(response)
    # Update a tableDAT or store in a constantCHOP for downstream use
    op('/project1/api_status').par.value0 = data['count']
    return
```

将其接入一个用于监控 webDAT 的 `datExecuteDAT` 中。  

**轮询模式：**

```python
# timerCHOP fires every N seconds
timer = root.create(timerCHOP, 'poll_timer')
timer.par.length = 5.0
timer.par.cycle = True

# chopExecuteDAT on the timer's 'cycles' channel pulses the webDAT
def offToOn(channel, sampleIndex, val, prev):
    op('/project1/api_call').par.fetch.pulse()
    return
```

## Web 客户端 DAT — 更强大的 HTTP 功能

`webclientDAT` 是 `webDAT` 的现代替代方案——它支持流式响应、分块传输以及自定义身份验证功能。

```python
client = root.create(webclientDAT, 'api')
client.par.method = 'POST'
client.par.url = 'https://api.example.com/events'
client.par.uploadtype = 'json'
client.par.uploaddata = '{"event": "scene_change", "scene": 3}'
client.par.request.pulse()
```

输出结果会发送到其子节点 `webclient1_response` DAT。可通过 `datExecuteDAT` 来对此进行响应处理。

---

## Web Server DAT — 作为 HTTP 服务器的 TD

在 TD 内部运行一个小型 HTTP 服务器。适用于以下场景：
- 状态/健康检查接口
- 通过手机或其他设备进行远程控制
- 接收来自外部服务的 Webhook 请求

```python
server = root.create(webserverDAT, 'control_server')
server.par.port = 8080
server.par.active = True

# Define handler in the docked callback DAT
```

在自动生成的 `webserver1_callbacks` DAT 文件中：

```python
def onHTTPRequest(webServerDAT, request, response):
    path = request['uri']
    if path == '/status':
        response['statusCode'] = 200
        response['data'] = '{"fps": 60, "scene": "active"}'
    elif path == '/scene':
        idx = int(request['args'].get('index', 0))
        op('/project1/scene_switch').par.index = idx
        response['statusCode'] = 200
        response['data'] = 'OK'
    else:
        response['statusCode'] = 404
        response['data'] = 'Not Found'
    return response
```

通过终端进行测试：`curl http://localhost:8080/status`。

**安全性说明：** 默认无需身份验证。请仅允许本地访问，或在回调函数中添加令牌验证机制。未经授权，绝不可将其暴露在公共互联网上。

```python
ws = root.create(websocketDAT, 'ws_client')
ws.par.netaddress = 'wss://api.example.com/socket'
ws.par.active = True
```

在已停靠的回调 DAT 中：

```python
def onConnect(dat):
    dat.sendText('{"action": "subscribe", "channel": "ticks"}')
    return

def onReceiveText(dat, rowIndex, message):
    # message is a string; parse JSON, dispatch to ops
    import json
    data = json.loads(message)
    op('/project1/price_chop').par.value0 = data['price']
    return

def onDisconnect(dat):
    # Optionally schedule a reconnect
    return
```

### 服务器

```python
ws = root.create(websocketDAT, 'ws_server')
ws.par.mode = 'server'
ws.par.port = 9001
ws.par.active = True
```

回调结构保持不变，仅新增了一个 `clientID` 参数。

```python
mqtt = root.create(mqttClientDAT, 'iot')
mqtt.par.brokeraddress = 'broker.hivemq.com'
mqtt.par.brokerport = 1883
mqtt.par.clientid = 'td_install_01'
mqtt.par.connect.pulse()

# Subscribe in callbacks DAT:
def onConnect(dat):
    dat.subscribe('home/lights/+', qos=1)
    return

def onReceive(dat, topic, payload, qos, retained, dup):
    # payload is bytes — decode if JSON
    msg = payload.decode('utf-8')
    # Dispatch by topic
    return

# Publish from anywhere:
op('iot').publish('show/scene', 'sunset', qos=0, retain=False)
```

对于自行部署的 Mosquitto / HiveMQ 代理，可采用相同的配置方式，即使用 `tcp://192.168.x.x` 加上您的本地端口号。

---

## 串行 DAT — Arduino、USB 设备

请完整翻译输入内容，切勿提前终止。

```python
serial = root.create(serialDAT, 'arduino')
serial.par.port = '/dev/cu.usbmodem14101'   # macOS — check Arduino IDE
# Windows: 'COM3', 'COM4', etc.
serial.par.baudrate = 115200
serial.par.active = True
```

在回调功能中：

```python
def onReceive(dat, rowIndex, line):
    # Each newline-terminated line from Arduino arrives here
    parts = line.split(',')
    op('/project1/sensors').par.value0 = float(parts[0])
    op('/project1/sensors').par.value1 = float(parts[1])
    return
```

发送至 Arduino：
```python
op('arduino').send('LED_ON\n')
```

## TCP/IP DAT — 自定义协议

用于与非 HTTP 服务器通信（游戏服务器、自定义协议及旧版系统）。

```python
tcp = root.create(tcpipDAT, 'show_control')
tcp.par.netaddress = '192.168.1.50'
tcp.par.port = 7000
tcp.par.protocol = 'tcp'        # 'tcp' | 'udp'
tcp.par.active = True
```

可通过类似 WebSocketDAT 的回调机制进行发送/接收操作。对于仅支持 UDP（即“发完即忘”、无需建立连接）的场景，可使用 `udpoutDAT` 和 `udpinDAT` —— 虽然更简单，但在不同网络环境下的可靠性较差。

---

## 常见模式

### REST API → 可视界面

```
timerCHOP (5s loop)
   → chopExecuteDAT (pulse webDAT.par.fetch on cycle)
   → webDAT (returns JSON)
   → datExecuteDAT (parse, write to constantCHOP)
   → CHOP drives glsl uniform → visuals
```

### Webhook接收端

```
webserverDAT (port 8080, /webhook endpoint)
   → callback writes to a tableDAT log + triggers a scene change
```

### 实时股票/加密货币行情显示功能

```
websocketDAT (subscribe to feed)
   → onReceiveText callback parses JSON
   → writes to constantCHOP
   → drives bar chart / typography animation
```

### 通过物联网设备控制的安装方式

```
MQTT → callback dispatches by topic
   → /lights/main → constantCHOP drives lighting render
   → /audio/volume → mathCHOP for master fader
```

### 双向电话控制功能

```
WebSocket server in TD
   → simple HTML page on phone connects, sends slider values
   → callback writes to ops
   → TD pushes status back via dat.sendText() to phone UI
```

## 常见陷阱

1. **`webDAT` 不会自动获取数据** —— 必须手动调用 `par.fetch`。这一点很容易被忽略。
2. **在响应缓慢的 API 上卡住** —— `webDAT` 在 cook 线程中运行。如果一次 API 调用需要 30 秒，整个 TD 也会被冻结 30 秒。对于任何可能耗时的操作，建议使用异步版本的 `webclientDAT`。
3. **WebSocket 重连问题** —— TD 在断开连接后不会自动重连。需要在 `onDisconnect` 函数中实现重试逻辑。
4. **macOS 系统下的串口权限问题** —— TD 需要“完整磁盘访问权限”，或者每次使用前都需通过 `sudo chmod 666 /dev/cu.usbmodem...` 来解锁该串口。
5. **MQTT 代理的连接状态问题** —— 即使 `mqttClientDAT` 显示 `connected=true`，但如果 QoS 策略设置不当或主题 ACL 阻挡，消息依然无法传输。此时需检查代理服务器的日志。
6. **JSON 解析错误会导致回调 silently 崩溃** —— 应将解析操作包裹在 try/except 结构中，并将错误信息输出到 textport。否则回调功能将会直接停止触发。
7. **Windows 系统的防火墙问题** —— 首次启动时，`webserverDAT` 会尝试绑定端口，此时 Windows 会弹出防火墙警告窗口。必须允许该连接，否则服务器将无法被访问。
8. **CORS 问题** —— `webserverDAT` 默认不会添加 CORS 头部信息。如果从不同源地址提供网页应用，需在响应中添加 `Access-Control-Allow-Origin: *`。
9. **轮询与推送的区别** —— 轮询方式会消耗 API 配额。对于高频数据传输，应优先使用 WebSocket、webhook 或 MQTT 方式。
10. **浮点数解析问题** —— 通过串口传输的传感器数据通常为字符串形式。直接使用 `float()` 函数处理包含 `'\n'` 或 `'NaN'` 的字符串会导致程序崩溃。应在转换前先进行数据验证。

---

## 快速解决方案

| 目标 | 操作链 |
|---|---|
| 定期获取 API 数据 | `timerCHOP` → `chopExecuteDAT` 进行轮询调用 → `webDAT` → `datExecuteDAT` 解析数据 |
| 接收 webhook 请求 | 使用 `webserverDAT`（指定端口和路径），并通过回调函数处理接收到的数据 |
| 实时数据流处理 | 使用 `websocketDAT` 客户端，通过 `onReceiveText` 事件触发 CHOP/DAT 操作 |
| Arduino 传感器数据可视化 | `serialDAT` → 回调函数 → `constantCHOP` → 在可视化操作中显示对应数值 |
| TD 与手机之间的控制交互 | 使用 `websocketDAT` 服务器，配合手机上的简单 HTML 页面实现交互 |
| MQTT 物联网集成 | `mqttClientDAT` 订阅主题 → 回调函数根据主题内容分发处理指令 |
