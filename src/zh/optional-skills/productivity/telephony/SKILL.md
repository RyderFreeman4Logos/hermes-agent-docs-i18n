---
name: telephony
description: Give Hermes phone capabilities without core tool changes. Provision and persist a Twilio number, send and receive SMS/MMS, make direct calls, and place AI-driven outbound calls through Bland.ai or Vapi.
version: 1.0.0
author: Nous Research
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [telephony, phone, sms, mms, voice, twilio, bland.ai, vapi, calling, texting]
    related_skills: [maps, google-workspace, agentmail]
    category: productivity
---

# 电话功能——无需修改核心工具即可实现号码、通话与短信功能

这项可选技能为Hermes带来了实用的电话功能，同时不会将电话相关功能纳入核心工具列表中。

它附带了一个辅助脚本 `scripts/telephony.py`，可用于：
- 将服务提供商的凭证保存到 `${HERMES_HOME:-~/.hermes}/.env` 中
- 搜索并购买Twilio电话号码
- 记住该号码以便后续会话使用
- 从该号码发送短信/MMS
- 无需Webhook服务器即可轮询该号码的 incoming短信
- 使用TwiML的 `<Say>` 或 `<Play>` 标签直接发起Twilio通话
- 将已拥有的Twilio号码导入Vapi
- 通过Bland.ai或Vapi发起外呼AI通话

## 解决的问题

该技能旨在覆盖用户实际需要的各类电话功能：
- 外拨通话
- 发送短信
- 拥有一个可重复使用的智能体号码
- 查看稍后发送到该号码的消息
- 在不同会话之间保留该号码及相关标识符
- 为将来接收incoming短信及实现其他自动化功能提供完善的电话身份管理

需要注意的是，它并不会将Hermes转变为真正的实时incoming电话网关。Incoming短信是通过轮询Twilio REST API来处理的，对于许多工作流而言已经足够，比如发送通知或获取一次性验证码，且无需额外搭建Webhook基础设施。

## 安全规则——必须遵守

1. 在拨打电话或发送短信之前务必先进行确认。
2. 绝对不要拨打紧急电话号码。
3. 禁止利用电话功能进行骚扰、垃圾信息发送、身份冒充或任何非法行为。
4. 应将第三方电话号码视为敏感的操作数据：
   - 不要将其保存在Hermes的内存中
   - 除非用户明确要求，否则不要在技能文档、总结或后续记录中提及这些号码
5. 可以保留**智能体拥有的Twilio号码**，因为这是用户配置的一部分。
6. VoIP号码**不一定**适用于所有第三方2FA流程。请谨慎使用，并向用户明确说明相关限制。

## 决策树——选择哪种服务？

建议使用以下逻辑而非硬编码的服务提供商路由方式来做出选择：

### 1) “我希望Hermes拥有一个真实的电话号码”
选择**Twilio**。

原因：
- 购买并保留号码的流程最为简单
- SMS/MMS支持最为完善
- Incoming短信轮询的实现方式最简单
- 为将来接入Webhook或处理来电提供了最清晰的扩展路径

适用场景：
- 后续接收短信
- 发送部署警报或定时通知
- 为智能体维护一个可重复使用的电话身份
- 日后尝试基于电话的认证流程

### 2) “我现在只需要最简单的AI外呼功能”
选择**Bland.ai**。

原因：
- 设置速度最快
- 只需要一个API密钥
- 无需自行购买或导入号码

缺点：
- 灵活性较低
- 语音质量尚可，但并非最佳

### 3) “我需要最佳的对话式AI语音质量”
选择**Twilio + Vapi**组合。

原因：
- Twilio可提供用户拥有的号码
- Vapi则能带来更出色的对话式AI通话质量以及更多语音/模型选项

推荐流程：
1. 购买/保存一个Twilio号码
2. 将其导入Vapi
3. 保存返回的 `VAPI_PHONE_NUMBER_ID`
4. 使用 `ai-call --provider vapi` 发起通话

### 4) “我想使用自定义预录语音消息进行通话”
选择带有公共音频URL的**Twilio直接通话**功能。

原因：
- 播放自定义MP3文件最为简单
- 可与Hermes的 `text_to_speech` 功能结合使用，再通过公共文件托管服务或隧道传输音频

## 文件与持久化状态

该技能将电话相关状态保存在两个位置：

### `${HERMES_HOME:-~/.hermes}/.env`
用于存储长期有效的服务提供商凭证及已拥有号码的标识符，例如：
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_PHONE_NUMBER`
- `TWILIO_PHONE_NUMBER_SID`
- `BLAND_API_KEY`
- `VAPI_API_KEY`
- `VAPI_PHONE_NUMBER_ID`
- `PHONE_PROVIDER`（AI通话服务提供商：bland或vapi）

### `~/.hermes/telephony_state.json`
用于存储仅在当前技能会话中有效、但需在多次会话之间保留的状态信息，例如：
- 已记住的默认Twilio号码/SID
- 已记住的Vapi电话号码ID
- 用于轮询收件箱消息的上一条消息SID及日期

这样一来：
- 下次加载该技能时，`diagnose` 功能就能告知当前已配置的号码是什么
- `twilio-inbox --since-last --mark-seen` 命令可以从上一次的轮询点继续处理消息

## 查找辅助脚本

安装此技能后，可通过以下方式找到该脚本：

```bash
SCRIPT="$(find ~/.hermes/skills -path '*/telephony/scripts/telephony.py' -print -quit)"
```

如果 `SCRIPT` 的值为空，说明该技能尚未安装。

## 安装

这是一项官方提供的可选技能，因此请通过 Skills Hub 进行安装：

```bash
hermes skills search telephony
hermes skills install official/productivity/telephony
```

## 提供商配置

### Twilio — 自有号码、短信/MMS、直接通话、接收短信轮询

注册地址：
- https://www.twilio.com/try-twilio

随后将凭证保存至Hermes中：

```bash
python3 "$SCRIPT" save-twilio ACXXXXXXXXXXXXXXXXXXXXXXXXXXXX your_auth_token_here
```

搜索可用的号码：

```bash
python3 "$SCRIPT" twilio-search --country US --area-code 702 --limit 5
```

购买并记住一个号码：

```bash
python3 "$SCRIPT" twilio-buy "+17025551234" --save-env
```

列出已拥有的号码：

```bash
python3 "$SCRIPT" twilio-owned
```

稍后可将其中之一设置为默认值：

```bash
python3 "$SCRIPT" twilio-set-default "+17025551234" --save-env
# or
python3 "$SCRIPT" twilio-set-default PNXXXXXXXXXXXXXXXXXXXXXXXXXXXX --save-env
```

### Bland.ai — 最简单的智能外呼工具

注册地址：
- https://app.bland.ai

保存配置：

```bash
python3 "$SCRIPT" save-bland your_bland_api_key --voice mason
```

### Vapi — 更出色的对话语音质量

注册地址：
- https://dashboard.vapi.ai

请先保存 API 密钥：

```bash
python3 "$SCRIPT" save-vapi your_vapi_api_key
```

将您拥有的 Twilio 号码导入 Vapi，并保存返回的电话号码标识符：

```bash
python3 "$SCRIPT" vapi-import-twilio --save-env
```

如果您已经知道 Vapi 电话号码的 ID，可直接将其保存：

```bash
python3 "$SCRIPT" save-vapi your_vapi_api_key --phone-number-id vapi_phone_number_id_here
```

## 诊断当前状态

随时查看该智能体已掌握的信息：

```bash
python3 "$SCRIPT" diagnose
```

在后续会话中恢复工作时，请首先使用此方法。

## 常见工作流程

### A. 购买代理号码并持续使用

1. 保存 Twilio 凭证：
```bash
python3 "$SCRIPT" save-twilio AC... auth_token_here
```

2. 搜索号码：
```bash
python3 "$SCRIPT" twilio-search --country US --area-code 702 --limit 10
```

3. 购买后将其保存至 `${HERMES_HOME:-~/.hermes}/.env` 文件中，并设置状态：
```bash
python3 "$SCRIPT" twilio-buy "+17025551234" --save-env
```

4. 在下一次会话中，运行如下命令：
```bash
python3 "$SCRIPT" diagnose
```
此处显示了已保存的默认号码以及收件箱检查点状态。

### B. 从智能体号码发送短信

```bash
python3 "$SCRIPT" twilio-send-sms "+15551230000" "Your deployment completed successfully."
```

支持媒体文件：

```bash
python3 "$SCRIPT" twilio-send-sms "+15551230000" "Here is the chart." --media-url "https://example.com/chart.png"
```

### C. 无 Webhook 服务器时，后续手动查看接收到的短信

轮询默认的 Twilio 号码的收件箱以获取消息：

```bash
python3 "$SCRIPT" twilio-inbox --limit 20
```

仅显示在上一个检查点之后收到的消息，阅读完毕后即可将检查点向前推进：

```bash
python3 "$SCRIPT" twilio-inbox --since-last --mark-seen
```

这正是针对“如何在技能再次加载时获取该号码接收到的消息？”这一问题的核心解答。

### D. 使用内置文本转语音功能直接发起 Twilio 呼叫

```bash
python3 "$SCRIPT" twilio-call "+15551230000" --message "Hello! This is Hermes calling with your status update." --voice Polly.Joanna
```

### E. 使用预录或自定义语音消息发起通话

这是复用 Hermes 现有 `text_to_speech` 功能的主要途径。

适用于以下情况：
- 您希望通话使用 Hermes 配置好的文本转语音，而非 Twilio 的 `<Say>` 功能
- 您需要单向语音传达信息（如简报、提醒、笑话、通知或状态更新）
- 您不需要实时对话式电话通话

请先单独生成或托管音频文件，然后：

```bash
python3 "$SCRIPT" twilio-call "+155****0000" --audio-url "https://example.com/briefing.mp3"
```

推荐的 Hermes TTS -> Twilio Play 工作流程如下：

1. 使用 Hermes 的 `text_to_speech` 功能生成音频文件。
2. 将生成的 MP3 文件设置为可公开访问。
3. 通过 `--audio-url` 参数发起 Twilio 通话。

示例智能体处理流程：
- 使用 `text_to_speech` 请求 Hermes 生成语音消息。
- 如有需要，可通过临时静态主机、隧道或对象存储 URL 公开该文件。
- 使用 `twilio-call --audio-url ...` 将音频通过电话传输给对方。

适合存储 MP3 文件的方案包括：
- 临时的公共对象/存储 URL
- 连接到本地静态文件服务器的短生命周期隧道
- 电话服务提供商可直接获取的任何现有 HTTPS URL

重要提示：
- Hermes TTS 非常适用于预录的外呼消息。
- 对于**实时对话式 AI 通话**，Bland/Vapi 是更佳选择，因为它们能够自行处理实时的电话音频处理流程。
- 本方案并未将 Hermes 的 STT/TTS 功能作为完整的双工电话通话引擎使用；若要实现该功能，需要比当前方案更为复杂的流媒体/ webhook 集成。

### F. 使用 Twilio 直接通话功能导航电话树/IVR 系统

如果需要在通话建立后输入数字，可使用 `--send-digits` 参数。
Twilio 会将参数 `w` 解释为短暂等待。

```bash
python3 "$SCRIPT" twilio-call "+18005551234" --message "Connecting to billing now." --send-digits "ww1w2w3"
```

该功能有助于在将通话转接给人工客服或发送简短状态信息之前，先进入特定的菜单分支。 

### G. 使用 Bland.ai 进行外呼智能电话通话

```bash
python3 "$SCRIPT" ai-call "+15551230000" "Call the dental office, ask for a cleaning appointment on Tuesday afternoon, and if they do not have Tuesday availability, ask for Wednesday or Thursday instead." --provider bland --voice mason --max-duration 3
```

查看状态：

```bash
python3 "$SCRIPT" ai-status <call_id> --provider bland
```

完成后可提出与Bland分析相关的问题：

```bash
python3 "$SCRIPT" ai-status <call_id> --provider bland --analyze "Was the appointment confirmed?,What date and time?,Any special instructions?"
```

### H. 使用 Vapi 从您自己的号码发起 AI 外呼电话

1. 将您的 Twilio 号码导入 Vapi：
```bash
python3 "$SCRIPT" vapi-import-twilio --save-env
```

2. 发起通话：
```bash
python3 "$SCRIPT" ai-call "+15551230000" "You are calling to make a dinner reservation for two at 7:30 PM. If that is unavailable, ask for the nearest time between 6:30 and 8:30 PM." --provider vapi --max-duration 4
```

3. 查看结果：
```bash
python3 "$SCRIPT" ai-status <call_id> --provider vapi
```

## 推荐的智能体操作流程

当用户请求拨打电话或发送短信时：

1. 通过决策树确定适合该请求的处理路径。
2. 若配置状态不明确，则运行 `diagnose` 命令进行诊断。
3. 收集完整的任务详情。
4. 在拨打电话或发送短信前向用户确认。
5. 使用正确的命令执行操作。
6. 如有需要，可轮询查询操作结果。
7. 概要说明最终结果，同时避免将第三方号码存储在 Hermes 的内存中。

## 该技能目前尚不支持的功能

- 实时接听来电
- 基于 webhook 的实时短信推送至智能体处理流程
- 对任意第三方双重认证提供商的全面支持

这些功能需要比普通可选技能更复杂的基础设施。

## 常见问题与注意事项

- Twilio 的试用账户及地区限制可能会影响可拨打/发送短信的对象。
- 部分服务不允许使用 VoIP 号码进行双重认证。
- `twilio-inbox` 功能通过轮询 REST API 获取信息，而非即时推送。
- Vapi 的外呼功能仍依赖于已正确导入的有效号码。
- Bland.ai 提供的语音效果最为平实，但未必总是最佳音质。
- 请勿将任意第三方电话号码存储在 Hermes 的内存中。

## 验证清单

完成设置后，仅使用该技能即可实现以下所有功能：

1. 通过 `diagnose` 命令查看服务提供商的可用状态及已保存的配置信息。
2. 搜索并购买 Twilio 号码。
3. 将该号码保存至 `${HERMES_HOME:-~/.hermes}/.env` 文件中。
4. 使用该号码发送短信。
5. 后续轮询查询该号码接收的短信。
6. 直接拨打 Twilio 号码。
7. 通过 Bland.ai 或 Vapi 发起人工智能语音通话。

## 参考资料

- Twilio 号码相关文档：https://www.twilio.com/docs/phone-numbers/api
- Twilio 消息服务文档：https://www.twilio.com/docs/messaging/api/message-resource
- Twilio 语音服务文档：https://www.twilio.com/docs/voice/api/call-resource
- Vapi 文档：https://docs.vapi.ai/
- Bland.ai 网站：https://app.bland.ai/
