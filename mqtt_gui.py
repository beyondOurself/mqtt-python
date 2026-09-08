import copy
import json
import os
import sys
import threading
import time
import tkinter as tk
import uuid
from tkinter import messagebox, simpledialog, ttk

from md5tool import md5sign
from mqtt_publish import Mqttpub

DEFAULT_TEMPLATE = "channelPersonAlert"

TEMPLATES = {
    "timing (DJ0GLJ04E8A9DETA)": {
        "data": {"time": "2025-01-22 14:37:18", "status": 0},
        "muid": "892154e3c425-97b6-4ce5-b0e2-c81c69b8b3bc",
        "name": "timing",
        "sn": "DJ0GLJ04E8A9DETA",
        "timestamp": "1737517038540",
        "version": "v2.1.1_1",
    },
    "heartBeat": {
        "muid": "",
        "name": "heartBeat",
        "sn": "MJ0FRY04FEF4H8MP",
        "timestamp": "",
        "version": "v2.1.1_1",
    },
    "timing (MJ0FRY04FEF4H8MP)": {
        "data": {"time": "2026-03-26 11:09:28", "status": 0},
        "muid": "",
        "name": "timing",
        "sn": "MJ0FRY04FEF4H8MP",
        "timestamp": "",
        "version": "v2.1.1_1",
    },
    "channelPersonAlert": {
        "data": {
            "ownerType": 3,
            "sendCenterStatus": 0,
            "triggerInduction": "2026-08-27 09:21:00",
            "snapUrl": "https://bsgoalsmartcloud.oss-cn-shenzhen.aliyuncs.com/AccessControl/1744353215604.jpg,https://bsgoalsmartcloud.oss-cn-shenzhen.aliyuncs.com/AccessControl/TD0TD204EB6QXKGV/2025-04-11/11000_20250411135944_rgb.jpg",
            "eventType": 1,
            "ownerId": 10077,
            "triggerWarning": "2026-08-27 09:21:00",
            "recordId": "",
            "ownerName": "77",
            "runUserNumber": 3,
            "temperature": "36.5",
            "keyType": 1,
            "userNumber": 1,
        },
        "muid": "",
        "name": "channelPersonAlert",
        "sn": "TD0TD204FC3T9751",
        "timestamp": "",
        "version": "v2.0.0",
    },
    "banner": {
        "name": "banner",
        "muid": "0220e2b513e2-2d8f-4d0e-a591-bbba0afead50",
        "sn": "MJ0FRY04E318Z276",
        "data": {
            "bannerId": 259,
            "type": 2,
            "url": "https://bsgoalsmartcloud.oss-cn-shenzhen.aliyuncs.com/AccessControl/20241205/20241205133348_ex1y.MP4",
            "serialNumber": 2,
        },
        "operator": "13068732224",
        "version": "v2.0.0_1",
        "timestamp": "",
    },
    "delBanner": {
        "name": "delBanner",
        "muid": "",
        "sn": "MJ0FRY04E318Z276",
        "data": {"bannerId": 258},
        "operator": "13068732224",
        "version": "v2.0.0_1",
        "timestamp": "1673234090000",
    },
}


def _app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


class MqttToolApp:
    def __init__(self, root):
        self.root = root
        root.title("MQTT 发送工具")
        root.geometry("920x760")
        root.minsize(760, 580)
        self._syncing = False
        self._last_payload_sn = None
        self.templates_path = os.path.join(_app_dir(), "templates.json")
        self.history_path = os.path.join(_app_dir(), "history.json")
        self.templates = self._load_templates()
        self.history = self._load_history()
        self._history_widgets = {}

        frm = ttk.Frame(root, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        conn = ttk.Frame(frm)
        conn.pack(fill=tk.X)
        self.host = self._add_history_combo(conn, "host", "Host", "192.168.110.19", 0)
        self.port = self._add_history_combo(conn, "port", "Port", "1883", 2, width=8)
        self.user = self._add_history_combo(conn, "user", "User", "test", 4)
        ttk.Label(conn, text="Password").grid(row=0, column=6, sticky=tk.W, padx=(8, 4))
        pwd_wrap = ttk.Frame(conn)
        pwd_wrap.grid(row=0, column=7, sticky=tk.EW)
        conn.columnconfigure(7, weight=1)
        self.pwd = ttk.Entry(pwd_wrap, show="*")
        self.pwd.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.pwd.insert(0, "Tt4@0#kA8")
        self.pwd_show = tk.BooleanVar(value=False)
        ttk.Checkbutton(pwd_wrap, text="显示", variable=self.pwd_show, command=self._toggle_pwd).pack(side=tk.LEFT, padx=(4, 0))

        topic_row = ttk.Frame(frm)
        topic_row.pack(fill=tk.X, pady=(8, 0))
        ttk.Label(topic_row, text="主题").pack(side=tk.LEFT)
        topic_wrap = ttk.Frame(topic_row)
        topic_wrap.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
        topic_vals = self.history.get("topic") or ["cloud/TD0TD204FC3T9751"]
        self.topic = ttk.Combobox(topic_wrap, values=topic_vals)
        self.topic.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.topic.set(topic_vals[0])
        self._history_widgets["topic"] = self.topic
        ttk.Button(topic_wrap, text="删", width=3, command=lambda: self._delete_history("topic")).pack(side=tk.LEFT, padx=(4, 0))
        self._bind_history_combo(self.topic, "topic")

        tpl_row = ttk.Frame(frm)
        tpl_row.pack(fill=tk.X, pady=(8, 0))
        ttk.Label(tpl_row, text="模版").pack(side=tk.LEFT)
        self.template = ttk.Combobox(tpl_row, state="readonly", values=list(self.templates.keys()))
        self.template.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 6))
        start = DEFAULT_TEMPLATE if DEFAULT_TEMPLATE in self.templates else next(iter(self.templates))
        self.template.set(start)
        self.template.bind("<<ComboboxSelected>>", self._on_template)
        ttk.Button(tpl_row, text="保存", command=self._save_template).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(tpl_row, text="另存为", command=self._save_template_as).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(tpl_row, text="重命名", command=self._rename_template).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(tpl_row, text="删除", command=self._delete_template).pack(side=tk.LEFT)

        ttk.Label(frm, text="发送内容").pack(anchor=tk.W, pady=(8, 0))
        payload_wrap = ttk.Frame(frm)
        payload_wrap.pack(fill=tk.BOTH, expand=True, pady=(4, 0))
        self.payload = tk.Text(payload_wrap, wrap=tk.NONE, font=("Consolas", 10), undo=True)
        yscroll = ttk.Scrollbar(payload_wrap, orient=tk.VERTICAL, command=self.payload.yview)
        self.payload.configure(yscrollcommand=yscroll.set)
        self.payload.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.payload.bind("<<Modified>>", self._on_payload_modified)

        act = ttk.Frame(frm)
        act.pack(fill=tk.X, pady=8)
        self.auto_sign = tk.BooleanVar(value=True)
        self.auto_trigger_time = tk.BooleanVar(value=True)
        self.sync_sn = tk.BooleanVar(value=True)
        ttk.Checkbutton(act, text="发送前自动 muid + sign", variable=self.auto_sign).pack(side=tk.LEFT)
        ttk.Checkbutton(act, text="触发时间取当前", variable=self.auto_trigger_time).pack(side=tk.LEFT, padx=(12, 0))
        ttk.Checkbutton(act, text="模版 sn 跟随主题", variable=self.sync_sn).pack(side=tk.LEFT, padx=(12, 0))
        self.send_btn = ttk.Button(act, text="发送", command=self._send)
        self.send_btn.pack(side=tk.RIGHT)

        ttk.Label(frm, text="日志").pack(anchor=tk.W)
        self.log = tk.Text(frm, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.log.pack(fill=tk.X)

        self._fill_payload(self.templates[start])

    def _add_history_combo(self, parent, key, label, default, col, width=18):
        ttk.Label(parent, text=label).grid(row=0, column=col, sticky=tk.W, padx=(0 if col == 0 else 8, 4))
        wrap = ttk.Frame(parent)
        wrap.grid(row=0, column=col + 1, sticky=tk.EW)
        parent.columnconfigure(col + 1, weight=1)
        values = self.history.get(key) or [default]
        combo = ttk.Combobox(wrap, values=values, width=width)
        combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        combo.set(values[0] if values else default)
        ttk.Button(wrap, text="删", width=3, command=lambda k=key: self._delete_history(k)).pack(side=tk.LEFT, padx=(4, 0))
        self._history_widgets[key] = combo
        self._bind_history_combo(combo, key)
        return combo

    def _bind_history_combo(self, combo, key):
        combo.bind("<FocusOut>", lambda e, k=key, c=combo: self._remember(k, c.get()))
        combo.bind("<<ComboboxSelected>>", lambda e, k=key, c=combo: self._remember(k, c.get()))
        menu = tk.Menu(combo, tearoff=0)
        menu.add_command(label="删除此项", command=lambda k=key: self._delete_history(k))
        menu.add_command(label="清空历史", command=lambda k=key: self._clear_history(k))
        combo.bind("<Button-3>", lambda e, m=menu: m.tk_popup(e.x_root, e.y_root))

    def _toggle_pwd(self):
        self.pwd.configure(show="" if self.pwd_show.get() else "*")

    def _load_history(self):
        defaults = {
            "host": ["192.168.110.19"],
            "port": ["1883"],
            "user": ["test"],
            "topic": ["cloud/TD0TD204FC3T9751"],
        }
        if os.path.isfile(self.history_path):
            try:
                with open(self.history_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    for key, seed in defaults.items():
                        items = data.get(key)
                        if isinstance(items, list) and items:
                            defaults[key] = [str(x) for x in items if str(x).strip()]
            except Exception:
                pass
        return defaults

    def _persist_history(self):
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def _remember(self, key, value):
        value = (value or "").strip()
        if not value:
            return
        items = list(self.history.get(key) or [])
        if value in items:
            items.remove(value)
        items.insert(0, value)
        self.history[key] = items[:50]
        combo = self._history_widgets.get(key)
        if combo:
            current = combo.get()
            combo.configure(values=self.history[key])
            if combo.get() != current:
                combo.set(current)
        self._persist_history()

    def _delete_history(self, key):
        combo = self._history_widgets.get(key)
        if not combo:
            return
        value = combo.get().strip()
        items = list(self.history.get(key) or [])
        if value in items:
            items.remove(value)
            self.history[key] = items
            self._persist_history()
            combo.configure(values=items)
            combo.set(items[0] if items else "")
            self._append_log("已删除历史: " + value)

    def _clear_history(self, key):
        combo = self._history_widgets.get(key)
        self.history[key] = []
        self._persist_history()
        if combo:
            combo.configure(values=[])
            combo.set("")

    def _load_templates(self):
        if os.path.isfile(self.templates_path):
            try:
                with open(self.templates_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict) and data:
                    return data
            except Exception:
                pass
        return copy.deepcopy(TEMPLATES)

    def _persist_templates(self):
        with open(self.templates_path, "w", encoding="utf-8") as f:
            json.dump(self.templates, f, ensure_ascii=False, indent=2)

    def _refresh_template_box(self, select=None):
        names = list(self.templates.keys())
        self.template.configure(values=names)
        if select and select in self.templates:
            self.template.set(select)
        elif self.template.get() not in self.templates and names:
            self.template.set(names[0])

    def _read_payload_json(self):
        raw = self.payload.get("1.0", tk.END).strip()
        body = json.loads(raw)
        if not isinstance(body, dict):
            raise ValueError("发送内容必须是 JSON 对象")
        return body

    def _save_template(self):
        name = self.template.get().strip()
        if not name:
            self._save_template_as()
            return
        try:
            body = self._read_payload_json()
        except Exception as e:
            messagebox.showerror("保存失败", str(e), parent=self.root)
            return
        self.templates[name] = body
        self._persist_templates()
        self._refresh_template_box(name)
        self._append_log("已保存模版: " + name)

    def _save_template_as(self):
        name = simpledialog.askstring("另存为模版", "模版名称", parent=self.root)
        if not name:
            return
        name = name.strip()
        if not name:
            return
        if name in self.templates and not messagebox.askyesno("覆盖", "模版已存在，是否覆盖？", parent=self.root):
            return
        try:
            body = self._read_payload_json()
        except Exception as e:
            messagebox.showerror("保存失败", str(e), parent=self.root)
            return
        self.templates[name] = body
        self._persist_templates()
        self._refresh_template_box(name)
        self._append_log("已另存为模版: " + name)

    def _rename_template(self):
        old = self.template.get().strip()
        if not old or old not in self.templates:
            return
        name = simpledialog.askstring("重命名模版", "新名称", initialvalue=old, parent=self.root)
        if not name:
            return
        name = name.strip()
        if not name or name == old:
            return
        if name in self.templates:
            messagebox.showerror("重命名失败", "名称已存在", parent=self.root)
            return
        self.templates[name] = self.templates.pop(old)
        self._persist_templates()
        self._refresh_template_box(name)
        self._append_log("模版已重命名: %s -> %s" % (old, name))

    def _delete_template(self):
        name = self.template.get().strip()
        if not name or name not in self.templates:
            return
        if len(self.templates) <= 1:
            messagebox.showerror("删除失败", "至少保留一个模版", parent=self.root)
            return
        if not messagebox.askyesno("删除模版", "确定删除「%s」？" % name, parent=self.root):
            return
        del self.templates[name]
        self._persist_templates()
        self._refresh_template_box()
        self._on_template()
        self._append_log("已删除模版: " + name)

    def _fill_payload(self, data):
        self._syncing = True
        try:
            text = json.dumps(data, ensure_ascii=False, indent=2)
            self.payload.delete("1.0", tk.END)
            self.payload.insert("1.0", text)
            sn = data.get("sn") if isinstance(data, dict) else None
            self._last_payload_sn = str(sn).strip() if sn else None
        finally:
            self.payload.edit_modified(False)
            self._syncing = False

    def _topic_sn(self):
        topic = self.topic.get().strip().rstrip("/")
        if not topic:
            return ""
        return topic.split("/")[-1]

    def _set_topic_sn(self, sn):
        topic = self.topic.get().strip()
        if "/" in topic:
            new_topic = topic.rsplit("/", 1)[0] + "/" + sn
        elif topic:
            new_topic = sn
        else:
            new_topic = "cloud/" + sn
        if new_topic != topic:
            self.topic.delete(0, tk.END)
            self.topic.insert(0, new_topic)
            self._remember("topic", new_topic)

    def _on_payload_modified(self, _event=None):
        if self._syncing:
            self.payload.edit_modified(False)
            return
        self.payload.edit_modified(False)
        try:
            body = json.loads(self.payload.get("1.0", tk.END))
        except json.JSONDecodeError:
            return
        if not isinstance(body, dict) or "sn" not in body:
            return
        sn = str(body.get("sn") or "").strip()
        if not sn or sn == self._last_payload_sn:
            return
        self._last_payload_sn = sn
        self._set_topic_sn(sn)

    def _on_template(self, _event=None):
        name = self.template.get()
        data = self.templates.get(name)
        if not data:
            return
        payload = json.loads(json.dumps(data, ensure_ascii=False))
        if self.sync_sn.get() and "sn" in payload:
            sn = self._topic_sn()
            if sn:
                payload["sn"] = sn
        self._fill_payload(payload)

    def _append_log(self, msg):
        self.log.configure(state=tk.NORMAL)
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)
        self.log.configure(state=tk.DISABLED)

    def _send(self):
        try:
            body = self._read_payload_json()
        except json.JSONDecodeError as e:
            self._append_log("JSON 无效: " + str(e))
            return
        except ValueError as e:
            self._append_log(str(e))
            return
        host = self.host.get().strip()
        topic = self.topic.get().strip()
        user = self.user.get().strip()
        pwd = self.pwd.get()
        try:
            port = int(self.port.get().strip())
        except ValueError:
            self._append_log("Port 必须是数字")
            return
        if not host or not topic:
            self._append_log("Host / 主题不能为空")
            return
        self._remember("host", host)
        self._remember("port", str(port))
        self._remember("user", user)
        self._remember("topic", topic)
        auto_sign = self.auto_sign.get()
        auto_trigger_time = self.auto_trigger_time.get()
        self.send_btn.configure(state=tk.DISABLED)
        self._append_log("正在发送 -> %s  %s" % (host, topic))
        threading.Thread(
            target=self._do_send,
            args=(host, port, topic, user, pwd, body, auto_sign, auto_trigger_time),
            daemon=True,
        ).start()

    def _do_send(self, host, port, topic, user, pwd, body, auto_sign, auto_trigger_time):
        try:
            payload = json.loads(json.dumps(body, ensure_ascii=False))
            if auto_trigger_time:
                data = payload.get("data")
                if isinstance(data, dict):
                    now = time.strftime("%Y-%m-%d %H:%M:%S")
                    if "triggerInduction" in data:
                        data["triggerInduction"] = now
                    if "triggerWarning" in data:
                        data["triggerWarning"] = now
            if auto_sign:
                payload.pop("sign", None)
                payload["muid"] = str(uuid.uuid1())
                payload["sign"] = md5sign(payload)
            message = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
            Mqttpub(host, topic, port).clicent_main(message, user, pwd)
            pretty = json.dumps(payload, ensure_ascii=False, indent=2)
            self.root.after(0, lambda m=message, p=pretty: self._on_send_done(True, m, p))
        except Exception as e:
            err = str(e)
            self.root.after(0, lambda m=err: self._on_send_done(False, m))

    def _on_send_done(self, ok, detail, pretty=None):
        self.send_btn.configure(state=tk.NORMAL)
        if ok:
            if pretty:
                self._fill_payload(json.loads(pretty))
            self._append_log("发送成功")
            self._append_log(detail)
        else:
            self._append_log("发送失败: " + detail)


if __name__ == "__main__":
    root = tk.Tk()
    MqttToolApp(root)
    root.mainloop()
