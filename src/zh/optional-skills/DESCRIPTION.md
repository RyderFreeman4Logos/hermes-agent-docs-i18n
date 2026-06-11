# 可选技能

由 Nous Research 维护的官方技能，**默认不会被激活**。

这些技能虽已包含在 hermes-agent 代码库中，但在安装过程中不会被复制到 `~/.hermes/skills/` 目录中。可通过 Skills Hub 查找它们：

```bash
hermes skills browse               # browse all skills, official shown first
hermes skills browse --source official  # browse only official optional skills
hermes skills search <query>       # finds optional skills labeled "official"
hermes skills install <identifier> # copies to ~/.hermes/skills/ and activates
```

## 为何设为可选？

某些技能虽实用，但并非所有用户都必需：

- **特定领域的集成**——针对特定付费服务或专业工具的整合；
- **实验性功能**——潜力巨大，但目前尚未经过充分验证；
- **复杂依赖项**——需要复杂的配置流程（如 API 密钥、应用安装等）。

通过将其设为可选，我们能在保持默认技能集精简的同时，仍为有需求的用户提供经过精心筛选、经过测试的官方技能。
