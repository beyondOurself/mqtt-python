# AGENTS

> 用于约定本项目长期适用的**开发规范、流程约束、协作规则**等基础原则。
> 与 RESEARCH.md（方案/结论沉淀）、TODO.md（执行性业务进度）联动，为所有新功能、代码实现和任务协作提供统一的团队“工作基线”。
> 仅记录项目长期约束和反复复用的标准，**不存放临时方案、日常进度、讨论记录**。

## 项目概述

- 项目：MQTT 发送工具（`mqtt-python`）
- 形态：Python + Tkinter 桌面客户端，模拟博享家设备 MQTT 上行
- 发布：源码运行或 PyInstaller 单文件 exe（Windows）

## 开发规范

- 默认最小改动；优先改用户指定路径；不扩散无关重构。
- 主路径：`mqtt_gui.py`、`mqtt_publish.py`、`md5tool.py`。勿把新逻辑堆进 `mqtt_publish_old.py` / `md5toolold.py`。
- Windows：Shell 用 PowerShell；路径用完整 Windows 路径或仓库相对路径。
- 禁止提交 broker 口令、证书、`.env`。Password 不得写入 `history.json`，不得写进文档示例。
- `md5sign` 的 timestamp 偏移（−4 分钟）与排序+紧凑 JSON 规则禁止无需求改动。
- **环境**：优先 `run.bat` / `dev.bat`；改依赖同步 `requirements.txt` 与 `setup_env.py` 校验项。
- **Tkinter**：`Frame` 勿用 tuple 作 `padx`/`pady` 构造参数；多 `Listbox` 设 `exportselection=False`。
- **模版弹窗**：保存右侧 JSON 与「从当前窗口保存」语义分离；切换模版才提示未保存。

## UI 与 DESIGN.md（强制）

- 根目录 **`DESIGN.md`** 为本项目 **UI 设计规范** 的单一事实来源（色板、字号、间距、组件形态、Do/Don't）。
- **生成或修改窗口、控件、样式前须先阅读并严格遵守 `DESIGN.md`**；禁止自创与规范冲突的配色或布局。
- 结构对齐 [getdesign.md — What is DESIGN.md?](https://getdesign.md/what-is-design-md)。
- 无 `DESIGN.md` 不得盲改界面。

## 文档协作规范（vibe-coding-new-project）

- 文档顺序：`RESEARCH.md` -> `PRD.md` -> `TECH_DESIGN.md` -> `AGENTS.md` -> `TODO.md`
- 需求变更先改 PRD/RESEARCH；方案变更改 TECH_DESIGN；规则沉淀改 AGENTS；视觉改 DESIGN.md；进度只写 TODO.md。

## 跨设备开发流程（强制）

- 开发前先读 `TODO.md`
- 以 `TODO.md` 作为任务状态单一事实来源

## 代码风格

- 缩进 4 空格（与现有 Python 文件一致）
- 新函数保持现有命名（如已有拼写 `clicent_main` 不要无需求改名）
- 注释只写非显而易见的协议约束

## 提交规范（强制中文）

- 描述内容中文为主，不要英文
- 采用「类型(范围): 内容摘要」方式（[Conventional Commits](https://www.conventionalcommits.org/zh-hans/v1.0.0/)）
- 类型：`feat` / `fix` / `docs` / `style` / `refactor` / `perf` / `test` / `chore`
- 单次提交聚焦单一改动
- 严禁 `fix: .`、`update`、`修改文件` 等笼统描述

## 测试与发布

- 改发送/签名后：用测试 broker 发一条 `heartBeat` 或 `channelPersonAlert`，日志出现「发送成功」
- 改 UI 后对照 `DESIGN.md`；主窗与模版管理弹窗启动应显示完整或可见滚动条
- 改模版管理后：列表有数据、粘贴 JSON 自动格式化、操作记录可选中回撤
- 密钥与口令不可提交
- 打包：双击或执行 `build.bat`（内部调用 `pyinstaller mqtt_tool_v5.spec`），将 `templates.json` 放 exe 同目录

## 注意事项

- GUI 发送必须后台线程 + `root.after` 回主线程
- 冻结目录用 `_app_dir()`，禁止写死 `C:\` 路径
- 至少保留一个模版
