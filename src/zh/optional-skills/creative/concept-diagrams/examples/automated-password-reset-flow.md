# 自动化密码重置流程

该流程图分为两个部分，完整展示了Web应用程序密码重置的用户操作路径：初始请求阶段（忘记密码 → 邮箱验证 → 令牌生成），以及重置表单阶段（点击链接 → 输入新密码 → 令牌/密码验证）。图中运用了多出口决策菱形、三列分支布局、回环路径以及截面分隔箭头等设计元素。

## 主要设计模式

- **三列布局**：左列（cx=115处的错误/终端分支）、中列（cx=340处的主正常流程）、右列（cx=552处的令牌过期分支）——这种布局使得侧支路径能够与中心节点处于同一Y轴高度，且互不重叠。
- **基于 `<polygon>` 的决策菱形**：每个决策点都使用一个包含 `<polygon>` 元素及居中 `<text>` 元素的 `<g class="decision">` 包装结构；菱形的顶点坐标通过 `cx±hw, cy±hh` 计算得出（其中hw=100，hh=28）。
- **药丸形终端节点**：起始节点和结束节点的 `<rect>` 元素使用 `rx=22` 的半径来标识进入/退出点；而所有中间流程节点则使用 `rx=8`。
- **三分支决策路径**：每个菱形都包含一个“是”分支（向下的短 `<line>`）和一个“否”分支（先水平延伸再垂直通往侧列的 `<path>`）。
- **回环路径**：当出现匹配错误时，节点会通过x=215处的路由通道回退到密码输入节点——左列（右边缘x=210）与中列（左边缘x=220）之间有5像素的间隙；路径从错误节点的底部穿出，向下延伸后向右移动至x=215，再上升至目标节点的中间Y轴位置，最后向右进入节点左边缘5像素处。
- **阶段分隔符**：位于y=452处的虚线水平 `<line>` 将两个阶段分开；连接箭头穿过该线条，并附有淡色标签（“用户收到邮件”），以此保持流程的连贯性。
- **斜体注释**：关于通用提示语（“如果该邮箱存在……”）的具体用户界面文案，会以淡色斜体 `ts` 文本块的形式显示在左分支终端节点下方。
- **图例行**：底部的五个内联色块（灰色、紫色、青色、红色、琥珀色菱形）用于说明颜色与功能角色的对应关系。

## 图表

```xml
<svg width="100%" viewBox="0 0 680 960" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5"
            markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke"
            stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>

  <!--
    Column layout (680px viewBox, safe area x=40–640):
      Left  col : x=20,  w=190, cx=115  (error / terminal branches)
      Center col: x=220, w=240, cx=340  (main happy path)
      Right  col: x=465, w=175, cx=552  (expired-token branch)
      Loop corridor at x=215 (5-px gap between left and center cols)
  -->

  <!-- ═══ SECTION 1 — Forgot password request ═══ -->
  <text class="ts" x="40" y="38" opacity=".45">Section 1 — Forgot password request</text>

  <!-- START terminal (pill rx=22 signals start/end) -->
  <g class="c-gray">
    <rect x="220" y="46" width="240" height="44" rx="22"/>
    <text class="th" x="340" y="68" text-anchor="middle" dominant-baseline="central">User: &quot;Forgot password&quot;</text>
  </g>

  <line x1="340" y1="90" x2="340" y2="108" class="arr" marker-end="url(#arrow)"/>

  <!-- N2 · Enter email -->
  <g class="c-gray">
    <rect x="220" y="108" width="240" height="44" rx="8"/>
    <text class="th" x="340" y="130" text-anchor="middle" dominant-baseline="central">Enter email address</text>
  </g>

  <line x1="340" y1="152" x2="340" y2="172" class="arr" marker-end="url(#arrow)"/>

  <!-- D1 · Email in system?  diamond: center=(340,200) hw=100 hh=28 -->
  <g class="decision">
    <polygon points="340,172 440,200 340,228 240,200"/>
    <text class="th" x="340" y="200" text-anchor="middle" dominant-baseline="central">Email in system?</text>
  </g>

  <!-- D1 "No" → left column -->
  <path d="M 240,200 L 115,200 L 115,248" class="arr" marker-end="url(#arrow)"/>
  <text class="ts" x="178" y="193" text-anchor="middle" opacity=".75">No</text>

  <!-- D1 "Yes" → continue down -->
  <line x1="340" y1="228" x2="340" y2="248" class="arr" marker-end="url(#arrow)"/>
  <text class="ts" x="348" y="242" text-anchor="start" opacity=".75">Yes</text>

  <!-- ── Left branch (D1 = No): generic security message → end ── -->

  <!-- L1 · Generic message (security: never confirm email existence) -->
  <g class="c-gray">
    <rect x="20" y="248" width="190" height="56" rx="8"/>
    <text class="th" x="115" y="269" text-anchor="middle" dominant-baseline="central">Generic message shown</text>
    <text class="ts" x="115" y="287" text-anchor="middle" dominant-baseline="central">Email sent if found</text>
  </g>

  <line x1="115" y1="304" x2="115" y2="324" class="arr" marker-end="url(#arrow)"/>

  <!-- L2 · End terminal (left) -->
  <g class="c-gray">
    <rect x="20" y="324" width="190" height="44" rx="22"/>
    <text class="th" x="115" y="346" text-anchor="middle" dominant-baseline="central">Request handled</text>
  </g>

  <!-- Italic annotation: actual UX copy shown below the end node -->
  <text class="ts" x="20" y="384" opacity=".45" font-style="italic">&quot;If that email exists, a reset</text>
  <text class="ts" x="20" y="398" opacity=".45" font-style="italic">link has been sent.&quot;</text>

  <!-- ── Center Yes branch: system generates & sends token ── -->

  <!-- N3 · Generate unique token -->
  <g class="c-purple">
    <rect x="220" y="248" width="240" height="56" rx="8"/>
    <text class="th" x="340" y="269" text-anchor="middle" dominant-baseline="central">Generate unique token</text>
    <text class="ts" x="340" y="287" text-anchor="middle" dominant-baseline="central">Time-limited, cryptographic</text>
  </g>

  <line x1="340" y1="304" x2="340" y2="324" class="arr" marker-end="url(#arrow)"/>

  <!-- N4 · Store token + user ID -->
  <g class="c-purple">
    <rect x="220" y="324" width="240" height="44" rx="8"/>
    <text class="th" x="340" y="346" text-anchor="middle" dominant-baseline="central">Store token + user ID</text>
  </g>

  <line x1="340" y1="368" x2="340" y2="388" class="arr" marker-end="url(#arrow)"/>

  <!-- N5 · Send reset email -->
  <g class="c-teal">
    <rect x="220" y="388" width="240" height="44" rx="8"/>
    <text class="th" x="340" y="410" text-anchor="middle" dominant-baseline="central">Send reset link via email</text>
  </g>

  <!-- ═══ Section separator ═══ -->
  <line x1="40" y1="452" x2="640" y2="452"
        stroke="var(--border)" stroke-width="1" stroke-dasharray="8 5"/>

  <!-- Arrow crossing separator (with inline label) -->
  <line x1="340" y1="432" x2="340" y2="472" class="arr" marker-end="url(#arrow)"/>
  <text class="ts" x="348" y="448" text-anchor="start" opacity=".55">user receives email</text>

  <text class="ts" x="40" y="464" opacity=".45">Section 2 — Password reset form</text>

  <!-- ═══ SECTION 2 — Password reset form ═══ -->

  <!-- N6 · User clicks reset link -->
  <g class="c-gray">
    <rect x="220" y="480" width="240" height="44" rx="8"/>
    <text class="th" x="340" y="502" text-anchor="middle" dominant-baseline="central">User clicks reset link</text>
  </g>

  <line x1="340" y1="524" x2="340" y2="544" class="arr" marker-end="url(#arrow)"/>

  <!-- N7 · Enter new password ×2 -->
  <g class="c-gray">
    <rect x="220" y="544" width="240" height="56" rx="8"/>
    <text class="th" x="340" y="565" text-anchor="middle" dominant-baseline="central">Enter new password ×2</text>
    <text class="ts" x="340" y="583" text-anchor="middle" dominant-baseline="central">Confirm both passwords match</text>
  </g>

  <line x1="340" y1="600" x2="340" y2="620" class="arr" marker-end="url(#arrow)"/>

  <!-- D2 · Token expired?  diamond: center=(340,648) hw=100 hh=28 -->
  <g class="decision">
    <polygon points="340,620 440,648 340,676 240,648"/>
    <text class="th" x="340" y="648" text-anchor="middle" dominant-baseline="central">Token expired?</text>
  </g>

  <!-- D2 "Yes" → right column (expired-token branch) -->
  <path d="M 440,648 L 552,648 L 552,692" class="arr" marker-end="url(#arrow)"/>
  <text class="ts" x="496" y="641" text-anchor="middle" opacity=".75">Yes</text>

  <!-- D2 "No" → down to password-match check -->
  <line x1="340" y1="676" x2="340" y2="714" class="arr" marker-end="url(#arrow)"/>
  <text class="ts" x="348" y="698" text-anchor="start" opacity=".75">No</text>

  <!-- ── Right branch (D2 = Yes): token expired → dead end ── -->

  <!-- R1 · Token expired error -->
  <g class="c-red">
    <rect x="465" y="692" width="175" height="56" rx="8"/>
    <text class="th" x="552" y="713" text-anchor="middle" dominant-baseline="central">Token expired</text>
    <text class="ts" x="552" y="731" text-anchor="middle" dominant-baseline="central">Show expiry error</text>
  </g>

  <line x1="552" y1="748" x2="552" y2="768" class="arr" marker-end="url(#arrow)"/>

  <!-- R2 · End terminal (right) -->
  <g class="c-gray">
    <rect x="465" y="768" width="175" height="44" rx="22"/>
    <text class="th" x="552" y="790" text-anchor="middle" dominant-baseline="central">End — request again</text>
  </g>

  <!-- D3 · Passwords match?  diamond: center=(340,742) hw=100 hh=28 -->
  <g class="decision">
    <polygon points="340,714 440,742 340,770 240,742"/>
    <text class="th" x="340" y="742" text-anchor="middle" dominant-baseline="central">Passwords match?</text>
  </g>

  <!-- D3 "No" → left column (mismatch branch) -->
  <path d="M 240,742 L 115,742 L 115,786" class="arr" marker-end="url(#arrow)"/>
  <text class="ts" x="178" y="735" text-anchor="middle" opacity=".75">No</text>

  <!-- D3 "Yes" → down to reset -->
  <line x1="340" y1="770" x2="340" y2="790" class="arr" marker-end="url(#arrow)"/>
  <text class="ts" x="348" y="783" text-anchor="start" opacity=".75">Yes</text>

  <!-- ── Left branch (D3 = No): passwords don't match → loop back ── -->

  <!-- L3 · Password mismatch error -->
  <g class="c-red">
    <rect x="20" y="786" width="190" height="56" rx="8"/>
    <text class="th" x="115" y="807" text-anchor="middle" dominant-baseline="central">Password mismatch</text>
    <text class="ts" x="115" y="825" text-anchor="middle" dominant-baseline="central">Passwords do not match</text>
  </g>

  <!-- Loop-back arrow: exits L3 bottom → drops to y=862 →
       travels right to corridor x=215 → climbs to N7 center y=572 →
       enters N7 left edge at (220, 572) pointing right -->
  <path d="M 115,842 L 115,862 L 215,862 L 215,572 L 220,572"
        class="arr" marker-end="url(#arrow)"/>
  <text class="ts" x="224" y="538" text-anchor="start" opacity=".6">retry</text>

  <!-- ── Center Yes branch (D3 = Yes): reset password & invalidate token ── -->

  <!-- N8 · Reset password -->
  <g class="c-teal">
    <rect x="220" y="790" width="240" height="56" rx="8"/>
    <text class="th" x="340" y="811" text-anchor="middle" dominant-baseline="central">Reset password</text>
    <text class="ts" x="340" y="829" text-anchor="middle" dominant-baseline="central">Invalidate used token</text>
  </g>

  <line x1="340" y1="846" x2="340" y2="866" class="arr" marker-end="url(#arrow)"/>

  <!-- N9 · Success terminal -->
  <g class="c-green">
    <rect x="220" y="866" width="240" height="44" rx="22"/>
    <text class="th" x="340" y="888" text-anchor="middle" dominant-baseline="central">Password reset complete</text>
  </g>

  <!-- ═══ Legend ═══ -->
  <text class="ts" x="40" y="930" opacity=".4">Legend —</text>
  <rect x="108" y="920" width="13" height="13" rx="2" fill="#F1EFE8" stroke="#5F5E5A" stroke-width="0.5"/>
  <text class="ts" x="126" y="930" opacity=".7">User action</text>
  <rect x="210" y="920" width="13" height="13" rx="2" fill="#EEEDFE" stroke="#534AB7" stroke-width="0.5"/>
  <text class="ts" x="228" y="930" opacity=".7">System process</text>
  <rect x="334" y="920" width="13" height="13" rx="2" fill="#E1F5EE" stroke="#0F6E56" stroke-width="0.5"/>
  <text class="ts" x="352" y="930" opacity=".7">Email / success</text>
  <rect x="455" y="920" width="13" height="13" rx="2" fill="#FCEBEB" stroke="#A32D2D" stroke-width="0.5"/>
  <text class="ts" x="473" y="930" opacity=".7">Error state</text>
  <polygon points="556,926 566,932 556,938 546,932" fill="#FAEEDA" stroke="#854F0B" stroke-width="0.5"/>
  <text class="ts" x="572" y="932" opacity=".7">Decision</text>

</svg>
```

## 自定义 CSS

在托管页面的 `<style>` 标签中添加这些类（在标准技能 CSS 之外）：

```css
/* Decision diamond — amber fill, same palette as c-amber */
.decision > polygon { fill: #FAEEDA; stroke: #854F0B; stroke-width: 0.5; }
.decision > .th     { fill: #633806; }

@media (prefers-color-scheme: dark) {
  .decision > polygon { fill: #633806; stroke: #EF9F27; }
  .decision > .th     { fill: #FAC775; }
}
```

## 颜色分配规则

| 元素 | 颜色 | 原因 |
|------|------|------|
| 起始/结束节点 | `c-gray` | 作为中性的起始与结束点 |
| 用户操作（输入邮箱、点击链接、输入密码） | `c-gray` | 仅涉及用户操作，无需系统处理 |
| 通用消息及请求处理完成节点 | `c-gray` | 故意采用中性颜色——安全提示信息不得泄露任何数据 |
| 生成并存储令牌 | `c-purple` | 后端系统操作 |
| 发送重置邮件 | `c-teal` | 正向外部操作（向外发送信息） |
| 令牌过期错误 | `c-red` | 失败/阻塞状态 |
| 密码不匹配错误 | `c-red` | 验证失败 |
| 重置密码及操作成功 | `c-teal` / `c-green` | 正向结果：操作用青色表示，节点用绿色表示 |
| 决策菱形节点 | `c-amber`（自定义`.decision`样式） | 警告/分支点——与琥珀色的语义含义相符 |

## 布局说明

- **视图框尺寸**：680×960——适用于包含两个阶段的纵向流程图
- **三列结构**：左列（cx=115）、中列（cx=340）、右列（cx=552）——每个分支均保持在所在列内，仅`<path>`箭头会跨越列边界
- **菱形节点公式**：`<polygon points="cx,cy-hh cx+hw,cy cx,cy+hh cx-hw,cy"/>`，其中hw=100、hh=28，可生成尺寸为200×56像素的菱形节点，其位置恰好位于中列范围内（x=220–460）
- **分支路径规则**：“否”分支使用`<path d="M left_point,cy L side_cx,cy L side_cx,node_top">`——由一段水平线段和一段垂直线段组成，无需曲线
- **循环路径设计**：左列与中列之间x=210–220处有5像素的间隙，可作为清晰的垂直通道用于循环路径，且不会导致节点重叠；该路径从节点底部出发，向下移动20像素后向右延伸至x=215，再上升至目标高度，从左侧进入节点
- **章节分隔线**：在y=452位置使用`stroke-dasharray="8 5"`的虚线`<line>`作为视觉上的阶段分隔；单个连接箭头从中部穿过该分隔线，箭头上配有淡色标签
- **胶囊形节点**：设置`rx=22`（即44像素节点高度的一半），即可形成完美的胶囊/药丸形状——所有起始/结束节点均应统一使用此样式
- **错误提示标注**：相关的用户界面文本会以淡色（`opacity=".45"`）、斜体`ts`文字的形式显示在对应节点下方，既能提供必要信息，又不会干扰整体流程的清晰度
