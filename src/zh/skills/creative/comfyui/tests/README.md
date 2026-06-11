# ComfyUI 技能测试

用于检测技能相关脚本的 Pytest 测试套件。纯标准库单元测试无需任何前置配置即可运行；而云集成测试则需要 Comfy Cloud API 密钥。

## 运行方式

```bash
# Unit tests only (no network required) — runs in <1s
python3 -m pytest tests/ -c tests/pytest.ini -o addopts="-p no:xdist"

# Including cloud integration tests
COMFY_CLOUD_API_KEY="comfyui-..." python3 -m pytest tests/ \
  -c tests/pytest.ini -o addopts="-p no:xdist"

# Just cloud tests
COMFY_CLOUD_API_KEY="comfyui-..." python3 -m pytest tests/test_cloud_integration.py \
  -c tests/pytest.ini -o addopts="-p no:xdist" -v
```

`-c` 和 `-o` 参数可让该测试套件独立于任何父级的 `pyproject.toml` 中配置的 pytest 设置（例如父仓库中设置的 `-n auto` 参数）。

## 测试文件

| 文件名 | 覆盖范围 |
|--------|----------|
| `test_common.py` | 云检测、URL 路由、格式验证、嵌入向量处理、路径处理、种子值处理、模型列表解析、文件夹别名处理 |
| `test_extract_schema.py` | 连接追踪、正/负向提示词检测、去重逻辑、嵌入向量依赖项处理 |
| `test_run_workflow.py` | 参数注入（包括使用 `-1` 作为种子值、链接拒绝处理）、输出文件下载流程、运行器构建 |
| `test_check_deps.py` | 模型名称模糊匹配、安装命令建议生成 |
| `test_cloud_integration.py` | 实时云 API 接口测试（若无 API 密钥则自动跳过） |

## 添加测试用例

修改脚本时，请执行以下操作：

1. 若修改内容仅涉及逻辑层面（如云检测、数据解析等），请添加单元测试；
2. 若修改内容依赖于云 API 的功能表现，请添加云集成测试（需使用 `pytestmark = pytest.mark.cloud` 标记，这样在没有 API 密钥时该测试会自动跳过）；
3. 工作流相关的固定配置请放在 `conftest.py` 文件中（如 `sd15_workflow`、`flux_workflow`、`video_workflow`）。

## 为何需要明确指定 `-c` / `-o`？

父级 hermes-agent 仓库的 `pyproject.toml` 默认已启用 `pytest-xdist` 功能（对应参数 `-n auto`）。但由于该测试套件规模较小，使用并行测试反而会增加复杂性，且用户的环境中也未必安装了 pytest-xdist。通过使用 `-c tests/pytest.ini -o addopts="-p no:xdist"` 这一参数组合，即可确保无论父项目的配置如何，该测试套件都能以相同方式运行。
