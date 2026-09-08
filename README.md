# MQTT 发送工具

## 说明

Windows 桌面客户端：向 MQTT broker 发送博享家设备上行 JSON（自动 `muid` + `sign`）。Python 3 + Tkinter + paho-mqtt。

## 如何运行

**推荐（自动装环境）：**

```
setup.bat    # 首次：检测 Python、创建 .venv、安装依赖
run.bat      # 启动 GUI（无 .venv 会先 setup）
dev.bat      # 开发模式：改 *.py 自动重启窗口
build.bat    # 打包 exe
```

**手动：**

1. 安装 Python 3（带 Tcl/Tk）
2. `pip install -r requirements.txt`
3. `python mqtt_gui.py`

## 主要功能

| 功能 | 说明 |
|------|------|
| 连接与发送 | Host / Port / User / Password / Topic；后台线程 publish |
| 多 Tab | 多个 JSON 窗口；重命名；拖拽分离；独立窗收回主界面 |
| 模版 | 侧栏快选；**管理**弹窗内搜索、编辑、保存、操作记录回撤 |
| 签名 | 自动 `muid` + `md5sign`；通道告警触发时间可选当前 |
| 历史 | Host/Port/User/Topic 下拉历史（不含密码） |

## 模版管理弹窗

- 左侧：模版列表 + 搜索
- 右侧：JSON 编辑（粘贴自动格式化）；**保存右侧编辑**
- 底部：操作记录，选中后 **回撤选中记录**（或双击记录）

## 打包

```
build.bat
```

或：`pyinstaller mqtt_tool_v5.spec`

产物在 `dist\mqtt_tool_v5.exe`。有根目录 `templates.json` 时会拷到 `dist\`。`history.json` 首次使用后生成。

## 目录摘要

| 路径 | 作用 |
|------|------|
| `mqtt_gui.py` | GUI 入口 |
| `mqtt_publish.py` | 短连接 publish |
| `md5tool.py` | `md5sign` |
| `setup_env.py` / `setup.bat` | 虚拟环境与依赖 |
| `run.bat` / `dev.bat` / `build.bat` | 运行 / 热重载 / 打包 |
| `dev_reload.py` | 文件监听重启 |
| `requirements.txt` | 运行时依赖 |
| `mqtt_tool_v5.spec` | PyInstaller |
| `templates.json` | 报文模版 |
| `history.json` | 连接历史 |
| `DESIGN.md` | UI 规范 |
| `TODO.md` | 任务进度 |

## 规范摘要

- 详细规则见 `AGENTS.md`
- 改界面先读 `DESIGN.md`
- 禁止把 broker 口令提交进 git

## 文档索引

- `RESEARCH.md`
- `PRD.md`
- `TECH_DESIGN.md`
- `DESIGN.md`
- `TODO.md`
