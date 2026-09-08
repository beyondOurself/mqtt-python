# MQTT 发送工具

## 说明

Windows 桌面客户端：向 MQTT broker 发送博享家设备上行 JSON（自动 `muid` + `sign`）。Python 3 + Tkinter + paho-mqtt。

## 如何运行

1. 安装 Python 3（带 Tcl/Tk）
2. `pip install paho-mqtt`
3. 在仓库根目录：`python mqtt_gui.py`
4. 填写 Host / Port / User / Password / 主题，选模版，点发送

打包：

```
pyinstaller mqtt_tool_v5.spec
```

把 `templates.json` 放到 exe 同目录。`history.json` 会在首次使用后生成。

## 目录摘要

| 路径 | 作用 |
|------|------|
| `mqtt_gui.py` | GUI 入口 |
| `mqtt_publish.py` | 短连接 publish |
| `md5tool.py` | `md5sign` |
| `mqtt_tool_v5.spec` | PyInstaller |
| `templates.json` | 报文模版（运行时） |
| `history.json` | 连接历史（不含密码） |
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
