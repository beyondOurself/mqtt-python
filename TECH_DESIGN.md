# 技术设计

> 用于定义本项目“怎么实现”的技术方案、架构约束、依赖选型与实现边界。
> 与 PRD.md（需求目标）、RESEARCH.md（方案依据）、TODO.md（执行任务）联动，作为研发实现与评审的技术基线。
> 仅记录可复用的技术决策与实现边界，**不存放临时排障记录和日常进度状态**。

## 文档协作约束

- 与 PRD 的 MVP 范围一致
- 与 TODO 建立任务映射

## 技术栈

| 项 | 选型 |
|----|------|
| 语言 | Python 3 |
| UI | Tkinter + ttk |
| MQTT | paho-mqtt（`paho.mqtt.client`） |
| 签名 | 标准库 `hashlib.md5` |
| 打包 | PyInstaller 单文件，`build_release.py` 驱动；产物 `MQTT发送工具_{major}.{minor}.{patch}.{build}.exe` |
| 运行环境 | Windows 10+ |

不引入 Web 框架、不引入 Qt。

## 目录结构

```
mqtt-python/
  mqtt_gui.py          # GUI 入口（主窗 + 模版管理弹窗 + 日志查看）
  mqtt_publish.py      # Mqttpub 短连接发布
  md5tool.py           # md5sign
  setup_env.py         # 虚拟环境检测 / 依赖安装 / 校验
  setup.bat            # 一键初始化（含 winget 装 Python）
  run.bat              # 无 .venv 时先 setup，再启动 GUI
  dev.bat              # 开发热重载（dev_reload.py）
  dev_reload.py        # 监听 *.py 变更并重启窗口
  build.bat            # 安装 dev 依赖 + 调用 build_release.py
  build_release.py     # bump build、生成 version_info、PyInstaller、拷 dist 资源
  app_version.py       # 版本读写与格式化（GUI 标题 / exe 基名）
  version.json         # 软件版本源（build 每次打包 +1）
  requirements.txt     # 运行时依赖（paho-mqtt）
  requirements-dev.txt # 打包依赖（pyinstaller）
  templates.json       # 运行时模版（exe 旁或源码旁）
  history.json         # 连接历史
  session.json         # 会话状态（含密码，勿提交 git）
  version_info.txt     # 构建时生成（gitignore）
  .build_out.txt       # 构建产物路径（gitignore）
  build/ dist/         # 打包产物
```

主路径只改：`mqtt_gui.py`、`mqtt_publish.py`、`md5tool.py`。

## 数据与接口约定

### 报文

JSON 对象，常见字段：`name`、`sn`、`muid`、`timestamp`、`version`、`data`、`sign`，banner 另有 `operator`。

### `md5sign(value: dict, offset_ms: int = 0) -> str`

1. `timestamp = str(int(time.time() * 1000 + offset_ms))` 写入 `value`
2. 顶层 `dict(sorted(items))`
3. `json.dumps(..., ensure_ascii=False, separators=(',', ':'))`
4. UTF-8 MD5 hex

发送前若勾选自动签名：先 `pop('sign')`，再写 `muid`，再 `md5sign(..., offset_ms)`；GUI「timestamp 偏移(分钟)」×60000 为 `offset_ms`。

### 发布

`Mqttpub(host, topic, port).clicent_main(message, user, pwd)`：

- `Client()` + `username_pw_set` + `connect` keepalive 60
- `publish` 后 `loop` 最多 8s，未 `is_published` 则抛错
- 短连接：发完 `disconnect`

### 落盘

| 文件 | 内容 |
|------|------|
| `templates.json` | `{ 模版名: payload对象 }` |
| `history.json` | `{ host, port, user, topic: string[] }` 每键最多 50 |

路径：`sys.frozen` 时为 exe 目录，否则为源码目录。缺文件时 GUI 用内置 `TEMPLATES` / 默认 host 列表。

## 路由与页面结构

- **主窗体** `MqttToolApp`：顶栏品牌区 + 左侧连接/模版侧栏（可滚动）+ 右侧多 Tab payload / 发送选项 / 日志
- **模版管理** `TemplateManagerDialog`（Toplevel）：左列表 + 右 JSON 编辑 + 操作记录；`grab_set` 模态
- **运行日志** `LogViewerDialog`（Toplevel）：全文搜索与放大查看
- **独立窗口**：Tab 拖拽分离为子 `MqttToolApp(parent_app=...)`，标题栏「收回主界面」合并 Tab 回父窗

## 模版管理弹窗（TemplateManagerDialog）

| 区域 | 行为 |
|------|------|
| 模版列表 | 搜索过滤；双击应用；`exportselection=False` 避免与操作记录列表抢选中 |
| JSON 编辑 | 可编辑；`Ctrl+A/C/V/X/Z/Y` + 右键菜单；粘贴后 `_format_preview_json` 立即 indent=2 |
| 保存 | 「保存右侧编辑」读 `preview.get("1.0","end-1c")` 写回 `templates.json` |
| 操作记录 | 内存栈最多 50 条（新建/保存/窗口保存/重命名/删除）；选中后「回撤选中记录」恢复 `before` 快照 |
| 未保存提示 | 仅**切换到其他模版**时弹窗；点右侧编辑器不失选左侧项（`_restore_list_selection`） |
| 初始化尺寸 | `after_idle(_fit_initial_window)` 按 `winfo_reqwidth/height` 适配并相对主窗居中 |

## 多 Tab 与窗口分离

- `PayloadTab`：每 Tab 独立 JSON 编辑器，450ms debounce 自动格式化
- Tab 栏：重命名（✎）、关闭（×）、右键菜单、拖拽分离
- `_detach_tab`：新建 Toplevel + 子 `MqttToolApp`，继承连接参数
- `_dock_to_parent`：子窗 Tab 合并回父窗；`_close_child_app` 关闭前可选收回

## 滚动与窗口适配

- `_scrollable_frame(parent, width)`：Canvas + 内层 Frame + 纵向滚动条；鼠标进入绑定 `<MouseWheel>`
- 主窗侧栏、模版管理左侧列表区使用可滚动容器
- 主窗 / 模版弹窗均在 UI 构建完成后 `after_idle` 调用 `_fit_initial_window`

## 环境初始化

| 脚本 | 作用 |
|------|------|
| `setup.bat` | `chcp 65001`；检测 `py`/`python`；无则 winget 装 Python 3.12；调用 `setup_env.py --install` |
| `setup_env.py` | 创建 `.venv`；`pip install -r requirements.txt`；校验 tkinter / paho-mqtt / `md5tool` / `mqtt_publish` |
| `run.bat` | 无 `.venv` 则 `setup.bat nopause`，再 `.venv\Scripts\python mqtt_gui.py` |
| `dev.bat` | 同上，运行 `dev_reload.py` 热重载 |
| `build.bat` | 装 `requirements-dev.txt` 后执行 `build_release.py` |

### 版本与打包

**版本文件** `version.json`：

```json
{ "major": 1, "minor": 0, "patch": 0, "build": 0 }
```

| 字段 | 维护方式 |
|------|----------|
| `major` / `minor` / `patch` | 发版前手动改 |
| `build` | `build_release.py` 每次打包前 `+1` 并写回 |

**命名**：`app_version.format_full()` → `1.0.0.15`；exe 基名 `MQTT发送工具_1.0.0.15`。

**`build_release.py` 流程**：

1. `bump_build(version.json)`
2. 生成 `version_info.txt`（Windows 属性：FileVersion / ProductVersion）
3. `PyInstaller --windowed --onefile --name {exe_basename} --version-file version_info.txt mqtt_gui.py`
4. 拷贝 `templates.json`、`version.json` 到 `dist\`
5. 写入 `.build_out.txt`（完整 exe 路径）

**运行时读版本**：`app_version.load_version_data()` 优先 exe 同目录 `version.json`，否则源码目录；`mqtt_gui.py` 标题栏显示 `v{major}.{minor}.{patch}.{build}`。

**注意**：报文 JSON 内的 `version` 字段（如 `v2.0.0_1`）为**设备协议版本**，与软件 `version.json` 无关。

**模块导入约束**：`md5tool.py` 顶层禁止 import `requests` / `paho`（仅 `__main__` 块可用），否则 `setup_env.py` 校验失败。

## Tkinter 布局注意

- `tk.Frame` 的 `padx`/`pady` **不支持** tuple（如 `pady=(0,16)`），须写在 `frame.pack(pady=(0,16))` 上；否则 TclError 导致弹窗初始化中断、列表未加载
- 多个 `Listbox` 并存时设 `exportselection=False`，避免 Windows 下选中态互抢

## 关键技术方案

| 点 | 决策 | 回退 |
|----|------|------|
| 签名 timestamp | 默认当前毫秒；GUI 可填偏移分钟 | 旧行为填 `-4` |
| UI 线程 | 发送进 daemon Thread，结果 `root.after` | 禁止在主线程 `connect` |
| sn ↔ topic | 主题 `rsplit('/', 1)` 末段 | 无 `/` 则整段当 sn |
| 打包 | `console=False` | 调试可临时 `True` |

## 多端/环境差异说明

- 仅桌面；无 H5 / 小程序
- 测试 broker 与账号由使用者填写，不写进仓库

## 常见问题与排查

- 连接失败：Host/端口/账号、防火墙、1883
- 设备不认：签名未勾选、JSON 手改后 key 顺序、timestamp 偏移被改
- exe 丢模版 / 标题版本不对：`templates.json`、`version.json` 须在 exe 同目录（`build_release.py` 会自动拷到 dist）
- 主题错设备：未开「模版 sn 跟随主题」，或 payload.sn 与主题末段不一致
- 模版管理列表空白：检查弹窗是否 TclError（Frame 非法 pady）；或 `_reload_list` 是否在 UI 建完前被中断
- 操作记录点不中：确认 `op_list` 与模版 `listbox` 均已 `exportselection=False`
- 环境 setup 报 `No module named requests`：检查 `md5tool.py` 是否有多余顶层 import
