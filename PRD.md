# 产品需求文档（PRD）

> 用于定义本项目“要做什么、为谁做、做到什么程度”的产品目标与范围基线。
> 与 RESEARCH.md（调研依据）、TECH_DESIGN.md（技术落地方案）、TODO.md（执行进度）联动，作为需求评审与范围控制的统一依据。
> 仅记录稳定需求与验收边界，**不存放实现细节、临时讨论和日常任务流转**。

_版本：v1.0_
_更新日期：2026-09-08（版本自增打包、模版管理弹窗、多窗口、环境脚本）_
_产品负责人：内部联调_

## 文档协作与交付约束

- MVP/迭代条目拆到 `TODO.md`
- 变更顺序：先改 PRD，再同步 TECH_DESIGN 与 TODO
- 界面规范见根目录 `DESIGN.md`

## 一、项目背景及目标

内部 Windows 桌面工具，模拟设备向 MQTT broker 发送博享家协议 JSON（含 `muid`、`timestamp`、`sign`），服务 GIS / 云端 / App 联调。

## 二、目标用户

- 后端 / GIS / 客户端联调人员
- 需伪造通道告警、心跳、校时、banner 等上行报文的测试同学

## 三、需求范围及版本规划

### MVP（已落地）

- 填写 Host / Port / User / Password / Topic
- 模版选择、保存 / 另存为 / 重命名 / 删除
- **模版管理弹窗**：列表搜索、右侧 JSON 可编辑保存、粘贴即格式化、操作记录与回撤
- JSON 编辑与发送（多 Tab，可重命名、拖拽分离、独立窗口收回主界面）
- 发送前自动 `muid` + `sign`
- 通道告警 `triggerInduction` / `triggerWarning` 可取当前时间
- 模版 `sn` 可跟随主题末段；payload 改 `sn` 可回写主题
- Host / Port / User / Topic 历史（最多 50 条）
- 发送日志（内嵌滚动条、放大查看）
- 启动时窗口按内容自适应尺寸；侧栏可滚动
- 一键环境初始化（`setup.bat` / `run.bat` / `dev.bat` / `build.bat`）
- PyInstaller 无控制台 exe；**四段式版本号**，每次构建 build 自增

### 后续

- 启动不预填口令；口令不进 git
- `requirements.txt` 与运行说明
- 订阅同一 topic 看回包
- TLS / QoS 可配

## 四、详细功能列表

| 功能 | 说明 | 验收 |
|------|------|------|
| 连接参数 | Host、Port、User、Password | Port 非数字拦截；Host/主题空则不发 |
| 密码显示 | 复选框切换明文 | 默认掩码 |
| 模版 | 内置 timing / heartBeat / channelPersonAlert / banner / delBanner | 切模版刷新 JSON |
| 模版 CRUD | 保存到 `templates.json` | 至少保留 1 个模版 |
| 模版管理弹窗 | 左侧列表 + 搜索；右侧 JSON 编辑；底部操作记录 | 打开即见全部模版；保存右侧编辑；可回撤 |
| 多窗口 Tab | 新建 / 重命名 / 关闭 / 拖拽分离 / 收回主界面 | 分离后独立窗口；关闭时可合并回主窗 |
| 自动签名 | 勾选后发送前 `uuid1` + `md5sign` | 发出 JSON 含 `sign`、`timestamp` |
| 触发时间 | 勾选则改 `data` 内两触发字段 | 格式 `YYYY-MM-DD HH:mm:ss` |
| sn 同步 | 主题末段 ↔ payload.sn | 双向 |
| 历史 | `history.json`，可删单条/清空 | 不含密码 |
| 发送 | 后台线程 `publish`，超时 8s | 成功/失败写日志，按钮恢复 |
| 打包 | `build.bat` → 自增 build → `MQTT发送工具_x.y.z.n.exe` | 无黑框；dist 含 `version.json` |

## 五、用户体验与设计规范

可执行视觉规范见 `DESIGN.md`。主窗口启动时按内容自适应尺寸并居中；侧栏与日志区可滚动；payload 等宽字体；发送时按钮禁用。模版管理弹窗同样启动自适应，JSON 粘贴后自动格式化。

## 六、技术与数据要求

- Python 3 + Tkinter + paho-mqtt
- 签名：顶层 key 排序后紧凑 JSON，UTF-8 MD5；`timestamp` 默认当前毫秒，GUI 可按分钟增减偏移
- 发出 JSON：`ensure_ascii=False`，`separators=(',', ':')`
- 主题惯例：`cloud/{sn}`

## 七、边界与限制

- 不实现 MQTT 订阅、遗嘱、集群管理
- 不替代 MQTTX
- 不提交真实环境口令、证书
- 不保证非 Windows 外观

## 八、非功能性需求

- 发送不卡死 UI（线程）
- 连接失败 / 未发出须可读错误
- 冻结 exe 时模版/历史在 exe 同目录

## 九、里程碑与进度

见 `TODO.md`。

## 十、后续规划

订阅回显、TLS、QoS、口令外置配置。
