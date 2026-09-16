# 广播功能

该功能为Hermes Desktop附带的插件，**默认处于关闭状态**。请在“设置 → 插件”中开启“广播”选项。只有按下播放键时，音频才会开始播放。

## 控制功能

状态栏控件包括简洁的盲文波形图、电台选择器、播放/暂停按钮以及双箭头形式的下一首歌曲切换按钮。电台选择器支持固定常用电台、搜索功能、更大的波形图显示、歌曲元数据展示、音量调节，以及电台网站链接。点击“下一首”可切换电台；对于直播内容，则不支持跳过单首歌曲。点击“暂停”可停止流媒体播放，再次播放则恢复直播状态。

预设电台包括Nightride FM、Radio Paradise和EVE Radio（GamingNow）。搜索功能可结合本地电台与[Radio Browser](https://api.radio-browser.info/)的搜索结果，支持接收非HLS协议的HTTPS流媒体，并通过编号和URL进行去重处理。固定电台、当前播放电台及音量设置均保存在插件级别的本地存储中。

## 插件边界

`plugin.js`文件仅导入`@hermes/plugin-sdk`、`react`和`react/jsx-runtime`这三个模块。系统会自动检测到已捆绑的该插件；若设置`defaultEnabled: false`，则使用常规的直播功能开关控制。无需对Shell、SDK、后端、依赖项或注册表进行任何修改。

在开发过程中，可通过运行时插件机制将同一个纯ESM格式的文件加载至` $HERMES_HOME/desktop-plugins/radio/plugin.js `路径下。请勿将该重复版本的文件与已捆绑的版本一同安装。该插件的界面样式采用Hermes主题主题变量，关闭广播功能时这些样式会自动消失。同时，播放功能、计时器及音频节点也会被释放。关闭窗口即会停止播放，因为该功能不支持后台音频服务。当有窗口开始播放时，其他窗口的播放也会随之暂停。

## 音频与隐私保护

两种波形格式均使用真实的音频采样数据，并显示两条历史轨迹。静音状态时波形保持平坦；运动减弱时会冻结显示画面。无法进行分析的流媒体会在不依赖CORS机制的情况下重新尝试播放，并显示活动指示器，而不会生成虚构的音量数值。在选择器打开且正在播放音乐时，系统会自动获取Nightride和EVE Radio歌曲的元数据。歌手姓名会直接链接到其个人主页，而非搜索结果或具体歌曲页面。苹果的公开歌手查询功能可将唯一确定的姓名对应到Apple Music上的歌手资料。对于Spotify、Bandcamp或歌手官方主页，系统则会回退至MusicBrainz作为数据来源。若无法匹配或匹配结果不明确，系统会以纯文本形式显示，而不会出现失效链接或空白图标。歌手姓名仅会在选择器显示实时元数据时发送至这些服务，相关结果会被缓存一天。向MusicBrainz发出的请求会在不同时间窗口间分散处理，且无需使用账户或API密钥。

音频内容会直接连接到广播源。搜索功能会将输入的电台名称发送至Radio Browser。该系统不支持账户管理、密钥使用、数据分析、录音或转播功能。已禁用的插件不会执行任何操作；启用插件也不会自动播放音乐。流媒体的可用性、地区限制及元数据内容可能各不相同。Hermes并非这些广播源的官方推荐产品。

## 参考资料

- [Nightride 直播频道](https://stream.nightride.fm/)  
- [Radio Paradise 直播链接](https://radioparadise.com/listen/stream-links)  
- [EVE Radio / GamingNow](https://gamingnow.net/eve-radio/)  
- [Original EVE jukebox](https://ashy.vargur.dev/the-eve-online-jukebox-project/)：紧凑型播放器/列表层级结构。  
- [node-drawille](https://github.com/madbence/node-drawille)（MIT 许可）：盲文像素打包技术的前身方案。  
- [Phosphor](https://github.com/hubertlim/oscilloscope_playground)（MIT 许可）：前帧保留效果的灵感来源。  

所有上游代码、资源文件、着色器及依赖项均未被复制使用。
