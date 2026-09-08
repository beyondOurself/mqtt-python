# -*- coding: utf-8 -*-
import json
import tkinter as tk
from tkinter import ttk

from mqtt_tool.ui.theme import C
from mqtt_tool.ui.widgets import _styled_text

class PayloadTab:
    def __init__(self, parent, title, on_change, on_sn_change):
        self.parent = parent
        self.title = title
        self.on_change = on_change
        self.on_sn_change = on_sn_change
        self._syncing = False
        self._format_job = None
        self._last_payload_sn = None
        self.chip = None

        self.frame = tk.Frame(parent, bg=C["surface"])
        editor_wrap = tk.Frame(self.frame, bg=C["surface"])
        editor_wrap.pack(fill=tk.BOTH, expand=True, padx=2, pady=(2, 0))

        self.text = _styled_text(editor_wrap, wrap=tk.NONE)
        yscroll = ttk.Scrollbar(editor_wrap, orient=tk.VERTICAL, command=self.text.yview)
        xscroll = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self.text.xview)
        self.text.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        xscroll.pack(fill=tk.X, padx=2, pady=(0, 2))

        status_wrap = tk.Frame(self.frame, bg=C["surface"])
        status_wrap.pack(fill=tk.X, padx=2, pady=(4, 6))
        self.status_pill = tk.Frame(status_wrap, bg=C["surface_alt"], highlightbackground=C["border"], highlightthickness=1)
        self.status_pill.pack(anchor=tk.W)
        self.status = tk.Label(
            self.status_pill,
            text="  等待输入  ",
            font=C["ui_sm"],
            fg=C["muted"],
            bg=C["surface_alt"],
            padx=4,
            pady=2,
        )
        self.status.pack()

        self.text.bind("<<Modified>>", self._on_modified)
        self.text.bind("<KeyRelease>", self._on_key_release)

    def show(self):
        self.frame.pack(fill=tk.BOTH, expand=True)

    def hide(self):
        self.frame.pack_forget()

    def schedule_format(self, root):
        if self._format_job:
            root.after_cancel(self._format_job)
        self._format_job = root.after(450, lambda: self._auto_format())

    def _on_key_release(self, _event=None):
        self.on_change()

    def _on_modified(self, _event=None):
        if self._syncing:
            self.text.edit_modified(False)
            return
        self.text.edit_modified(False)
        self.on_change()
        self._try_sn_sync()

    def _try_sn_sync(self):
        try:
            body = json.loads(self.text.get("1.0", tk.END))
        except json.JSONDecodeError:
            return
        if not isinstance(body, dict) or "sn" not in body:
            return
        sn = str(body.get("sn") or "").strip()
        if not sn or sn == self._last_payload_sn:
            return
        self._last_payload_sn = sn
        self.on_sn_change(sn)

    def _set_status(self, text, kind="muted"):
        styles = {
            "muted": (C["surface_alt"], C["muted"]),
            "ok": (C["success_bg"], C["success"]),
            "err": (C["error_bg"], C["error"]),
        }
        bg, fg = styles.get(kind, styles["muted"])
        self.status_pill.configure(bg=bg, highlightbackground=bg)
        self.status.configure(text="  %s  " % text, bg=bg, fg=fg)

    def _auto_format(self):
        self._format_job = None
        if self._syncing:
            return
        raw = self.text.get("1.0", tk.END).strip()
        if not raw:
            self._set_status("等待输入", "muted")
            return
        try:
            body = json.loads(raw)
            pretty = json.dumps(body, ensure_ascii=False, indent=2)
            self._syncing = True
            if pretty != raw:
                pos = self.text.index(tk.INSERT)
                self.text.delete("1.0", tk.END)
                self.text.insert("1.0", pretty)
                try:
                    self.text.mark_set(tk.INSERT, pos)
                except tk.TclError:
                    pass
            self._set_status("JSON 已格式化", "ok")
            if isinstance(body, dict) and "sn" in body:
                self._last_payload_sn = str(body.get("sn") or "").strip() or None
        except json.JSONDecodeError as e:
            self._set_status("JSON 无效 · %s" % e.msg, "err")
        finally:
            self.text.edit_modified(False)
            self._syncing = False

    def read_json(self):
        raw = self.text.get("1.0", tk.END).strip()
        body = json.loads(raw)
        if not isinstance(body, dict):
            raise ValueError("发送内容必须是 JSON 对象")
        return body

    def fill(self, data):
        self._syncing = True
        try:
            text = json.dumps(data, ensure_ascii=False, indent=2)
            self.text.delete("1.0", tk.END)
            self.text.insert("1.0", text)
            sn = data.get("sn") if isinstance(data, dict) else None
            self._last_payload_sn = str(sn).strip() if sn else None
            self._set_status("JSON 已格式化", "ok")
        finally:
            self.text.edit_modified(False)
            self._syncing = False

    def get_raw_text(self):
        return self.text.get("1.0", tk.END).strip()

    def fill_raw(self, raw):
        self._syncing = True
        try:
            self.text.delete("1.0", tk.END)
            self.text.insert("1.0", raw)
            try:
                body = json.loads(raw.strip())
                if isinstance(body, dict) and "sn" in body:
                    self._last_payload_sn = str(body.get("sn") or "").strip() or None
                self._set_status("JSON 已格式化", "ok")
            except json.JSONDecodeError as e:
                self._set_status("JSON 无效 · %s" % e.msg, "err")
        finally:
            self.text.edit_modified(False)
            self._syncing = False

