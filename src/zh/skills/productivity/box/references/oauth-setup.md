# OAuth 设置

在所有 Hermes 与 Box 的连接中均应使用 OAuth。OAuth 会遵循已登录 Box 用户的权限以及应用程序所申请的权限范围，不会授予企业级的全局访问权限。

## 选择 OAuth 账户

指定 Hermes 应该以哪个 Box 账户的身份进行操作。OAuth 会依据该账户的权限来限制访问。如果用户希望获得更严格的权限控制，可选用仅被授权访问特定文件、文件夹或 Hubs 的账户。切勿仅为实现特殊功能而将此类账户设置为管理员。

所有使用共享或后台部署模式的 Hermes 实例的用户，都将获得其所对应授权的 Box 账户的访问权限，因此请勿将其连接到权限更广的个人账户或管理员账户。在开始浏览器授权流程之前，请确保用于授权的浏览器已使用目标 Box 账户登录。

请为该环境选择一个具有描述性的名称，例如 `hermes-box-oauth`。在确认其身份信息之前，切勿覆盖现有环境或重新进行授权。

## 同主机交互模式

首先根据 [CLI 指南](cli-guide.md) 找到对应的 Box 命令运行器。随后确认 Hermes 是否运行在与用户用于授权 Box 的浏览器相同的计算机上。仅当用户确认情况如此时才可使用此模式，这通常适用于本地计算机环境。切勿仅凭操作系统信息就做出判断。应直接使用已确定的命令运行器，除非已安装并验证了确切的本地 npm 前缀，否则不要自行重新构建。

先执行一次不包含`--code`参数的官方本地登录操作，让其终端进程保持运行状态直至退出，随后对相关执行主体进行验证。以下示例使用了`box`命令；仅当Hermes已安装并验证过私有的CLI版本时，才需将此可执行文件替换为之前已验证过的本地运行器。

```bash
box login --default-box-app --name <ENVIRONMENT_NAME>
box users:get me --json --fields id,name,login
```

该流程通过浏览器创建并选择指定的环境，应通过Hermes的终端来执行相关操作，而非要求用户复制运行命令。系统需先提示用户进行授权，等待CLI进程完成后再继续进行角色验证。由CLI负责打开授权页面并接收本地回调信号，严禁使用浏览器工具、查看浏览器标签页、获取生成的URL、导航至Box网站，或要求用户粘贴代码。

若回调服务器无法绑定端口3000，或者浏览器显示的授权结果无法使用，又或是回调信号始终无法送达正在等待的CLI进程，则应在重新尝试之前终止当前的登录流程。请依次在支持的端口`3001`、`4000`、`5000`和`8080`上重新尝试官方应用，并在每次操作成功完成后进行角色验证。

```bash
box login --default-box-app --port 3001 --name <ENVIRONMENT_NAME>
```

请勿仅因端口 3000 使用失败，就将同主机架构的设置切换为 `--code` 模式。只有在所有支持的本地端口均无法使用，或用户确认授权浏览器运行在另一台主机上时，才应使用 `--code` 模式。

## 分离主机或无头模式

仅当用户明确确认 Hermes 运行在远程主机上——例如 VPS、容器或云虚拟机——或者确认其为无头模式且授权浏览器位于其他计算机上时，才可使用此路径。此时仍应使用之前已确定的运行器来执行操作：

```bash
box login --default-box-app --code --name <ENVIRONMENT_NAME>
```

仅当该流程受控于用户授权的浏览器时，才可使用浏览器工具打开显示的 URL。否则，应先展示该 URL 并暂停，等待用户登录并批准访问权限，之后再继续执行 CLI 的代码与状态相关提示，并对操作主体进行验证。若存在同主机回调功能，则无需使用此路径。

## 现有环境

Box CLI 可存储多个命名环境，但目前仅使用一个默认环境：

```bash
box configure:environments:list
box configure:environments:set-current <ENVIRONMENT_NAME>
box users:get me --json --fields id,name,login
```

在切换当前环境之前，请务必先获得批准，尤其是当该环境为共享环境或后台安装环境时。只有在获得批准并确认生成的 Actor 后，才能进行切换。如果返回的身份仅支持 API 访问且无法通过常规 Box 登录，则不可将其用于 Hermes；应通过 OAuth 连接常规 Box 账户。

## 自定义 OAuth 平台应用

仅当所需操作需要官方 CLI 应用无法提供的权限范围时（例如**管理 Webhook**），才可使用此路径。打开 [Box 开发者控制台](https://app.box.com/developers/console)，创建或选择一个具有**用户身份验证（OAuth 2.0）**功能的平台应用，然后仅启用所需的权限范围。切勿为避免授权错误而随意扩大权限范围。

其拓扑结构配置应与官方应用保持一致。对于同主机上的浏览器，需在应用的**配置**选项卡中添加 `http://localhost:3000/callback` 作为 OAuth 重定向地址，保存设置后即可运行：

```bash
box login --platform-app --port 3000 --name <ENVIRONMENT_NAME>
```

如果端口 3000 无法被绑定，可选择另一个空闲的本地端口，将完整的 `http://localhost:<PORT>/callback` URI 添加到平台应用中，保存配置后终止失败的登录进程，再使用对应的 `--port` 参数重新尝试。与官方应用不同，自定义平台应用可以使用任何已注册完整回调 URI 的端口。

对于授权浏览器位于另一台计算机上的远程或无头 Hermes 运行环境，则需要注册相同的回环地址回调 URI，并同时添加 `--code` 参数：

```bash
box login --platform-app --code --port 3000 --name <ENVIRONMENT_NAME>
```

在启动远程流程之前，需告知用户浏览器可能会加载到无法访问的本地主机页面，这是正常现象。生成的URL中会包含`code`和`state`这两个参数，等待中的CLI会请求这些值。只需让用户提供这两个参数，将其提交给正在运行的进程，随后即可验证对应的执行主体。切勿查看无关的浏览器标签页，也不应在远程主机上切换到本地回调工作流。

让CLI提示用户输入客户端ID和客户端密钥。不要要求用户将客户端密钥粘贴到聊天窗口中、写入Hermes配置文件，或提供未经验证的本地运行命令供其复制。首先在浏览器中对目标用户进行身份认证，然后再验证生成的执行主体。应将仅管理员才能执行的操作与常规的Hermes OAuth身份认证流程分开处理。

## 官方链接

- [Box CLI快速入门](https://developer.box.com/guides/cli/quick-start/)
- [Box CLI无界面登录](https://developer.box.com/guides/cli/headless-login/)
- [OAuth 2.0指南](https://developer.box.com/guides/authentication/oauth2/)
- [Box OAuth权限范围](https://developer.box.com/guides/api-calls/permissions-and-errors/scopes/)
