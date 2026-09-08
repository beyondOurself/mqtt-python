# MQTT 发送工具

Utilitarian lab bench: dense controls, monospace payload, system chrome. Built for operators who send device MQTT all day, not for marketing screens.

## Overview

Internal Windows desktop client for simulating 博享家 device uplink JSON. Layout is a single stacked form: connection strip, topic, template, JSON editor, send options, log. Visual language follows stock ttk on Windows so it sits next to MQTTX and IDEs without a custom skin. Depth is flat: padding and grouping, not drop shadows. Primary accent is reserved for the Send action. Payload and log are the working surfaces; labels stay mute gray-blue.

## Colors

- **Primary** (#0078D4): Send button emphasis if ttk themed; Windows accent equivalent
- **Secondary** (#605E5C): Secondary actions (删 / 保存 / 另存为 / 重命名)
- **Tertiary** (#107C10): Success log line intent (发送成功)
- **Background** (#F3F3F3): Window / ttk Frame default
- **Surface** (#FFFFFF): Combobox, Entry, Text editors
- **Text** (#1A1A1A): Labels and body
- **Muted** (#605E5C): Secondary labels (Host, Port, 主题, 模版)
- **Success** (#107C10)
- **Warning** (#9D5D00)
- **Error** (#C42B1C): 发送失败, JSON 无效, messagebox error
- **Info** (#0078D4)
- **Log Bg** (#FFFFFF)
- **Payload Fg** (#1A1A1A)

## Typography

- **Headline Font**: Segoe UI
- **Body Font**: Segoe UI
- **Mono Font**: Consolas

- **Display**: unused. No marketing hero.
- **Headline**: Segoe UI 11px/400. Window title is system "MQTT 发送工具".
- **Subhead**: unused. Sections use 9–10px labels, not titles.
- **Body Large**: unused.
- **Body**: Segoe UI 9px/400, 1.3 line height. Labels, buttons, checkboxes.
- **Body Small**: Segoe UI 8px/400. Optional helper; prefer none.
- **Caption**: Segoe UI 8px/400. Log timestamps if added later.
- **Overline**: unused.
- **Code**: Consolas 10px/400, 1.4 line height. Payload Text only.

## Spacing

- **Base unit:** 8px
- **Scale:** 4, 8, 12, 16, 24, 32
- **Component padding:** root Frame `padding=10`; row gaps `pady=(8, 0)`; label-to-field `padx=(8, 4)`
- **Section spacing:** 8px between stacked rows; payload expands; log height 8 lines
- **Window:** default `920x760`, minsize `760x580`

## Border Radius

Tk/ttk native. Do not draw custom CSS radii.

- **None:** 0px — window chrome
- **Small:** system ttk — buttons, combobox
- **Medium:** unused custom
- **Large:** unused
- **XL:** unused
- **Full:** unused (no pills)

## Elevation

Flat ttk. No custom shadows.

- **Subtle:** grouping by 8px vertical gap, not cards
- **Medium:** native Entry/Text sunken border only
- **Large:** unused
- **Overlay:** system `messagebox` / `simpledialog` only
- **Focus Ring**: native ttk focus; do not paint extra rings

## Components

### Buttons
**Primary (Filled)** — Send：`ttk.Button` 右对齐，文案「发送」；发送中 `state=DISABLED`，完成后恢复
**Secondary** — 模版「保存 / 另存为 / 重命名 / 删除」：同一行、左起、间距 4px
**Ghost** — 历史「删」：`width=3`，贴在 Combobox 右侧
**Destructive** — 删除模版走 `askyesno`，按钮本身仍是 Secondary，不单独红底
- **Sizes**: 跟随 ttk；删钮固定宽 3 字符
- **Disabled**: Send 发送期间禁用

### Cards
**Default** — 无卡片。整窗一个 `ttk.Frame`
**Elevated** — unused

### Inputs
**Text Input** — Host/Port/User：`ttk.Combobox`；Password：`ttk.Entry(show="*")`；Topic：`ttk.Combobox` 可编辑
- **Label**: 左置 Segoe UI，与控件同一行
- **Helper text**: 无；错误进底部日志
**Payload** — `tk.Text` `wrap=NONE`，Consolas 10，垂直滚动条，`undo=True`
**Log** — `tk.Text` height=8，`wrap=WORD`，`state=DISABLED`，仅 `_append_log` 写入

### Chips
**Filter Chip** — unused
**Status Chip** — unused；状态只写日志文案

### Lists
**Default List Item** — Combobox 下拉历史，最多 50；右键「删除此项 / 清空历史」

### Checkboxes
`ttk.Checkbutton`：显示密码；发送前自动 muid + sign（默认开）；触发时间取当前（默认开）；模版 sn 跟随主题（默认开）。与按钮同一 `act` 行，间距 12px。

### Radio Buttons
unused

### Tooltips
unused；错误用 `messagebox.showerror`

### Window
title `MQTT 发送工具`；几何 `920x760`；minsize `760x580`

## Do's and Don'ts

- **Do** keep connection fields on one row so operators can tab Host → Port → User → Password.
- **Do** use Consolas 10 for payload; JSON is the product.
- **Do** disable Send while the background publish thread runs.
- **Do** put failures in the log with `发送失败:` prefix; keep the form filled.
- **Do** mask password by default; 「显示」 is opt-in.
- **Don't** wrap the window in a dark dashboard or web-like card grid.
- **Don't** use MarketNest terracotta, rounded-full CTAs, or drop shadows.
- **Don't** put password into history dropdowns or screenshots in docs.
- **Don't** add a second window for templates; CRUD stays on the template row.
- **Don't** shrink payload to a single-line Entry; it must remain the expanding editor.
