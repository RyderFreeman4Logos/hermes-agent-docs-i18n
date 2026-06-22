# 看板设置 — 项目初始化与配置

在需求确定且团队架构搭建完成后，下一步便是生成实际的 `setup.sh` 脚本。该脚本用于创建项目工作空间、配置 Hermes 配置文件，并启动初始看板任务。

本文档将阐述相关的实现模式。配套脚本 `scripts/bootstrap_pipeline.py` 可以根据结构化的 JSON 输入自动完成大部分操作。

> **致谢：** 单项目工作空间布局、配置文件补丁修改方法、每个配置文件对应的 SOUL.md 文件规范，以及 `--workspace dir:<path>` 参数规则，均借鉴自 alt-glitch 的原始多智能体视频处理流程：
> [NousResearch/kanban-video-pipeline](https://github.com/NousResearch/kanban-video-pipeline)。
> 本技能将这些模式推广到了各种视频处理场景，并用基于 PyYAML 的配置补丁工具替换了原有的字符串替换式补丁工具。

## 项目工作空间结构

每个视频项目都会在 `~/projects/video-pipeline/<slug>/` 目录下拥有一个对应的工作空间：

```
~/projects/video-pipeline/<slug>/
├── brief.md                       ← the contract; all tasks reference
├── TEAM.md                        ← team composition + task graph (director reads this)
├── taste/
│   ├── brand-guide.md             ← color, typography, motion rules
│   ├── emotional-dna.md           ← what the piece should FEEL like
│   └── style-frames/              ← optional: visual references
├── audio/
│   ├── track.mp3                  ← provided music (if any)
│   ├── voiceover/                 ← per-line TTS clips
│   └── sfx/                       ← sound effects
├── assets/
│   ├── logos/
│   ├── fonts/
│   └── existing-footage/          ← reusable provided clips
├── scenes/
│   ├── scene-01/
│   │   ├── VISUAL_SPEC.md         ← cinematographer's per-scene spec
│   │   ├── render.py              ← renderer's code (or sketch.html, etc.)
│   │   ├── checkpoints/           ← preview frames for QA
│   │   └── clip.mp4               ← the deliverable for this scene
│   ├── scene-02/...
│   └── ...
├── checkpoints/                   ← global review frames
├── tools/                         ← optional project-local helpers
└── output/
    ├── final.mp4                  ← stitched + audio
    ├── final-noaudio.mp4
    ├── final-9x16.mp4             ← optional: vertical alternate
    └── captions.srt               ← optional: subtitle file
```

**slug** 是由简短标题转换而来：全部转为小写，再用连字符分隔。
示例：`q3-product-teaser`、`ascii-mood-loop`、`interview-cut-2026-q1`。

## setup.sh 脚本

该设置脚本会按顺序执行以下六项操作：

1. **创建工作区目录结构** — 即上述所有目录
2. **创建配置文件** — 使用命令 `hermes profile create <name> --clone`
3. **配置各配置文件** — 修改每个配置文件中的
   `~/.hermes/profiles/<name>/config.yaml`，设置工具集、始终加载的技能以及 `cwd` 参数
4. **为每个配置文件生成 SOUL.md 文件** — 包含角色设定与性格描述
5. **复制所提供的所有资源，并编写 `brief.md`、`TEAM.md` 以及 `taste/` 目录下的文件**
6. **创建初始看板任务** — 使用命令 `hermes kanban create`，并将该任务分配给项目负责人

模板结构可参考 `assets/setup.sh.tmpl` 文件。

### 配置文件创建模式

```bash
hermes profile create director --clone 2>/dev/null || true
```

`--clone` 参数用于从当前激活的配置文件进行克隆（同时保留模型及基础配置）。而 `|| true` 选项则能使脚本具备幂等性——即便该配置文件已存在，重新运行也不会出现错误。

### 配置文件补丁修改

每个配置文件在 `~/.hermes/profiles/<名称>/config.yaml` 目录下都存有一份 YAML 格式的配置。设置脚本仅会修改两个关键字段：

1. `toolsets:` — 用该角色所需的工具集替换默认值；
2. `skills.always_load:` — 列出该角色必须加载的技能（该列表可为空）。

**切勿**修改 `approvals.mode`（该参数用于控制用户对工具调用的确认流程，属于安全设置，必须保持用户原有的配置）。同样**切勿**修改 `terminal.cwd`——看板调度器会通过 `--workspace dir:<路径>` 参数为每个任务指定独立的当前工作目录，因此配置文件中的当前工作目录对看板操作并无影响，修改它反而可能破坏用户对该配置文件的交互式使用。

建议使用 **PyYAML** 库而非字符串替换方式来进行修改，这样才能有效避免因默认配置结构变化而导致的异常问题。

```bash
configure_profile() {
    local profile="$1"
    local toolsets_json="$2"     # JSON array, e.g. '["kanban","terminal","file"]'
    local skills_json="$3"       # JSON array, e.g. '["ascii-video"]'
    python3 - "$profile" "$toolsets_json" "$skills_json" <<'PY'
import json, os, sys, yaml
profile, ts_json, sk_json = sys.argv[1:4]
p = os.path.expanduser(f"~/.hermes/profiles/{profile}/config.yaml")
with open(p) as f:
    cfg = yaml.safe_load(f) or {}
cfg["toolsets"] = json.loads(ts_json)
cfg.setdefault("skills", {})["always_load"] = json.loads(sk_json)
with open(p, "w") as f:
    yaml.safe_dump(cfg, f, sort_keys=False)
PY
}
```

用户端的 Python 环境中必须已安装 PyYAML（大多数 Hermes 安装版本均已预装该库）。若未安装，请执行 `pip install pyyaml`。

设置脚本还应通过重新读取文件并进行比对来**验证**补丁内容——具体验证规则可参考 `assets/setup.sh.tmpl` 文件。

### 每个角色的 SOUL.md 文件

每个角色都会在 `~/.hermes/profiles/<name>/SOUL.md` 目录下拥有一个对应的 `SOUL.md` 文件，用于定义该角色的职责、语气及工作规则。模板文件位于 `assets/soul.md.tmpl`，可根据不同角色和项目的需求进行定制。

其中，负责整体统筹的角色的 SOUL.md 应包含最明确的指导原则——其设定的语气将影响整个项目的运作风格。**该角色 SOUL.md 中的关键内容包括：**

- **防懈怠规则**：“切勿亲自执行任务。对于每一项具体工作，都应创建一个看板任务并分配给他人处理。通过分解任务、转派处理、添加备注及审批等步骤来完成工作。”（看板任务管理的相关指导会自动注入到每个看板处理工具的系统提示词中，无需额外加载任何技能。）
- **任务分解步骤**：请阅读 `brief.md`、`TEAM.md` 以及 `taste/` 目录下的相关文件，利用 `TEAM.md` 中提供的团队结构图来进一步拆分任务。
- **workspace_path 规则**（详见下文）。

其他角色的 SOUL.md 文件内容相对简短，主要侧重于说明基本信息：角色身份、需要阅读的资料、需输出的内容、应使用的技能/工具以及输出文件的存放位置。由于看板任务管理的相关指导会自动注入到每个看板处理工具的系统提示词中，因此这些角色无需额外加载任何看板相关技能。

### 初始看板任务

`setup.sh` 脚本的最终操作就是启动看板系统：

```bash
hermes kanban create "Direct production of <video title>" \
    --assignee director \
    --workspace dir:"$HOME/projects/video-pipeline/${PROJECT_SLUG}" \
    --tenant ${PROJECT_SLUG} \
    --priority 2 \
    --max-runtime 4h \
    --body "$(cat <<EOF
Read brief.md, TEAM.md, and taste/.
Decompose into the team graph defined in TEAM.md.
All child tasks MUST use:
  workspace_kind="dir"
  workspace_path="$HOME/projects/video-pipeline/${PROJECT_SLUG}"
  tenant="${PROJECT_SLUG}"
EOF
)"
```

`--workspace dir:<path>` 参数至关重要——它告知看板所有子任务都共享同一个工作空间。若省略该参数或使用 `worktree`，则会将不同配置的进程隔离，从而导致资源无法共享。

## TEAM.md 文件

除了 `brief.md` 之外，还需编写一份供项目负责人查阅的 `TEAM.md` 文件。该文件应详细说明团队构成以及协调者需遵循的任务流程图，从而消除模糊之处，避免项目负责人自行添加不必要的步骤。

（以包含音乐监制和剪辑师的 ASCII 视频为例）其文件结构如下：

```markdown
# Team & Task Graph — <video title>

## Team

- `director` (this profile) — vision, decomposition, approval
- `cinematographer` — visual spec, quality review (loads `ascii-video`)
- `renderer-ascii` — ASCII scenes (loads `ascii-video`)
- `music-supervisor` — track analysis (loads `songsee`)
- `voice-talent` — narration (uses ElevenLabs API)
- `audio-mixer` — final mix (ffmpeg)
- `editor` — assembly (ffmpeg)
- `reviewer` — final QA gate

## Task Graph

T0: this task — decompose
 │
 ├── T1: cinematographer  "Design visual language"            (parent: T0)
 │    │
 │    ├── T2a: renderer-ascii   "Scene 1 — title card"        (parent: T1)
 │    ├── T2b: renderer-ascii   "Scene 2 — main beat"         (parent: T1)
 │    ├── T2c: renderer-ascii   "Scene 3 — outro"             (parent: T1)
 │
 ├── T3: music-supervisor "Analyze track + emit beats.json"   (parent: T0)
 │
 ├── T4: voice-talent     "Generate narration"                (parent: T0)
 │
 ├── T5: audio-mixer      "Mix VO + bg music"                 (parents: T3, T4)
 │
 ├── T6: editor           "Assemble cut + mux audio"          (parents: T2*, T5)
 │
 └── T7: reviewer         "Final QA"                          (parent: T6)
```

调度器会将此操作转换为实际的 `kanban_create` 调用。

## API密钥前提条件检查

在触发看板操作之前，请先确认所需的密钥已存在。需同时检查Hermes的`.env`文件（路径为`${HERMES_HOME:-$

```bash
check_key() {
    local var="$1"
    local kc_account="$2"
    local kc_service="$3"
    local _hermes_env="${HERMES_HOME:-$HOME/.hermes}/.env"
    if grep -q "^${var}=" "$_hermes_env" 2>/dev/null && \
       [ -n "$(grep "^${var}=" "$_hermes_env" | cut -d= -f2-)" ]; then
        return 0
    fi
    if command -v security >/dev/null 2>&1 && \
       security find-generic-password -a "${kc_account}" -s "${kc_service}" -w >/dev/null 2>&1; then
        return 0
    fi
    echo "ERROR: ${var} not set in ${_hermes_env} or Keychain (${kc_account}/${kc_service})"
    return 1
}

check_key ELEVENLABS_API_KEY hermes ELEVENLABS_API_KEY || exit 1
check_key OPENROUTER_API_KEY hermes OPENROUTER_API_KEY || exit 1
# ...
```

如果缺少某个必要键，脚本会立即终止并给出明确提示，而不会触发任务卡板，从而避免在执行过程中出现凭证错误。

## 关键规则

1. 每次执行 `kanban_create` 操作时，必须同时设置 **`workspace_kind="dir"`** 和 **`workspace_path="<绝对路径>"`**。否则，各工作流配置将无法共享相关资源。

2. 为每个任务指定租户。使用 `--tenant <项目标识>` 可以限制仪表板的范围，防止与其他正在进行的任务卡板产生相互干扰。

3. 使用幂等性键。对于那些重复执行时不应出现重复结果的任务（例如用于创建工作流配置的任务），应使用 `idempotency_key` 参数，或先检查该键是否已存在。

4. 每个任务都需设置 **`max_runtime_seconds`** 时间限制。如果渲染任务陷入停滞，会占用大量计算资源。默认时间值如下：
   - 渲染任务：1800秒（30分钟）
   - 编辑任务：600秒（10分钟）
   - 语音合成任务：300秒（5分钟）
   - 图像生成任务：600秒（10分钟）
   - 图像转视频生成任务：900秒（15分钟）

5. 对于耗时超过5分钟的任务，需定期发送包含进度信息的 **`kanban_heartbeat`** 消息。渲染工具应报告帧数，而编辑工具则应汇报组装进度。

6. 在触发任务卡板之前，必须先准备好 **`audio/`** 和 **`taste/`** 目录中的内容。切勿让任务执行流程去动态获取这些文件，应在初始化阶段就完成复制操作。

7. 初始化完成后，**`brief.md`** 文件将变为只读状态。如果在任务执行过程中需求文档发生变更，这属于重大调整，应重新触发任务卡板而非直接在线编辑。
