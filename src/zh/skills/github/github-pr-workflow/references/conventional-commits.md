# Conventional Commits 快速参考

格式：`类型(范围): 描述`

## 类型

| 类型 | 使用场景 | 示例 |
|------|----------|---------|
| `feat` | 新功能或新能力 | `feat(auth): 添加 OAuth2 登录流程` |
| `fix` | 错误修复 | `fix(api): 处理 /users 接口返回的空值响应` |
| `refactor` | 代码重构，无行为变化 | `refactor(db): 将查询构建器提取到独立模块中` |
| `docs` | 仅用于文档更新 | `docs: 更新 README 中的 API 使用示例` |
| `test` | 添加或更新测试用例 | `test(auth): 为令牌刷新功能添加集成测试` |
| `ci` | CI/CD 配置调整 | `ci: 在测试矩阵中加入 Python 3.12 版本` |
| `chore` | 维护工作、依赖管理及工具升级 | `chore: 将 pytest 升级到 8.x 版本` |
| `perf` | 性能优化 | `perf(search): 在 users.email 列上添加索引` |
| `style` | 格式调整、空白处理及分号规范 | `style: 对 src/ 目录运行 black 格式化工具` |
| `build` | 构建系统或外部依赖更新 | `build: 从 setuptools 更改为 hatch` |
| `revert` | 撤销之前的提交 | `revert: 撤销 “feat(auth): 添加 OAuth2 登录流程” 这次提交` |

## 范围（可选）

代码库中对应模块的简短标识符：`auth`、`api`、`db`、`ui`、`cli` 等。

## 影响较大的变更

可在类型后添加 `!` 标记，或在文档底部注明 `BREAKING CHANGE:`：

```
feat(api)!: change authentication to use bearer tokens

BREAKING CHANGE: API endpoints now require Bearer token instead of API key header.
Migration guide: https://docs.example.com/migrate-auth
```

## 多行内容格式

每行字符数需控制在72个以内。如需列出多项修改内容，可使用项目符号表示：

```
feat(auth): add JWT-based user authentication

- Add login/register endpoints with input validation
- Add User model with argon2 password hashing
- Add auth middleware for protected routes
- Add token refresh endpoint with rotation

Closes #42
```

## 关联问题

在提交内容或底部信息中：

```
Closes #42          ← closes the issue when merged
Fixes #42           ← same effect
Refs #42            ← references without closing
Co-authored-by: Name <email>
```

## 快速决策指南

- 添加了新功能？→ `feat`
- 发现错误并已修复？→ `fix`
- 调整了代码结构但功能未变？→ `refactor`
- 仅修改了测试相关内容？→ `test`
- 仅修改了文档？→ `docs`
- 更新了 CI/CD 流水线？→ `ci`
- 更新了依赖项或工具？→ `chore`
- 提高了运行效率？→ `perf`
