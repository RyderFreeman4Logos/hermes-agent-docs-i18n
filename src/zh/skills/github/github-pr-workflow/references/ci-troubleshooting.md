# CI故障排查快速参考指南

常见的CI运行失败模式及如何通过日志进行诊断。

## 阅读CI日志

```bash
# With gh
gh run view <RUN_ID> --log-failed

# With curl — download and extract
curl -sL -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$GH_OWNER/$GH_REPO/actions/runs/<RUN_ID>/logs \
  -o /tmp/ci-logs.zip && unzip -o /tmp/ci-logs.zip -d /tmp/ci-logs
```

## 常见故障模式

### 测试失败

**日志中的特征信息：**
```
FAILED tests/test_foo.py::test_bar - AssertionError
E       assert 42 == 43
ERROR tests/test_foo.py - ModuleNotFoundError
```

**故障诊断：**
1. 从错误堆栈中找出测试文件及具体行号。
2. 使用 `read_file` 功能读取出问题的测试用例。
3. 判断问题是代码中的逻辑错误，还是过时的测试断言。
4. 检查是否出现 `ModuleNotFoundError` —— 通常是由于 CI 环境中缺少依赖项所致。

**常见解决方案：**
- 更新断言内容，使其符合新的预期行为。
- 在 `requirements.txt` 或 `pyproject.toml` 中添加缺失的依赖项。
- 修复偶发性故障测试（添加重试机制、模拟外部服务、解决竞态条件问题）。

---

### 代码风格/格式检查失败

**日志中的签名信息：**
```
src/auth.py:45:1: E302 expected 2 blank lines, got 1
src/models.py:12:80: E501 line too long (95 > 88 characters)
error: would reformat src/utils.py
```

**诊断步骤：**
1. 查看相关文件及具体的行号信息。
2. 确定是哪种代码检查工具发出了警告（flake8、ruff、black、isort、mypy）。

**常见解决方案：**
- 在本地运行格式化工具：`black .`、`isort .`、`ruff check --fix .`
- 通过编辑文件来修正具体的样式违规问题。
- 若使用 `patch` 方式，务必确保缩进风格与现有代码保持一致。

---

### 类型检查失败（mypy / pyright）

**日志中的错误信息格式：**
```
src/api.py:23: error: Argument 1 to "process" has incompatible type "str"; expected "int"
src/models.py:45: error: Missing return statement
```

**诊断步骤：**
1. 读取指定行对应的文件内容
2. 检查函数签名以及传入的参数

**常见解决方案：**
- 添加类型转换操作
- 修正函数签名
- 作为最后手段添加 `# type: ignore` 注释（并附上说明）

---

### 构建/编译失败问题

**日志中的函数签名信息：**
```
ModuleNotFoundError: No module named 'some_package'
ERROR: Could not find a version that satisfies the requirement foo==1.2.3
npm ERR! Could not resolve dependency
```

**诊断步骤：**
1. 检查 requirements.txt / package.json 文件中是否存在缺失或不兼容的依赖项。
2. 对比本地环境与 CI 环境中的 Python/Node 版本。

**常见解决方案：**
- 将缺失的依赖项添加到需求文件中。
- 指定兼容的版本号。
- 更新锁定文件（使用 `pip freeze`、`npm install` 命令）。 

---

### 权限/认证失败问题

**日志中的签名信息：**
```
fatal: could not read Username for 'https://github.com': No such device or address
Error: Resource not accessible by integration
403 Forbidden
```

**诊断步骤：**
1. 检查工作流是否需要特殊权限（令牌作用域）。
2. 检查密钥配置是否完整（缺少 `GITHUB_TOKEN` 或自定义密钥）。

**常见解决方案：**
- 在工作流的 YAML 文件中添加 `permissions:` 块。
- 验证密钥是否存在：使用 `gh secret list` 命令或查看仓库设置。
- 对于 Fork 的 Pull Request，部分密钥按设计无法被访问。

---

### 超时故障

**日志中的相关提示：**
```
Error: The operation was canceled.
The job running on runner ... has exceeded the maximum execution time
```

**诊断步骤：**
1. 检查是哪个步骤出现了超时。
2. 查找是否存在无限循环、进程挂起或网络调用过慢的问题。

**常见解决方案：**
- 为特定步骤设置超时时间：`timeout-minutes: 10`
- 解决根本性的性能问题
- 将任务拆分为并行处理

---

### Docker / 容器故障

**日志中的特征标识：**
```
docker: Error response from daemon
failed to solve: ... not found
COPY failed: file not found in build context
```

**诊断步骤：**
1. 检查 Dockerfile 中出错的步骤
2. 确认代码仓库中存在被引用的文件

**常见解决方案：**
- 修正 COPY/ADD 命令中的路径
- 更新基础镜像的版本标签
- 将缺失的文件添加到 `.dockerignore` 文件的排除列表中，或从该列表中移除

---

## 自动修复决策树

```
CI Failed
├── Test failure
│   ├── Assertion mismatch → update test or fix logic
│   └── Import/module error → add dependency
├── Lint failure → run formatter, fix style
├── Type error → fix types
├── Build failure
│   ├── Missing dep → add to requirements
│   └── Version conflict → update pins
├── Permission error → update workflow permissions (needs user)
└── Timeout → investigate perf (may need user input)
```

## 修复后的重新运行

```bash
git add <fixed_files> && git commit -m "fix: resolve CI failure" && git push

# Then monitor
gh pr checks --watch 2>/dev/null || \
  echo "Poll with: curl -s -H 'Authorization: token ...' https://api.github.com/repos/.../commits/$(git rev-parse HEAD)/status"
```
