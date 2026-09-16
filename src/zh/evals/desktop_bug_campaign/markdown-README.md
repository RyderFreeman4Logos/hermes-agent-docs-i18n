# Markdown空白检测探针

该测试工具现在仅运行Markdown相关功能：不涉及producer.json、页面渲染、SystemMessage、后端服务、模型请求或通知发送等操作。独立的异步报告流程对应编号为#101078。旧版的综合生成器代码位于commit 07a4da338bc中，相关文件为navigation-markdown-{probe.tsx,live.mjs}；而markdown-producer.py文件则保持不变。

请从工作树根目录开始（该目录已安装锁定的工作空间依赖项）：

```sh
node evals/desktop_bug_campaign/navigation-vite.mjs
PLAYWRIGHT_BROWSERS_PATH=/home/teknium/.hermes/cache/desktop-bugs-74848ed3/navigation-markdown/browsers node evals/desktop_bug_campaign/navigation-markdown-live.mjs after
```

Vite需要占用端口18160（strictPort模式）；请确认HTML文件中引用了该工作树的探测条目。Chromium为无头模式，因此无需使用Xvfb或原生Electron环境。NAVIGATION_ARTIFACT_DIR用于覆盖默认的营销活动收据存储目录。

该测试框架共设置了30种测试场景：包括五种实际的代码导入函数，每种函数都涉及硬断点/软断点测试、首行缩进检查、带有终端空格的未闭合代码块、以空行结尾的已闭合代码块，以及代码开头和结尾的空行检测。测试会等待真实的Shiki解析器启动，读取代码的文本内容，点击代码卡片上的复制控件，进而查看实际浏览器中的剪贴板内容。对于代码格式的要求包括必须保留Markdown解析器生成的最终换行符；测试会原封不动地保存这些原始数据，而不会随意进行裁剪。若测试退出码非零，则表示断言失败或页面出现错误。此时仍会保留JSON格式的数据及截图。

单元测试的实现位于src/lib/markdown-whitespace.test.ts文件中，共包含两项测试用例。所有验证操作均需在campaign tests.lock文件的约束下执行。此测试属于生产环境组件级别的Chromium环境验证，而非针对原生Electron、后端传输层或macOS系统的验证。
