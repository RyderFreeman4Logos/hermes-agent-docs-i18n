# 内置插件

只需将默认导出 `HermesPlugin` 的 `<name>/plugin.{ts,tsx}` 文件放入此处，即可在启动时自动注册（相关配置位于 `../contrib/plugins.ts` 中的 vite glob 规则），其功能清单及实时启用/禁用机制与运行时插件完全一致。

目前官方版本中并未内置任何插件——所有示例/演示插件（如计数器示例、gateway-pill 1:1 重建示例以及 runtime-loader 的“Hello World”示例）均存放在配套的 [`hermes-example-plugins`](https://github.com/NousResearch/hermes-example-plugins) 仓库中，从而避免官方应用文件过于臃肿。

由用户或智能体编写的插件则会在运行时从 `$HERMES_HOME/desktop-plugins/<name>/plugin.js` 文件加载——详情请参阅 `hermes-desktop-plugins` 技能文档。
