# 内置插件

只需将默认导出 `HermesPlugin` 的 `<name>/plugin.{ts,tsx}` 文件放入此处，即可在启动时自动注册（该文件位于 `../contrib/plugins.ts` 中的 vite 全局配置路径中），其管理方式与运行时插件相同，包括插件清单展示以及实时的启用/禁用功能。

请将真正发布的插件（以及用于测试 SDK 的小型辅助工具）保存在此目录下。那些直接复制核心组件以实现一次性演示的功能不应存放于此——这类文件会增加界面冗余，并造成“设置 ▸ 插件”菜单的混乱。此类内容请发布在配套的
[`hermes-example-plugins`](https://github.com/NousResearch/hermes-example-plugins)
仓库中。

由用户或智能体创建的插件则会在运行时从 `$HERMES_HOME/desktop-plugins/<name>/plugin.js`（即磁盘目录）加载——相关细节可参考 `hermes-desktop-plugins` 技能。
