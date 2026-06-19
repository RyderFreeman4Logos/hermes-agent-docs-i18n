---
title: "Canvas — Canvas LMS integration — fetch enrolled courses and assignments using API token authentication"
sidebar_label: "Canvas"
description: "Canvas LMS integration — fetch enrolled courses and assignments using API token authentication"
---

{/* 本页面由 website/scripts/generate-skill-docs.py 根据技能对应的 SKILL.md 文件自动生成。请直接编辑源文件 SKILL.md，而非此页面。 */}

# Canvas

Canvas LMS 集成——通过 API 令牌认证获取已注册的课程与作业信息。

## 技能元数据

| | |
|---|---|
| 来源 | 可选——使用 `hermes skills install official/productivity/canvas` 命令安装 |
| 路径 | `optional-skills/productivity/canvas` |
| 版本 | `1.0.0` |
| 创建者 | 社区用户 |
| 许可协议 | MIT |
| 支持平台 | linux、macos、windows |
| 标签 | `Canvas`、`LMS`、`教育`、`课程`、`作业` |

## 参考：完整的 SKILL.md 文件

:::info
以下是当触发该技能时 Hermes 会加载的完整技能定义。技能处于激活状态时，智能体将依据此内容执行操作。
:::

# Canvas LMS —— 课程与作业查询功能

以只读方式访问 Canvas LMS，用于列出课程及作业信息。

## 脚本

- `scripts/canvas_api.py` —— 用于调用 Canvas API 的 Python 命令行工具

## 设置步骤

1. 在浏览器中登录您的 Canvas 实例
2. 进入 **账户 → 设置**（点击个人资料图标，然后选择设置）
3. 滚动到 **已批准集成**，点击 **+ 新建访问令牌**
4. 为该令牌命名（例如“Hermes Agent”），可选择设置过期时间，然后点击 **生成令牌**
5. 复制生成的令牌，并将其添加到 `${HERMES_HOME:-~/.hermes}/.env` 文件中：

```
CANVAS_API_TOKEN=your_token_here
CANVAS_BASE_URL=https://yourschool.instructure.com
```

基础网址即您登录 Canvas 后浏览器中显示的地址（不含末尾斜杠）。

## 使用方法

请翻译完整的输入内容，切勿提前终止。

```bash
CANVAS="python $HERMES_HOME/skills/productivity/canvas/scripts/canvas_api.py"

# List all active courses
$CANVAS list_courses --enrollment-state active

# List all courses (any state)
$CANVAS list_courses

# List assignments for a specific course
$CANVAS list_assignments 12345

# List assignments ordered by due date
$CANVAS list_assignments 12345 --order-by due_at
```

## 输出格式

**list_courses** 的返回值为：
```json
[{"id": 12345, "name": "Intro to CS", "course_code": "CS101", "workflow_state": "available", "start_at": "...", "end_at": "..."}]
```

**list_assignments** 的返回值为：
```json
[{"id": 67890, "name": "Homework 1", "due_at": "2025-02-15T23:59:00Z", "points_possible": 100, "submission_types": ["online_upload"], "html_url": "...", "description": "...", "course_id": 12345}]
```

注意：任务描述会被截断为500个字符以内。`html_url`字段可链接至Canvas中的完整任务页面。

## API参考（curl）

```bash
# List courses
curl -s -H "Authorization: Bearer $CANVAS_API_TOKEN" \
  "$CANVAS_BASE_URL/api/v1/courses?enrollment_state=active&per_page=10"

# List assignments for a course
curl -s -H "Authorization: Bearer $CANVAS_API_TOKEN" \
  "$CANVAS_BASE_URL/api/v1/courses/COURSE_ID/assignments?per_page=10&order_by=due_at"
```

Canvas 使用 `Link` 请求头来实现分页功能，该 Python 脚本会自动处理分页操作。

## 规则

- 该技能为**只读型**——仅用于获取数据，绝不会修改课程或作业内容
- 首次使用时，需通过运行 `$CANVAS list_courses` 命令来验证授权状态；如果返回 401 错误，请指导用户完成设置
- Canvas 的请求频率限制为每 10 分钟约 700 次请求；若达到限制，请查看 `X-Rate-Limit-Remaining` 请求头中的数值

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 401 Unauthorized 错误 | 令牌无效或已过期——请在 Canvas 设置中重新生成令牌 |
| 403 Forbidden 错误 | 令牌缺乏访问该课程的权限 |
| 课程列表为空 | 尝试使用 `--enrollment-state active` 参数，或省略该参数以查看所有状态下的课程 |
| 所属机构错误 | 请确认 `CANVAS_BASE_URL` 与浏览器中显示的地址一致 |
| 超时错误 | 请检查与 Canvas 服务器的网络连接状况 |
