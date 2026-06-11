# Matrix交叉签名引导流程——端到端测试

该测试针对`gateway/platforms/matrix.py`中新增的自动引导功能，构建了一个独立的端到端测试方案。它会在Docker环境中启动一个真实的Continuuity homeserver，注册一个新机器人，然后使用经过修改的引导逻辑对该机器人进行测试，并验证以下要点：

1. 交叉签名密钥会以**未填充**的base64格式的keyid形式被发布（这正是本PR要修复的缺陷——在Element环境中，带有填充字符的keyid会被matrix-rust-sdk直接拒绝）。
2. 当使用相同的加密存储再次启动时，将跳过引导流程。
3. 若设置了`MATRIX_RECOVERY_KEY`环境变量，则会优先使用现有的恢复密钥机制，不会执行新的引导操作。

## 运行方式

```bash
# from repo root
docker compose -f tests/e2e/matrix_xsign_bootstrap/docker-compose.yml up -d
python tests/e2e/matrix_xsign_bootstrap/test_bootstrap.py
docker compose -f tests/e2e/matrix_xsign_bootstrap/docker-compose.yml down -v
```

`down -v` 步骤会移除持久卷，从而让下一次运行时获得一个全新的家庭服务器——这一点非常重要，因为 Continuuity 的一次性管理员注册令牌仅在创建第一个用户之前有效。

## 端口

默认情况下，`docker compose` 会将 Continuuity 绑定到 `127.0.0.1:26167` 端口。如果该端口在本地已被占用，可使用 `HOMESERVER_HOST_PORT=NNNNN docker compose up -d` 参数进行覆盖。

## 测试的内容

该测试直接引用了 `gateway/platforms/matrix.py` 文件中的引导代码片段（即“if MATRIX_RECOVERY_KEY else get_own_cross_signing_public_keys / generate_recovery_key”这段逻辑），因此无需导入整个 hermes gateway 及其众多依赖项即可运行。**如果实际代码与 `_connect_with_bootstrap` 中的内容有所不同，就必须更新此测试以保持一致。** 这也是为了在 CI 环境中无需使用完整的 hermes-agent 运行时而付出的小小代价。

## 何时跳过测试

- 未安装 `mautrix` Python 包
- 无法通过 `$E2E_MATRIX_HS`（默认为 `http://127.0.0.1:26167`）访问家庭服务器
