# MQTT 发送工具

Commercial operator desk: dark header, card sidebar, monospace payload, Segoe MDL2 icon accents. Built for internal MQTT uplink simulation, not marketing screens.

## Overview

Internal Windows desktop client for 博享家 device uplink JSON. **主窗**：顶栏品牌 + 左栏连接/模版卡片（可滚动）+ 右栏多 Tab JSON 编辑 / 发送 / 日志。**模版管理**为独立 Toplevel 弹窗：左列表 + 右 JSON 编辑 + 操作记录。

## Colors

- **Canvas** (#EEF2F6): 主背景
- **Header Bg** (#0B1220): 顶栏
- **Header Fg** (#F8FAFC): 顶栏标题
- **Accent** (#2563EB): 主按钮、选中态、Tab 激活
- **Accent Soft** (#DBEAFE): 图标徽章底
- **Surface** (#FFFFFF): 卡片内容
- **Surface Alt** (#F8FAFC): 输入框、列表底
- **Border** (#E2E8F0): 分割线、边框
- **Text** (#0F172A): 正文
- **Muted** (#64748B): 副标题、标签
- **Success** (#059669): 保存/格式化成功
- **Error** (#DC2626): 未保存、JSON 无效
- **Code Bg** (#1E293B) / **Code Fg** (#CBD5E1): JSON 编辑器

## Typography

- **UI**: Segoe UI 10px（标签、按钮、列表）
- **UI Sm**: Segoe UI 9px（辅助说明）
- **Section**: Segoe UI 11px bold（区块标题）
- **Hero**: Segoe UI 20px bold（主窗标题）
- **Mono**: Cascadia Mono / Consolas 11px（JSON、日志）
- **Icons**: Segoe MDL2 Assets（`_icon_font` / `IC` 常量）

## Spacing

- **Base unit:** 8px
- **Root padding:** 20px horizontal, 18px vertical
- **Sidebar width:** 328px（`C["sidebar_w"]`）
- **Card padding:** 14–16px
- **Section head:** 12px bottom gap + 1px divider

## Window

| 窗口 | 默认几何 | 最小 | 初始化 |
|------|----------|------|--------|
| 主窗 | 1100×920（fallback） | 900×680 | `_fit_initial_window` 按内容 + 屏幕居中 |
| 模版管理 | 980×720 | 760×560 | 相对主窗居中，左侧列表区可滚动 |
| 运行日志 | 860×560 | 640×400 | 固定 |

## Components

### Header（主窗 / 弹窗）

- 高度 56–92px；深色底 + 底部 accent 线 2–3px
- 左侧：28–46px 圆角徽章 + 标题 + 副标题
- 独立子窗：右侧「收回主界面」outline 按钮

### Cards（`_card`）

- 1px 边框 shell + 白底 inner；`accent=True` 时左边 3px 蓝色强调
- 用于连接、模版、payload、日志区

### Buttons（`_flat_btn`）

- **primary**: 蓝底白字（发送、应用、保存）
- **secondary**: 浅底描边
- **outline**: 白底蓝字
- **ghost**: 无底色（删除、撤销）
- 支持 `icon=` Segoe MDL2 前缀

### Sidebar（主窗）

- 连接卡片 + 模版卡片，整栏 `_scrollable_frame` 可纵向滚
- 模版行：Combobox +「应用到当前窗口」+ 新增 / 管理

### Payload Tabs

- Tab 栏：激活态白底蓝字；✎ 重命名、× 关闭；`+` 新建；拖拽分离
- 每 Tab：`tk.Text` 无 wrap + 双滚动条；下方 JSON 状态 pill
- 450ms debounce 自动格式化

### Template Manager（Toplevel）

| 区域 | 规格 |
|------|------|
| 左栏 | 宽 280px；搜索框；Listbox + 滚动条；模版计数；新建/窗口保存/应用/重命名/删除 |
| 右栏 JSON | 深色 code 编辑器；双滚动；`Ctrl+A/C/V/X/Z/Y` + 右键菜单 |
| 保存行 | 「保存右侧编辑」「放弃未保存」+ 状态文案 |
| 操作记录 | Listbox height=4；「回撤选中记录」；双击记录可回撤 |
| 行为 | 粘贴后立即 JSON indent=2；切换模版才弹未保存；两 Listbox 均 `exportselection=False` |

### Log

- 主窗内嵌 height=6，`wrap=WORD`，纵向滚动条
- 搜索 +「放大查看」打开 `LogViewerDialog`

### Checkboxes

- 自动 muid + sign；触发时间取当前；sn 跟随主题（默认开）
- 密码「显示」Checkbutton

## Do's and Don'ts

- **Do** 主窗/模版弹窗启动后 `after_idle` 适配尺寸，小屏靠滚动条暴露更多内容
- **Do** JSON 区用等宽字体；粘贴进模版编辑器后自动格式化
- **Do** 模版管理保存只读右侧 editor 内容，勿与「从当前窗口保存」混淆
- **Do** 操作记录回撤前 `askyesno` 确认
- **Don't** 在 `tk.Frame(..., pady=(0,n))` 写 tuple — 用 `pack(pady=...)`
- **Don't** 多个 Listbox 共用默认 `exportselection=True`
- **Don't** 点击 JSON 编辑器时把左侧模版失选当作切换模版
- **Don't** 提交 broker 口令或写进 `history.json`
