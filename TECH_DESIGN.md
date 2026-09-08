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
| 打包 | PyInstaller，入口 `mqtt_gui.py`，产物名 `mqtt_tool_v5` |
| 运行环境 | Windows 10+ |

不引入 Web 框架、不引入 Qt。

## 目录结构

```
mqtt-python/
  mqtt_gui.py          # GUI 入口
  mqtt_publish.py      # Mqttpub 短连接发布
  md5tool.py           # md5sign
  mqtt_tool_v5.spec    # 当前打包
  templates.json       # 运行时模版（exe 旁或源码旁）
  history.json         # 连接历史
  mqtt_publish_old.py  # 旧脚本，勿当主路径
  md5toolold.py
  mqtt_tool*.spec      # 历史 spec
  build/ dist/         # 打包产物
```

主路径只改：`mqtt_gui.py`、`mqtt_publish.py`、`md5tool.py`。

## 数据与接口约定

### 报文

JSON 对象，常见字段：`name`、`sn`、`muid`、`timestamp`、`version`、`data`、`sign`，banner 另有 `operator`。

### `md5sign(value: dict) -> str`

1. `timestamp = str(int(time.time() * 1000 - 1000 * 60 * 4))` 写入 `value`
2. 顶层 `dict(sorted(items))`
3. `json.dumps(..., ensure_ascii=False, separators=(',', ':'))`
4. UTF-8 MD5 hex

发送前若勾选自动签名：先 `pop('sign')`，再写 `muid`，再 `md5sign`。

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

单窗体 `MqttToolApp`，无多页。分区：连接行 → 主题 → 模版行 → payload → 选项+发送 → 日志。

## 关键技术方案

| 点 | 决策 | 回退 |
|----|------|------|
| 签名偏移 4 分钟 | 对齐现网，禁止改默认 | 仅当服务端规则变更 |
| UI 线程 | 发送进 daemon Thread，结果 `root.after` | 禁止在主线程 `connect` |
| sn ↔ topic | 主题 `rsplit('/', 1)` 末段 | 无 `/` 则整段当 sn |
| 打包 | `console=False` | 调试可临时 `True` |

## 多端/环境差异说明

- 仅桌面；无 H5 / 小程序
- 测试 broker 与账号由使用者填写，不写进仓库

## 常见问题与排查

- 连接失败：Host/端口/账号、防火墙、1883
- 设备不认：签名未勾选、JSON 手改后 key 顺序、timestamp 偏移被改
- exe 丢模版：`templates.json` 不在 exe 同目录
- 主题错设备：未开「模版 sn 跟随主题」，或 payload.sn 与主题末段不一致
