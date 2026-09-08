# 进度清单（唯一事实源）

> 用于跟踪本项目可执行任务的当前状态与流转，作为跨设备协作的统一进度面板。
> 与 PRD.md（需求范围）、RESEARCH.md（结论依据）、TECH_DESIGN.md（技术方案）、AGENTS.md（长期规范）联动，保障执行与目标一致。
> 仅记录任务项与状态变化，**不存放方案长文、调研细节与规范正文**。

## 使用规则

- 状态分区固定：`进行中`、`待开发`、`阻塞`、`已完成`
- 标题格式：`项目-类型-序号 + 动词 + 结果`
- 类型：`M` 业务 / `C` 组件 / `S` 样式 / `I` 工程 / `D` 文档
- 每条至少含：`范围`、`验收`
- 任务来源可追溯到 `PRD.md` + `TECH_DESIGN.md`

## 进行中

（无）

## 待开发

- [ ] MQTT-I-001 补依赖清单并去掉源码预填口令
  - 范围：`mqtt_gui.py` `mqtt_publish.py` `md5tool.py`（新增 `requirements.txt`）
  - 验收：Password 启动为空；文档与代码无真实口令；`pip install -r requirements.txt` 后能开 GUI

- [ ] MQTT-M-001 支持订阅回显
  - 范围：`mqtt_gui.py` `mqtt_publish.py`
  - 验收：可选订阅当前主题，入站 JSON 进日志

- [ ] MQTT-M-002 可选 QoS 与 TLS
  - 范围：`mqtt_publish.py` `mqtt_gui.py`
  - 验收：明文 1883 仍为默认；勾选 TLS 后能连测试 broker

## 阻塞

（无）

## 已完成

- [x] MQTT-M-000 实现 GUI 发布与模版
  - 范围：`mqtt_gui.py`
  - 验收：模版 CRUD、自动签名、触发时间、sn 跟随主题、历史、日志

- [x] MQTT-D-001 按 vibe-coding 落盘项目文档
  - 范围：`RESEARCH.md` `PRD.md` `TECH_DESIGN.md` `AGENTS.md` `DESIGN.md` `README.md` `TODO.md` `.cursorignore`
  - 验收：根目录 8 份文件齐，且与现有 GUI 行为一致

- [x] MQTT-M-010 实现短连接发布
  - 范围：`mqtt_publish.py`
  - 验收：publish 成功或 8s 超时抛错

- [x] MQTT-M-011 实现 md5sign
  - 范围：`md5tool.py`
  - 验收：发出报文含 timestamp 与 sign

- [x] MQTT-I-000 提供 v5 无控制台打包
  - 范围：`mqtt_tool_v5.spec`
  - 验收：`pyinstaller mqtt_tool_v5.spec` 产出无黑框 exe

## 变更记录（近 7 天）

- 2026-09-08：初始化 vibe-coding 文档；MQTT-D-001 完成；短连接任务号改为 MQTT-M-010
