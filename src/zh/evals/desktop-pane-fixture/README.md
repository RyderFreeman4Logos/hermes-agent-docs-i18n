# 已保存面板 fixture 的导入延迟控制

在通过 `npm ci` 完成基础安装后，在 `apps/desktop` 目录下执行：

```sh
npx vitest run --config ../../evals/desktop-pane-fixture/vitest.config.mts --reporter verbose
npx vitest run --project ui src/store/session-pane-focus.test.ts --sequence.shuffle.tests --sequence.seed=12345 --reporter verbose
```

Vite插件会在真实面板树存储的评估过程中添加11秒的异步等待时间。它不会模拟面板函数，也不会在断言中检查源代码、缩短截止时间或修改两个测试主体。UI测试的截止时间仍为15秒，而默认钩子的截止时间则保持为10秒。这属于通过调度方式模拟导入延迟，并不意味着本地机器能够在无需辅助的情况下完全复现原始CI环境下的负载情况。该功能为可选启用，并非用于执行耗时的CI测试。

对于A/B测试，需将此评估目录应用到父版本上并运行相同命令，随后再在修复后的版本上进行测试。“Base”模式会在每个`beforeEach`函数中分别评估相关内容，而“Fixed”模式则仅在测试收集阶段进行一次评估。在“Base”模式下会显示两次延迟标记，而在“Fixed”模式下仅显示一次。预期结果是：“Base”模式会因“钩子在10000毫秒内超时”而失败；而“Fixed”模式则能成功通过所有行为断言。

基于初始版本`fb3446a281e`的测试数据如下：

| 对照组 | 测试结果 |
| --- | --- |
| Base模式 + 评估延迟 | 2次钩子超时，测试阶段耗时20.04秒 |
| Fixed模式 + 相同延迟 | 2项测试通过，测试阶段耗时5毫秒；导入阶段耗时11.84秒 |
| Fixed模式，测试顺序正常及反向（种子值12345） | 两种顺序下均有2项测试通过 |
| 使用存储目录，8个工作进程 | 共123个文件，1491项测试全部通过 |
| 完整的UI项目，8个工作进程 | 共753个文件，7355项断言全部通过，但`statusbar-visibility.test.tsx`文件中由于Radix焦点范围计时器的错误事件，导致测试以状态码1退出 |

突变控制措施则是分别应用于`session-states.ts`文件，之后再恢复原状。

- 在 `focusOpenSession` 函数中移除 `revealTreePane(paneId)`：此时叠加层重用场景会失败（返回值为 `null` 而非 `canonical-chat`），而未命中场景则可以正常通过。  
- 使 `focusWorkspaceOwnerSessionTile` 函数无论 `focusOpenSession` 的执行结果如何，始终返回存储的 ID：此时未命中场景会失败（返回值为 `canonical-chat` 而非 `null`），而叠加层场景则可以正常通过。  

该测试用例使用了真实的注册表、树结构监控器、面板镜像工具、叠加层功能、磁贴存储系统以及焦点控制功能。在每个独立的 Vitest 文件组中只需安装一次应用生命周期监控器。通过真实操作丢弃相关磁贴，即可同时清除响应式数据源及其内存中的持久化存储；并在每个测试用例之间重置布局、焦点状态、预设设置、选中内容、读取基准值以及 localStorage 数据。镜像工具会监测到该丢弃操作，并自动取消自身的贡献。没有任何生产环境 API 需要专门的测试用重置或清理功能。  

如果主机已用尽 inotify 监控资源，可在命令前添加 `CHOKIDAR_USEPOLLING=true` 参数；此操作仅会改变文件监控方式，而不会影响测试的截止时间。记录存储/完整套件功能以及最终焦点控制功能均采用了该解决方案。
