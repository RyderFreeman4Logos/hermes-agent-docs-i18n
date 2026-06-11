# 调查模板

针对常见供应链攻击场景预置的假设与调查模板。
每个模板均包含：攻击模式、需收集的关键证据以及假设构建思路。

---

## 模板 1：维护者账户被盗用

**攻击模式**：攻击者通过钓鱼或凭证填充等手段获取合法维护者账户的访问权限，进而利用该账户推送恶意代码、创建带后门的版本，或窃取持续集成系统中的机密信息。

**真实案例**：XZ Utils（2024年）、Codecov（2021年）、event-stream（2018年）

**需收集的关键证据**：
- [ ] 维护者账户在非正常工作时间或时区外进行的推送操作
- [ ] 添加新依赖项、混淆代码或修改构建脚本的提交记录
- [ ] 在可疑推送后立即创建版本（旨在最大化软件包的传播范围）
- [ ] MemberEvent中出现的未知协作者信息（攻击者为自身获取备用访问权限）
- [ ] WorkflowRunEvent中存在异常的机密信息访问行为或类似数据窃取的特征
- [ ] 账户登录地点发生变更（可通过社交媒体、会议演讲等内容进行印证）

**假设构建思路**：
```
[HYPOTHESIS] Actor <HANDLE>'s account was compromised on or around <DATE>, 
based on anomalous commit timing [EV-XXXX] and geographic access patterns [EV-YYYY].
```
```
[HYPOTHESIS] Release <VERSION> was published by the compromised account to push 
malicious code to downstream users, evidenced by the malicious commit [EV-XXXX] 
being added <N> hours before the release [EV-YYYY].
```

## 模板2：恶意依赖注入

**攻击模式**：篡改受信任的包，使其在依赖项中包含恶意代码；或向现有包注入新的恶意依赖项。

**需收集的关键证据**：
- [ ] 可疑提交前后 `package.json`/`requirements.txt`/`go.mod` 的差异对比
- [ ] 新依赖项的发布时间与注入操作的提交时间
- [ ] 该新依赖项是否存在于 npm/PyPI 上，以及其所有者是谁
- [ ] 注入的依赖项代码中是否存在任何混淆处理手段
- [ ] 安装时会在安装过程中执行代码的脚本（如 `postinstall`、`setup.py` 等）

**假设生成思路**：
```
[HYPOTHESIS] Commit <SHA> [EV-XXXX] introduced dependency <PACKAGE@VERSION> 
which appears to be a malicious package published by actor <HANDLE> [EV-YYYY], 
designed to execute <BEHAVIOR> during installation.
```

## 模板 3：CI/CD 流水线注入攻击

**攻击模式**：攻击者篡改 GitHub Actions 工作流，以此窃取机密信息、外传代码，或向构建输出中注入恶意文件。

**需收集的关键证据**：
- [ ] 怀疑时间段前后所有 `.github/workflows/*.yml` 文件的差异对比
- [ ] 被篡改的工作流所触发的 WorkflowRunEvents 事件
- [ ] 工作流步骤中新增的任何 `curl`、`wget` 或网络请求
- [ ] 新增或被修改的、引用 `secrets.*` 的 `env:` 部分
- [ ] 被篡改的工作流运行所生成的文件

**假设生成提示**：
```
[HYPOTHESIS] Workflow file <FILE> was modified in commit <SHA> [EV-XXXX] to 
exfiltrate repository secrets via <METHOD>, as evidenced by the added network 
call pattern [EV-YYYY].
```

## 模板 4：域名混淆/依赖项混淆攻击

**攻击模式**：攻击者注册一个名称与热门软件包（或内部软件包名称）相似的包，旨在拦截因输入错误而下载该包的用户。

**需收集的关键证据**：
- [ ] 该可疑包在注册仓库中的注册时间戳
- [ ] 包的内容：其中是否包含恶意代码，还是仅为空壳？
- [ ] 该可疑包的下载统计数据
- [ ] 可能成为攻击目标的内部软件包名称（若为私有仓库范围）
- [ ] 恶意包的元数据中是否存在对合法软件包的引用

**假设生成提示**：
```
[HYPOTHESIS] Package <MALICIOUS_NAME> was registered on <DATE> [EV-XXXX] to 
typosquat on <LEGITIMATE_NAME>, targeting users who misspell the package name. 
The package contains <BEHAVIOR> [EV-YYYY].
```

## 模板5：强制推送历史重写（证据删除）

**行为模式**：在检测到恶意提交后（或在尚未广泛通知之前），攻击者会通过强制推送将该恶意提交从分支历史中移除。

**检测是关键**——此模板旨在证明确实发生了数据删除行为。

**需收集的关键证据**：
- [ ] 包含 `distinct_size=0` 参数的 GH Archive PushEvent（表明为强制推送）[EV-XXXX]
- [ ] 强制推送之前的提交 SHA 值（来自 GH Archive 的 `payload.before`）
- [ ] 通过直接 URL 或 `git fetch origin SHA` 恢复被删除的提交
- [ ] 提交页面在删除前的 Wayback Machine 快照
- [ ] git log 中的时间线缺失现象（归档中可见 N 个提交，但当前仓库中仅显示 M 个 < N）

**假设生成提示**：
```
[HYPOTHESIS] Actor <HANDLE> force-pushed branch <BRANCH> on <DATE> [EV-XXXX] 
to erase commit <SHA> [EV-YYYY], which contained <MALICIOUS_CONTENT>. 
The erased commit was recovered via <METHOD> [EV-ZZZZ].
```

## 跨场景调查检查清单

无论使用何种调查模板，均需执行以下步骤：

- [ ] 检查所有贡献者是否存在新创建的账户（在恶意行为发生时账号创建时间不超过30天）
- [ ] 查看是否有维护者账户在案发期间更改了邮箱地址（这可能是账号被劫持的迹象）
- [ ] 验证可疑提交中的GPG签名是否与已知的维护者密钥匹配
- [ ] 检查仓库在事件发生前后是否发生过所有权变更或所属组织变动
- [ ] 查找在恶意提交之后立即出现的“清理”类提交（这属于掩盖行为的特征）
- [ ] 检查同一作者开发的其他相关包或仓库中是否存在类似异常模式
