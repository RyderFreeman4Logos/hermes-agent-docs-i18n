# 下单流程 —— UML序列图

该图展示了电子商务系统中“下单”用例的UML序列图。六条生命线（:Customer、:ShoppingCart、:OrderController、:PaymentGateway、:InventorySystem、:EmailService）通过14条编号的消息相互交互。一个**alt**组合片段（琥珀色）用于表示三种条件结果——支付成功、支付失败以及商品缺货。嵌套在成功分支内的**par**组合片段（青色）则展示了邮件确认与库存状态更新的同时进行过程。图中还使用了激活条、两种不同类型的箭头标记、UML五边形片段标签以及守卫条件。

## 主要设计模式

- **等间距排列的6条生命线**：各生命线的中心点分别位于x=90、190、290、390、490、590处，间距为100像素。因此，最左侧的生命线左边界位于x=40，最右侧的生命线右边界位于x=640，恰好填满安全区域。
- **两行式的参与者标题**：每个生命线框中，第一行显示`":"`符号（颜色较浅，为第三级颜色），第二行显示类名（颜色稍深且加粗），这与UML匿名实例表示法`:ClassName`保持一致。
- **两种独立的箭头标记**：`#arr-call`代表同步调用，采用实心三角形形状（`<polygon>`）；`#arr-ret`代表虚线返回消息，采用空心箭头形状（`fill="none"`）。两者均通过`context-stroke`属性继承线条颜色。
- **激活条**：宽度为8像素的窄矩形（`class="activation"`）叠加在生命线杆上，用于显示对象的执行时间。OrderController的激活条覆盖整个交互过程；PaymentGateway、InventorySystem和EmailService的激活条则在其活跃时段显示较短的长度。
- **组合片段的五边形标签**：每个`alt`/`par`框架的左上角都使用`<polygon>`形状的标签，其顶点坐标遵循`(x,y) (x+w,y) (x+w+6,y+6) (x+w+6,y+18) (x,y+18)`的规律，从而形成UML特有的凹角。
- **alt框架内的par嵌套结构**：青色的`par`矩形位于琥珀色`alt`矩形的第一个分支内。内部矩形通过向内偏移x/y坐标（+15/+2）的设计，确保两侧边框依然清晰可见且可区分。
- **守卫条件**：守卫条件以斜体文字形式出现在每个`alt`框架分隔线之后，或直接位于第一个分支的框架内部。这些文字通过专门的`guard-lbl`类呈现，具有斜体样式和琥珀色背景。
- **分支分隔线**：根据UML规范，`alt`分支的分隔线为实线水平线（`.frag-alt-div`），宽度与整个`alt`矩形相同；而`par`分支的分隔线则为虚线（`.frag-par-div`）。
- **生命线端点标记**：在所有生命线杆的底部（y=590处）有长度为14像素的短水平刻线，用于正式标记每个生命线的结束位置。
- **消息序列注释**：图例下方有一行淡淡的编号（①–③ / ④–⑩ / ⑪–⑫ / ⑬–⑭），用于说明四组消息的顺序，不会给图表主体带来过多干扰。

## 图表展示

```xml
<svg width="100%" viewBox="0 0 680 648" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Open chevron arrowhead — return messages -->
    <marker id="arr-ret" viewBox="0 0 10 10" refX="8" refY="5"
            markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke"
            stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>

    <!-- Filled triangle arrowhead — synchronous calls -->
    <marker id="arr-call" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="7" markerHeight="7" orient="auto">
      <polygon points="0,1 10,5 0,9" fill="context-stroke"/>
    </marker>
  </defs>

  <!--
    Lifeline centres (x):
      L1 :Customer        →  90
      L2 :ShoppingCart    → 190
      L3 :OrderController → 290
      L4 :PaymentGateway  → 390
      L5 :InventorySystem → 490
      L6 :EmailService    → 590
    Actor boxes: x = cx−50, y=20, w=100, h=56, rx=6
    Lifelines:   x = cx,    y1=76, y2=590
  -->

  <!-- ── 1. LIFELINE DASHED STEMS (drawn first, behind everything) ── -->
  <line x1="90"  y1="76" x2="90"  y2="590" class="lifeline"/>
  <line x1="190" y1="76" x2="190" y2="590" class="lifeline"/>
  <line x1="290" y1="76" x2="290" y2="590" class="lifeline"/>
  <line x1="390" y1="76" x2="390" y2="590" class="lifeline"/>
  <line x1="490" y1="76" x2="490" y2="590" class="lifeline"/>
  <line x1="590" y1="76" x2="590" y2="590" class="lifeline"/>

  <!-- ── 2. ACTOR HEADER BOXES ── -->

  <!-- :Customer -->
  <rect x="40"  y="20" width="100" height="56" rx="6" class="actor"/>
  <text class="actor-colon" x="90"  y="40" text-anchor="middle" dominant-baseline="central">:</text>
  <text class="actor-name"  x="90"  y="58" text-anchor="middle" dominant-baseline="central">Customer</text>

  <!-- :ShoppingCart -->
  <rect x="140" y="20" width="100" height="56" rx="6" class="actor"/>
  <text class="actor-colon" x="190" y="37" text-anchor="middle" dominant-baseline="central">:</text>
  <text class="actor-name"  x="190" y="55" text-anchor="middle" dominant-baseline="central">ShoppingCart</text>

  <!-- :OrderController -->
  <rect x="240" y="20" width="100" height="56" rx="6" class="actor"/>
  <text class="actor-colon" x="290" y="37" text-anchor="middle" dominant-baseline="central">:</text>
  <text class="actor-name"  x="290" y="55" text-anchor="middle" dominant-baseline="central">OrderController</text>

  <!-- :PaymentGateway -->
  <rect x="340" y="20" width="100" height="56" rx="6" class="actor"/>
  <text class="actor-colon" x="390" y="37" text-anchor="middle" dominant-baseline="central">:</text>
  <text class="actor-name"  x="390" y="55" text-anchor="middle" dominant-baseline="central">PaymentGateway</text>

  <!-- :InventorySystem -->
  <rect x="440" y="20" width="100" height="56" rx="6" class="actor"/>
  <text class="actor-colon" x="490" y="37" text-anchor="middle" dominant-baseline="central">:</text>
  <text class="actor-name"  x="490" y="55" text-anchor="middle" dominant-baseline="central">InventorySystem</text>

  <!-- :EmailService -->
  <rect x="540" y="20" width="100" height="56" rx="6" class="actor"/>
  <text class="actor-colon" x="590" y="37" text-anchor="middle" dominant-baseline="central">:</text>
  <text class="actor-name"  x="590" y="55" text-anchor="middle" dominant-baseline="central">EmailService</text>

  <!-- ── 3. ACTIVATION BARS ── -->
  <!-- ShoppingCart: active while forwarding checkout → placeOrder -->
  <rect x="186" y="102" width="8" height="26"  rx="1" class="activation"/>
  <!-- OrderController: active throughout full sequence -->
  <rect x="286" y="128" width="8" height="415" rx="1" class="activation"/>
  <!-- PaymentGateway: active during auth check (happy-path branch only) -->
  <rect x="386" y="154" width="8" height="46"  rx="1" class="activation"/>
  <!-- InventorySystem: active from reserveItems → updateStockLevels end -->
  <rect x="486" y="225" width="8" height="128" rx="1" class="activation"/>
  <!-- EmailService: active during confirmation send -->
  <rect x="586" y="290" width="8" height="25"  rx="1" class="activation"/>

  <!-- ── 4. PRE-ALT MESSAGES ── -->

  <!-- ① checkout()  :Customer → :ShoppingCart -->
  <line x1="90"  y1="102" x2="186" y2="102" class="msg-call" marker-end="url(#arr-call)"/>
  <text class="mlbl" x="140" y="97" text-anchor="middle">checkout()</text>

  <!-- ② placeOrder(cartItems)  :ShoppingCart → :OrderController -->
  <line x1="194" y1="128" x2="286" y2="128" class="msg-call" marker-end="url(#arr-call)"/>
  <text class="mlbl" x="242" y="123" text-anchor="middle">placeOrder(cartItems)</text>

  <!-- ③ authorizePayment(amount)  :OrderController → :PaymentGateway -->
  <line x1="294" y1="154" x2="386" y2="154" class="msg-call" marker-end="url(#arr-call)"/>
  <text class="mlbl" x="342" y="149" text-anchor="middle">authorizePayment(amount)</text>

  <!-- ── 5. ALT COMBINED FRAGMENT  y=166 → y=563 ── -->

  <!-- Outer alt rectangle -->
  <rect x="45" y="166" width="590" height="397" rx="3" class="frag-alt-bg"/>

  <!-- Pentagon "alt" tag: TL corner notch shape -->
  <polygon points="45,166 84,166 90,173 90,185 45,185" class="frag-alt-tag"/>
  <text class="frag-alt-kw" x="67" y="178" text-anchor="middle" dominant-baseline="central">alt</text>

  <!-- Guard: branch 1 -->
  <text class="guard-lbl" x="96" y="179" dominant-baseline="central">[payment authorized]</text>

  <!-- ─── Branch 1: payment authorized ─── -->

  <!-- ④ « authorized »  :PaymentGateway → :OrderController (dashed return) -->
  <line x1="386" y1="200" x2="294" y2="200" class="msg-ret" marker-end="url(#arr-ret)"/>
  <text class="rlbl" x="342" y="195" text-anchor="middle">« authorized »</text>

  <!-- ⑤ reserveItems(cartItems)  :OrderController → :InventorySystem -->
  <line x1="294" y1="225" x2="486" y2="225" class="msg-call" marker-end="url(#arr-call)"/>
  <text class="mlbl" x="392" y="220" text-anchor="middle">reserveItems(cartItems)</text>

  <!-- ⑥ « itemsReserved »  :InventorySystem → :OrderController (dashed return) -->
  <line x1="486" y1="250" x2="294" y2="250" class="msg-ret" marker-end="url(#arr-ret)"/>
  <text class="rlbl" x="392" y="245" text-anchor="middle">« itemsReserved »</text>

  <!-- ── 6. PAR COMBINED FRAGMENT (nested inside alt branch 1)  y=266 → y=373 ── -->

  <!-- Inner par rectangle -->
  <rect x="60" y="266" width="560" height="107" rx="3" class="frag-par-bg"/>

  <!-- Pentagon "par" tag -->
  <polygon points="60,266 97,266 102,272 102,284 60,284" class="frag-par-tag"/>
  <text class="frag-par-kw" x="81" y="275" text-anchor="middle" dominant-baseline="central">par</text>

  <!-- Par branch 1: email confirmation -->

  <!-- ⑦ sendConfirmationEmail()  :OrderController → :EmailService -->
  <line x1="294" y1="295" x2="586" y2="295" class="msg-call" marker-end="url(#arr-call)"/>
  <text class="mlbl" x="442" y="290" text-anchor="middle">sendConfirmationEmail()</text>

  <!-- ⑧ « emailQueued »  :EmailService → :OrderController (dashed return) -->
  <line x1="586" y1="318" x2="294" y2="318" class="msg-ret" marker-end="url(#arr-ret)"/>
  <text class="rlbl" x="442" y="313" text-anchor="middle">« emailQueued »</text>

  <!-- Par branch divider (dashed, per UML spec) -->
  <line x1="60" y1="336" x2="620" y2="336" class="frag-par-div"/>

  <!-- Par branch 2: stock level update -->

  <!-- ⑨ updateStockLevels()  :OrderController → :InventorySystem -->
  <line x1="294" y1="355" x2="486" y2="355" class="msg-call" marker-end="url(#arr-call)"/>
  <text class="mlbl" x="392" y="350" text-anchor="middle">updateStockLevels()</text>

  <!-- PAR fragment ends at y=373 -->

  <!-- ⑩ « orderPlaced »  :OrderController → :Customer (dashed return, after par) -->
  <line x1="286" y1="395" x2="90"  y2="395" class="msg-ret" marker-end="url(#arr-ret)"/>
  <text class="rlbl" x="190" y="390" text-anchor="middle">« orderPlaced »</text>

  <!-- ─── Alt else: [payment failed] ─── -->

  <!-- Alt branch divider 1 (solid line) -->
  <line x1="45" y1="415" x2="635" y2="415" class="frag-alt-div"/>
  <text class="guard-lbl" x="50" y="429" dominant-baseline="central">[payment failed]</text>

  <!-- ⑪ « authFailed »  :PaymentGateway → :OrderController (dashed return) -->
  <line x1="390" y1="448" x2="294" y2="448" class="msg-ret" marker-end="url(#arr-ret)"/>
  <text class="rlbl" x="344" y="443" text-anchor="middle">« authFailed »</text>

  <!-- ⑫ error(PAYMENT_FAILED)  :OrderController → :Customer -->
  <line x1="286" y1="470" x2="90"  y2="470" class="msg-call" marker-end="url(#arr-call)"/>
  <text class="mlbl" x="190" y="465" text-anchor="middle">error(PAYMENT_FAILED)</text>

  <!-- ─── Alt else: [item unavailable] ─── -->

  <!-- Alt branch divider 2 (solid line) -->
  <line x1="45" y1="490" x2="635" y2="490" class="frag-alt-div"/>
  <text class="guard-lbl" x="50" y="504" dominant-baseline="central">[item unavailable]</text>

  <!-- ⑬ « unavailable »  :InventorySystem → :OrderController (dashed return) -->
  <line x1="486" y1="523" x2="294" y2="523" class="msg-ret" marker-end="url(#arr-ret)"/>
  <text class="rlbl" x="392" y="518" text-anchor="middle">« unavailable »</text>

  <!-- ⑭ error(ITEM_UNAVAILABLE)  :OrderController → :Customer -->
  <line x1="286" y1="545" x2="90"  y2="545" class="msg-call" marker-end="url(#arr-call)"/>
  <text class="mlbl" x="190" y="540" text-anchor="middle">error(ITEM_UNAVAILABLE)</text>

  <!-- ALT fragment ends at y=563 -->

  <!-- ── 7. LIFELINE END CAPS (short horizontal tick at y=590) ── -->
  <line x1="83"  y1="590" x2="97"  y2="590" stroke="var(--text-tertiary)" stroke-width="1.5"/>
  <line x1="183" y1="590" x2="197" y2="590" stroke="var(--text-tertiary)" stroke-width="1.5"/>
  <line x1="283" y1="590" x2="297" y2="590" stroke="var(--text-tertiary)" stroke-width="1.5"/>
  <line x1="383" y1="590" x2="397" y2="590" stroke="var(--text-tertiary)" stroke-width="1.5"/>
  <line x1="483" y1="590" x2="497" y2="590" stroke="var(--text-tertiary)" stroke-width="1.5"/>
  <line x1="583" y1="590" x2="597" y2="590" stroke="var(--text-tertiary)" stroke-width="1.5"/>

  <!-- ── 8. LEGEND ── -->
  <text class="ts" x="45" y="612" opacity=".45">Legend —</text>

  <line x1="110" y1="609" x2="148" y2="609"
        stroke="var(--text-primary)" stroke-width="1.5" marker-end="url(#arr-call)"/>
  <text class="ts" x="154" y="613" opacity=".75">Synchronous call</text>

  <line x1="288" y1="609" x2="326" y2="609"
        stroke="var(--text-secondary)" stroke-width="1.5"
        stroke-dasharray="5 3" marker-end="url(#arr-ret)"/>
  <text class="ts" x="332" y="613" opacity=".75">Return message</text>

  <rect x="458" y="603" width="22" height="13" rx="2"
        fill="#FAEEDA" fill-opacity="0.5" stroke="#854F0B" stroke-width="0.75"/>
  <text class="ts" x="484" y="613" opacity=".75">alt fragment</text>

  <rect x="558" y="603" width="22" height="13" rx="2"
        fill="#E1F5EE" fill-opacity="0.6" stroke="#0F6E56" stroke-width="0.75"/>
  <text class="ts" x="584" y="613" opacity=".75">par fragment</text>

  <!-- Message group annotation -->
  <text class="ts" x="45" y="632" opacity=".35">
    ①–③ pre-condition  ·  ④–⑩ happy path  ·  ⑪–⑫ payment failure  ·  ⑬–⑭ item unavailable
  </text>

</svg>
```

## 自定义 CSS

在托管页面的 `<style>` 标签中添加这些类（在标准技能 CSS 之外）：

```css
/* ── Actor lifeline header boxes ── */
.actor       { fill: var(--bg-secondary); stroke: var(--text-secondary); stroke-width: 0.5; }
.actor-name  { font-family: system-ui, sans-serif; font-size: 11.5px; font-weight: 600;
               fill: var(--text-primary); }
.actor-colon { font-family: system-ui, sans-serif; font-size: 10px; fill: var(--text-tertiary); }

/* ── Lifeline dashed stems ── */
.lifeline { stroke: var(--text-tertiary); stroke-width: 1; stroke-dasharray: 6 4; fill: none; }

/* ── Activation bars ── */
.activation { fill: var(--bg-secondary); stroke: var(--text-secondary); stroke-width: 0.75; }

/* ── Message arrows ── */
.msg-call { stroke: var(--text-primary);   stroke-width: 1.5; fill: none; }
.msg-ret  { stroke: var(--text-secondary); stroke-width: 1.5; fill: none; stroke-dasharray: 6 3; }

/* ── Message labels ── */
.mlbl { font-family: system-ui, sans-serif; font-size: 11px; fill: var(--text-primary); }
.rlbl { font-family: system-ui, sans-serif; font-size: 11px; fill: var(--text-secondary);
        font-style: italic; }

/* ── Combined fragment: alt (amber) ── */
.frag-alt-bg  { fill: #FAEEDA; fill-opacity: 0.18; stroke: #854F0B; stroke-width: 1; }
.frag-alt-tag { fill: #FAEEDA; stroke: #854F0B; stroke-width: 0.75; }
.frag-alt-kw  { font-family: system-ui, sans-serif; font-size: 11px; font-weight: 700;
                fill: #633806; }
.frag-alt-div { stroke: #854F0B; stroke-width: 0.75; fill: none; }
.guard-lbl    { font-family: system-ui, sans-serif; font-size: 10.5px; font-style: italic;
                fill: #854F0B; }

/* ── Combined fragment: par (teal) ── */
.frag-par-bg  { fill: #E1F5EE; fill-opacity: 0.35; stroke: #0F6E56; stroke-width: 1; }
.frag-par-tag { fill: #E1F5EE; stroke: #0F6E56; stroke-width: 0.75; }
.frag-par-kw  { font-family: system-ui, sans-serif; font-size: 11px; font-weight: 700;
                fill: #085041; }
.frag-par-div { stroke: #0F6E56; stroke-width: 0.75; stroke-dasharray: 5 3; fill: none; }

/* ── Dark mode overrides ── */
@media (prefers-color-scheme: dark) {
  .actor       { fill: #2c2c2a; stroke: #b4b2a9; }
  .actor-name  { fill: #e8e6de; }
  .actor-colon { fill: #888780; }
  .frag-alt-bg  { fill: #633806; fill-opacity: 0.25; stroke: #EF9F27; }
  .frag-alt-tag { fill: #633806; stroke: #EF9F27; }
  .frag-alt-kw  { fill: #FAC775; }
  .frag-alt-div { stroke: #EF9F27; }
  .guard-lbl    { fill: #EF9F27; }
  .frag-par-bg  { fill: #085041; fill-opacity: 0.35; stroke: #5DCAA5; }
  .frag-par-tag { fill: #085041; stroke: #5DCAA5; }
  .frag-par-kw  { fill: #9FE1CB; }
  .frag-par-div { stroke: #5DCAA5; }
}
```

## 颜色规范

| 元素 | 颜色 | 原因 |
|------|------|------|
| 演员标题框 | 中性色（`var(--bg-secondary)`） | 仅用于结构展示，无语义含义——所有生命线采用相同风格 |
| 激活状态条 | 中性色（`var(--bg-secondary)`） | 用于显示执行时长，不添加具有语义意义的颜色 |
| 同步调用箭头 | `var(--text-primary)` + 实心三角形 | 箭头为主要交互方向，需高对比度显示 |
| 返回/虚线箭头 | `var(--text-secondary)` + 开放形箭头 | 返回为次要流程方向，对比度较低 |
| `alt`片段 | 橙黄色（`#FAEEDA` / `#854F0B`） | 表示警告或条件逻辑——与`c-amber`的语义含义对应 |
| 守卫条件文本 | 橙黄色斜体 | 在视觉上属于`alt`片段部分 |
| `par`片段 | 青色（`#E1F5EE` / `#0F6E56`） | 表示并行成功路径——与`c-teal`的语义含义对应 |
| `alt`分支分隔线 | 橙黄色实线 | 与`alt`框架颜色保持一致 |
| `par`分支分隔线 | 青色虚线 | 符合UML规范：`par`分支之间应使用虚线分隔 |

## 布局说明

- **视图框尺寸**：680×648（标准宽度；高度 = 生命线底部坐标590 + 图例 + 注释文字 + 16像素缓冲区）
- **生命线间距计算公式**：`(safe_area_width) / (n_lifelines − 1) = 600 / 5 = 120px`——但实际上从`x=90`开始设置`spacing = 100px`，这样第一个框的左侧边缘为40像素，最后一个框的右侧边缘恰好为640像素
- **演员标题框拆分标签技巧**：每个标题框使用两个独立的 `<text>` 元素——一个用于显示冒号（10像素，辅助颜色），另一个用于显示类名（11.5像素粗体，主色）——这样即便类名较长如“OrderController”，也不需要14像素的字体大小和超过150像素的宽度
- **五边形标签点计算公式**：对于从`(fx, fy)`位置开始的片段，其标签五边形的顶点坐标为`(fx,fy) (fx+w,fy) (fx+w+6,fy+6) (fx+w+6,fy+18) (fx,fy+18)`，其中`w`为关键词的近似文本宽度加上每侧8像素的边距
- **嵌套片段内边距设置**：`par`矩形区域的`x`坐标设为`alt_x + 15`，`y`坐标设为`alt_y_current + 2`，这样两个边框就能同时显示——内边距要足够以实现视觉分隔，但又不能过多以至于浪费垂直空间
- **激活状态条位置**：`x = lifeline_cx − 4`，`宽度 = 8`——位于生命线正中央，宽度足够窄，不会遮挡其背后的虚线部分
- **消息标签的Y轴偏移**：所有标签均置于`y = arrow_y − 5`的位置，刚好位于箭头线上方；这一规则适用于向左和向右的箭头，因为`text-anchor="middle"`会自动实现水平居中
- **进入激活状态条的返回箭头**：箭头的`x1/x2`端点应设在生命线中心（例如OrderController的x值为294），而非状态条边缘（x值为286）——这种轻微的重叠是刻意为之，有助于更清晰地标识目标对象
- **`alt`分支守卫标签位置**：第一个分支的守卫标签位于五边形标签右侧、`frame_top + 13`的位置；后续分支的守卫标签则位于`divider_y + 14`的位置，这样它们就会刚好处于新分支的内部
- **生命线末端标记样式**：使用`<line x1="cx−7" y1="590" x2="cx+7" y2="590" stroke-width="1.5"/>`——即一个简单对称的勾号，无需特殊标记即可实现相同效果
