# SDK 开发

对于已发布的 Box 应用程序，请参考本文档。若仅需执行一次性 Hermes 任务，则应使用 CLI 相关文档。

## 从应用程序入手

查看代码仓库中现有的 Box 客户端实现、`BOX_` 配置、令牌存储方式、Webhook 处理逻辑、重试策略以及代码风格规范。应在现有集成基础上进行扩展，而非毫无必要地混用 SDK 与原始 REST 接口。

## 选择身份认证方式

| 身份认证方式 | 适用场景 |
| --- | --- |
| OAuth | 每位最终用户均需自行连接其 Box 账户 |

OAuth 会遵循已登录用户的权限及应用授权范围。对于共享型或后台运行的应用程序，由授权该应用的 Box 账户决定其访问权限边界；只需将该账户邀请至应用程序所需的文件、文件夹或 Hubs 即可。

## 使用官方 SDK

- [Python SDK 生成工具](https://github.com/box/box-python-sdk-gen)
- [`box` npm 包](https://developer.box.com/guides/tooling/box-npm-package)
- [现有的 Node SDK 项目](https://github.com/box/box-node-sdk)
- [其他 Box SDK](https://developer.box.com/guides/tooling/sdks/)

请根据项目所使用的语言选择对应的 SDK。对于新的 JavaScript 或 TypeScript 应用程序，可使用项目现有的包管理器来安装统一的 `box` 包；若使用 npm，则执行以下命令：

```bash
npm install box
```

从指定的 SDK 子路径中导入其 Node SDK：

```typescript
import BoxSDK from "box/sdk";
```

该包还通过 `npx box` 提供了项目级专属的 Box CLI。在应用开发过程中如有需要，可选用该命令行工具，但切勿擅自替换已独立配置的 Hermes CLI 运行器或其认证环境。若项目当前已使用 `box-node-sdk`，则应在此基础上进行扩展，而非在没有充分理由的情况下直接迁移。对于 Python 或其他编程语言，也应安装其官方提供的 Box SDK，而非 npm 包。

请将 OAuth 令牌以及任何自定义的 Platform App 客户端密钥存储在项目允许使用的密钥管理机制中，而不可放入版本控制系统中。当自定义 Platform App 需要更多权限范围时，应采用**用户认证（OAuth 2.0）**方式，由目标 Box 用户授权，而不应为常规应用功能设置身份冒充机制。企业级特殊管理操作应与常规的 Hermes 运行时及应用身份机制分离，切勿提升应用日常使用的账户权限。

## OAuth 客户端

请直接使用生成的 SDK 所提供的 OAuth 功能，无需自行实现授权码交换或令牌刷新逻辑。在调用具体功能时，需遵循已安装 SDK 的现有 OAuth 方法名称及其对应语言的授权指南。在调用任何 SDK 方法之前，应先初始化 OAuth 客户端，将存储的令牌与授予这些令牌的 Box 用户关联起来，并在执行操作前验证该用户身份。切勿在未完成 OAuth 初始化及令牌刷新机制配置的情况下，直接将 SDK 的部分功能代码集成到应用中。

## 利用 Box AI 构建具备文档理解能力的应用

当应用程序需要处理 Box 文档时，建议优先使用 Box AI：它能够保留原有的 Box 权限，通过 Box 的受控 AI 集成来处理源文件，避免将源文件内容引入应用程序的外部模型上下文，同时无需下载所有文件即可实现大规模的文档处理：

- 生成问答内容及摘要；
- 为重复出现的字段或元数据模板提取结构化信息；
- 为可变字段提取数据；
- 基于单个 Box 文件生成文本内容。

在首次发起请求之前，需告知用户必须启用 Box AI，且该功能会消耗 AI 计算资源。当 Box AI 不可用时，不得擅自切换到外部处理方式，而应中立地提供用户明确选择的替代方案。同时，应将 Box AI 的响应视为可能属于敏感的应用程序数据。

## 构建基于 Box Hub 的知识体验

若需针对精心筛选的文档集合实现持续的问答功能，建议使用 Box Hub，而非在每次请求时上传超过 25 个文件。首先应探索现有的 Hub；创建 Hub、填充内容、启用其 AI 功能或调整协作设置都会影响共享资源，且需要获得产品的正式批准。Box Hubs 的接口端点使用 API 版本 `2025.0`。

请使用与项目语言相匹配的生成 SDK。不同 SDK 版本生成的函数名称可能有所差异，但请保持请求格式不变，并遵循已安装 SDK 当前的函数命名规范。

```python
from box_sdk_gen import AiItemAsk, AiItemAskTypeField, CreateAiAskMode

answer = client.ai.create_ai_ask(
    CreateAiAskMode.SINGLE_ITEM_QA,
    "What changed in the latest policy?",
    [AiItemAsk(id=hub_id, type=AiItemAskTypeField.HUBS)],
    include_citations=True,
)
```

```typescript
const answer = await client.ai.createAiAsk({
  mode: "single_item_qa",
  prompt: "What changed in the latest policy?",
  items: [{ id: hubId, type: "hubs" }],
  includeCitations: true,
});
```

查询 Hub 时会利用其已索引的内容，且仅返回当前操作主体有权访问的文件中的信息。新添加的 Hub 内容可能需要几分钟，有时甚至长达一小时才能完成索引；系统会显示可重试的索引状态，而不会将过早返回的结果视为最终结果。免费开发者计划包含了用于构建和测试的 Hubs 以及 Box AI API，并提供一定的每月 AI 单位额度。实际可用性则取决于组织的套餐选择及配置设置。在所有环境中，都需确认 Hub 存在、已启用 AI 功能，且是在 Hub AI 功能开启之后创建的，这样才能确保其内容能够被索引。如需了解 CLI 及操作流程，请参阅 [Box Hubs](hubs.md) 文档。

## Webhook 与可靠性

请务必验证 webhook 签名，妥善保存幂等性键，在事件发生后再获取权威状态，并明确设定重试/退避策略。在提升处理效率之前，应限制并发 API 调用次数，并确保重试操作的安全性。更多相关内容请参见 [Webhook 与事件](webhooks-and-events.md) 文档。
