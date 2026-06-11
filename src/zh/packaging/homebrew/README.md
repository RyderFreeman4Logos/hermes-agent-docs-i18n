Hermes Agent 的 Homebrew 打包说明

建议以 `packaging/homebrew/hermes-agent.rb` 作为 Tap 资源，或以 `homebrew-core` 作为基础模板。

关键设计决策：
- 稳定版本应基于每个 GitHub 发布版本所附带的、采用语义化版本号命名的 sdist 文件构建，而非基于 CalVer 标签对应的压缩包。
- `faster-whisper` 现已移至 `voice` 附加组件中，这样仅包含 wheel 格式依赖的模块就不会被纳入 Homebrew 基础公式中。
- 该封装脚本会导出 `HERMES_BUNDLED_SKILLS`、`HERMES_OPTIONAL_SKILLS` 以及 `HERMES_MANAGED=homebrew` 等参数，从而确保打包后的安装版本能保留运行时所需资源，并将升级操作交由 Homebrew 处理。

常规更新流程：
1. 更新公式中的 `url`、`version` 和 `sha256` 参数。
2. 使用 `brew update-python-resources --print-only hermes-agent` 命令刷新 Python 相关资源。
3. 保持 `ignore_packages: %w[certifi cryptography pydantic]` 的设置不变。
4. 执行 `brew audit --new --strict hermes-agent` 进行安全检查，并通过 `brew test hermes-agent` 验证功能正常性。
