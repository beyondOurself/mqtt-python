# -*- coding: utf-8 -*-
import copy
import json
import os
import re
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

C = {
    "canvas": "#EEF2F6",
    "header_bg": "#0B1220",
    "header_bg2": "#151D2E",
    "header_fg": "#F8FAFC",
    "header_sub": "#94A3B8",
    "accent": "#2563EB",
    "accent_hover": "#1D4ED8",
    "accent_soft": "#DBEAFE",
    "accent_glow": "#3B82F6",
    "surface": "#FFFFFF",
    "surface_alt": "#F8FAFC",
    "border": "#E2E8F0",
    "text": "#0F172A",
    "muted": "#64748B",
    "success": "#059669",
    "success_bg": "#ECFDF5",
    "error": "#DC2626",
    "error_bg": "#FEF2F2",
    "code_bg": "#1E293B",
    "code_fg": "#CBD5E1",
    "code_caret": "#60A5FA",
    "log_bg": "#F8FAFC",
    "sidebar_w": 328,
    "mono": ("Cascadia Mono", 11),
    "mono_fallback": ("Consolas", 11),
    "ui": ("Segoe UI", 10),
    "ui_sm": ("Segoe UI", 9),
    "ui_bold": ("Segoe UI", 10, "bold"),
    "section": ("Segoe UI", 11, "bold"),
    "hero": ("Segoe UI", 20, "bold"),
    "hero_sub": ("Segoe UI", 10),
}

IC = {
    "brand": "\uE968",
    "send": "\uE724",
    "add": "\uE710",
    "close": "\uE711",
    "edit": "\uE70F",
    "template": "\uE8A5",
    "connection": "\uE839",
    "log": "\uE7C3",
    "dock": "\uE72B",
    "search": "\uE721",
    "payload": "\uE943",
    "manage": "\uE8F1",
    "apply": "\uE898",
}


def _icon_font(size=14):
    try:
        import tkinter.font as tkfont
        tkfont.Font(family="Segoe MDL2 Assets", size=size)
        return ("Segoe MDL2 Assets", size)
    except Exception:
        return C["ui"]


def _icon_text(glyph, fallback):
    try:
        import tkinter.font as tkfont
        tkfont.Font(family="Segoe MDL2 Assets", size=12)
        return glyph
    except Exception:
        return fallback


def _mono_font():
    try:
        import tkinter.font as tkfont
        tkfont.Font(family="Cascadia Mono", size=11)
        return C["mono"]
    except Exception:
        return C["mono_fallback"]


def _flat_btn(parent, text, command, variant="secondary", icon=None, **kw):
    palette = {
        "primary": (C["accent"], "#FFFFFF", C["accent_hover"], "#FFFFFF"),
        "secondary": (C["surface"], C["text"], "#F1F5F9", C["text"]),
        "ghost": ("#E2E8F0", C["muted"], "#CBD5E1", C["text"]),
        "outline": (C["surface"], C["accent"], C["accent_soft"], C["accent_hover"]),
    }
    bg, fg, hover, active_fg = palette.get(variant, palette["secondary"])
    padx = kw.get("padx", 14)
    pady = kw.get("pady", 8)
    text_font = kw.get("font", C["ui_bold"] if variant == "primary" else C["ui"])

    if icon:
        wrap = tk.Frame(parent, bg=bg, cursor="hand2", highlightthickness=0)
        icon_lbl = tk.Label(wrap, text=_icon_text(icon, "●"), font=_icon_font(12), bg=bg, fg=fg, cursor="hand2")
        icon_lbl.pack(side=tk.LEFT, padx=(padx, 4), pady=pady)
        text_lbl = tk.Label(wrap, text=text, font=text_font, bg=bg, fg=fg, cursor="hand2")
        text_lbl.pack(side=tk.LEFT, padx=(0, padx), pady=pady)
        disabled = {"on": False}

        def _paint(h_bg, h_fg, cursor="hand2"):
            wrap.configure(bg=h_bg, cursor=cursor)
            icon_lbl.configure(bg=h_bg, fg=h_fg, cursor=cursor)
            text_lbl.configure(bg=h_bg, fg=h_fg, cursor=cursor)

        def _click(_e=None):
            if disabled["on"]:
                return
            command()

        def _enter(_e):
            if disabled["on"]:
                return
            _paint(hover, active_fg)

        def _leave(_e):
            if disabled["on"]:
                _paint(C["border"], C["muted"], "arrow")
            else:
                _paint(bg, fg)

        def _configure(**kwargs):
            if "width" in kwargs:
                tk.Frame.configure(wrap, width=kwargs["width"])
            if "state" in kwargs:
                disabled["on"] = kwargs["state"] == tk.DISABLED
                if disabled["on"]:
                    _paint(C["border"], C["muted"], "arrow")
                else:
                    _paint(bg, fg)

        for w in (wrap, icon_lbl, text_lbl):
            w.bind("<Button-1>", _click)
            w.bind("<Enter>", _enter)
            w.bind("<Leave>", _leave)
        wrap.configure = _configure
        wrap._base_bg, wrap._base_fg = bg, fg
        if kw.get("width"):
            tk.Frame.configure(wrap, width=kw["width"])
        return wrap

    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=fg,
        activebackground=hover,
        activeforeground=active_fg,
        relief=tk.FLAT,
        bd=0,
        padx=padx,
        pady=pady,
        font=text_font,
        cursor="hand2",
        highlightthickness=0,
    )
    if kw.get("width"):
        btn.configure(width=kw["width"])

    def _enter(_e):
        btn.configure(bg=hover, fg=active_fg)

    def _leave(_e):
        btn.configure(bg=bg, fg=fg)

    btn.bind("<Enter>", _enter)
    btn.bind("<Leave>", _leave)
    btn._base_bg, btn._base_fg = bg, fg
    return btn


def _card(parent, pad=16, fill=tk.X, expand=False, accent=False):
    wrap = tk.Frame(parent, bg=C["canvas"])
    shell = tk.Frame(wrap, bg=C["accent"] if accent else C["border"])
    shell.pack(fill=fill, expand=expand)
    box = tk.Frame(shell, bg=C["surface"], highlightthickness=0)
    box.pack(fill=tk.BOTH, expand=True, padx=(3 if accent else 1, 1), pady=1)
    inner = tk.Frame(box, bg=C["surface"], padx=pad, pady=pad)
    inner.pack(fill=tk.BOTH, expand=True)
    return wrap, inner


def _section_head(parent, title, subtitle=None, icon=None):
    head = tk.Frame(parent, bg=C["surface"])
    head.pack(fill=tk.X, pady=(0, 12))
    title_row = tk.Frame(head, bg=C["surface"])
    title_row.pack(fill=tk.X)
    if icon:
        badge = tk.Frame(title_row, bg=C["accent_soft"], width=28, height=28)
        badge.pack_propagate(False)
        badge.pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(badge, text=_icon_text(icon, "●"), font=_icon_font(12), fg=C["accent"], bg=C["accent_soft"]).pack(expand=True)
    tk.Label(title_row, text=title, font=C["section"], fg=C["text"], bg=C["surface"], anchor=tk.W).pack(side=tk.LEFT)
    if subtitle:
        tk.Label(head, text=subtitle, font=C["ui_sm"], fg=C["muted"], bg=C["surface"], anchor=tk.W).pack(fill=tk.X, pady=(4, 0))
    tk.Frame(parent, bg=C["border"], height=1).pack(fill=tk.X, pady=(0, 12))
    return head


def _field_label(parent, text):
    tk.Label(parent, text=text, font=C["ui_sm"], fg=C["muted"], bg=C["surface"], anchor=tk.W).pack(fill=tk.X, pady=(0, 4))


def _styled_entry(parent, **kw):
    e = tk.Entry(
        parent,
        font=C["ui"],
        bg=C["surface_alt"],
        fg=C["text"],
        relief=tk.FLAT,
        highlightthickness=1,
        highlightbackground=C["border"],
        highlightcolor=C["accent"],
        insertbackground=C["accent"],
        **kw,
    )
    return e


def _styled_text(parent, **kw):
    defaults = dict(
        font=_mono_font(),
        bg=C["code_bg"],
        fg=C["code_fg"],
        insertbackground=C["code_caret"],
        relief=tk.FLAT,
        highlightthickness=1,
        highlightbackground=C["border"],
        highlightcolor=C["accent"],
        padx=12,
        pady=10,
        undo=True,
        autoseparators=True,
        maxundo=-1,
    )
    defaults.update(kw)
    return tk.Text(parent, **defaults)


def _bind_text_shortcuts(text, on_after_paste=None):
    menu = tk.Menu(text, tearoff=0)

    def _select_all(_event=None):
        text.tag_remove(tk.SEL, "1.0", tk.END)
        text.tag_add(tk.SEL, "1.0", tk.END)
        text.mark_set(tk.INSERT, tk.END)
        text.see(tk.INSERT)
        return "break"

    def _copy(_event=None):
        try:
            chunk = text.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            return "break"
        text.clipboard_clear()
        text.clipboard_append(chunk)
        return "break"

    def _paste(_event=None):
        try:
            chunk = text.clipboard_get()
        except tk.TclError:
            return "break"
        try:
            if text.tag_ranges(tk.SEL):
                text.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass
        text.insert(tk.INSERT, chunk)
        if on_after_paste:
            on_after_paste()
        return "break"

    def _cut(_event=None):
        _copy()
        try:
            text.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass
        return "break"

    def _undo(_event=None):
        try:
            text.edit_undo()
        except tk.TclError:
            pass
        return "break"

    def _redo(_event=None):
        try:
            text.edit_redo()
        except tk.TclError:
            pass
        return "break"

    for seq, fn in (
        ("<Control-a>", _select_all),
        ("<Control-A>", _select_all),
        ("<Control-c>", _copy),
        ("<Control-C>", _copy),
        ("<Control-v>", _paste),
        ("<Control-V>", _paste),
        ("<Shift-Insert>", _paste),
        ("<Control-x>", _cut),
        ("<Control-X>", _cut),
        ("<Control-z>", _undo),
        ("<Control-Z>", _undo),
        ("<Control-y>", _redo),
        ("<Control-Y>", _redo),
    ):
        text.bind(seq, fn)

    menu.add_command(label="全选", command=_select_all)
    menu.add_command(label="复制", command=_copy)
    menu.add_command(label="粘贴", command=_paste)
    menu.add_command(label="剪切", command=_cut)
    menu.add_separator()
    menu.add_command(label="撤销", command=text.edit_undo)
    menu.add_command(label="重做", command=text.edit_redo)

    def _popup_menu(event):
        menu.tk_popup(event.x_root, event.y_root)

    text.bind("<Button-3>", _popup_menu)


def _scrollable_frame(parent, width=None, bg=None):
    bg = bg or C["canvas"]
    wrap = tk.Frame(parent, bg=bg)
    canvas = tk.Canvas(wrap, bg=bg, highlightthickness=0, borderwidth=0)
    if width:
        canvas.configure(width=width)
    vsb = ttk.Scrollbar(wrap, orient=tk.VERTICAL, command=canvas.yview)
    inner = tk.Frame(canvas, bg=bg)
    inner_id = canvas.create_window((0, 0), window=inner, anchor="nw")

    def _sync_scroll(_event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _sync_width(event):
        canvas.itemconfigure(inner_id, width=event.width)

    def _wheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bind_wheel(_event):
        canvas.bind_all("<MouseWheel>", _wheel)

    def _unbind_wheel(_event):
        canvas.unbind_all("<MouseWheel>")

    inner.bind("<Configure>", _sync_scroll)
    canvas.bind("<Configure>", _sync_width)
    canvas.bind("<Enter>", _bind_wheel)
    canvas.bind("<Leave>", _unbind_wheel)
    canvas.configure(yscrollcommand=vsb.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    return wrap, inner, canvas


def _app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


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


class LogViewerDialog(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.title("运行日志")
        self.geometry("860x560")
        self.minsize(640, 400)
        self.configure(bg=C["canvas"])
        self.transient(parent)
        self._search_idx = 0
        self._hits = []
        self._last_keyword = ""

        head = tk.Frame(self, bg=C["header_bg"], height=52)
        head.pack(fill=tk.X)
        head.pack_propagate(False)
        row = tk.Frame(head, bg=C["header_bg"])
        row.pack(side=tk.LEFT, padx=20, pady=12)
        badge = tk.Frame(row, bg=C["accent_soft"], width=28, height=28)
        badge.pack_propagate(False)
        badge.pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(badge, text=_icon_text(IC["log"], "L"), font=_icon_font(12), fg=C["accent"], bg=C["accent_soft"]).pack(expand=True)
        tk.Label(row, text="运行日志", font=C["section"], fg=C["header_fg"], bg=C["header_bg"]).pack(side=tk.LEFT)
        tk.Frame(head, bg=C["accent_glow"], height=2).pack(side=tk.BOTTOM, fill=tk.X)

        tool = tk.Frame(self, bg=C["canvas"], padx=16, pady=12)
        tool.pack(fill=tk.X)
        tk.Label(tool, text="搜索", font=C["ui_sm"], fg=C["muted"], bg=C["canvas"]).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(tool, textvariable=self.search_var, font=C["ui"], width=32)
        self.search_entry.pack(side=tk.LEFT, padx=(8, 8), fill=tk.X, expand=True)
        self.search_entry.bind("<Return>", lambda e: self._search_next())
        _flat_btn(tool, "查找", self._search_next, variant="outline", padx=10, pady=6).pack(side=tk.LEFT, padx=(0, 6))
        _flat_btn(tool, "上一个", self._search_prev, variant="ghost", padx=10, pady=6).pack(side=tk.LEFT, padx=(0, 6))
        _flat_btn(tool, "下一个", self._search_next, variant="ghost", padx=10, pady=6).pack(side=tk.LEFT, padx=(0, 6))
        _flat_btn(tool, "刷新", self._reload, variant="secondary", padx=10, pady=6).pack(side=tk.LEFT)

        body_wrap, body = _card(self, pad=12, fill=tk.BOTH, expand=True)
        body_wrap.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))
        text_wrap = tk.Frame(body, bg=C["surface"])
        text_wrap.pack(fill=tk.BOTH, expand=True)
        self.text = _styled_text(text_wrap, wrap=tk.WORD, state=tk.DISABLED, bg=C["log_bg"], fg=C["text"], font=C["mono_fallback"])
        yscroll = ttk.Scrollbar(text_wrap, orient=tk.VERTICAL, command=self.text.yview)
        self.text.configure(yscrollcommand=yscroll.set)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.tag_configure("hit", background="#FEF3C7", foreground=C["text"])
        self.text.tag_configure("current", background="#FDE68A", foreground=C["text"])

        foot = tk.Frame(self, bg=C["canvas"])
        foot.pack(fill=tk.X, padx=16, pady=(0, 16))
        self.status = tk.Label(foot, text="", font=C["ui_sm"], fg=C["muted"], bg=C["canvas"], anchor=tk.W)
        self.status.pack(side=tk.LEFT, fill=tk.X, expand=True)
        _flat_btn(foot, "关闭", self.destroy, variant="secondary").pack(side=tk.RIGHT)

        self._reload()

    def _reload(self):
        content = self.app.log.get("1.0", tk.END)
        self.text.configure(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", content)
        self.text.configure(state=tk.DISABLED)
        self._clear_hits()
        self.status.configure(text="共 %d 条" % content.count("─" * 58))

    def _clear_hits(self):
        self.text.tag_remove("hit", "1.0", tk.END)
        self.text.tag_remove("current", "1.0", tk.END)
        self._hits = []
        self._search_idx = 0

    def _collect_hits(self, keyword):
        self._clear_hits()
        self._last_keyword = keyword
        if not keyword:
            return
        start = "1.0"
        while True:
            pos = self.text.search(keyword, start, stopindex=tk.END, nocase=True)
            if not pos:
                break
            end = "%s+%dc" % (pos, len(keyword))
            self.text.tag_add("hit", pos, end)
            self._hits.append(pos)
            start = end

    def _goto_hit(self, idx):
        if not self._hits:
            self.status.configure(text="未找到匹配")
            return
        idx = idx % len(self._hits)
        self._search_idx = idx
        self.text.tag_remove("current", "1.0", tk.END)
        pos = self._hits[idx]
        end = "%s+%dc" % (pos, len(self._last_keyword))
        self.text.tag_add("current", pos, end)
        self.text.see(pos)
        self.status.configure(text="第 %d / %d 处" % (idx + 1, len(self._hits)))

    def _search_next(self):
        keyword = self.search_var.get().strip()
        if not keyword:
            return
        if keyword != self._last_keyword:
            self._collect_hits(keyword)
        if not self._hits:
            self.status.configure(text="未找到: %s" % keyword)
            return
        self._goto_hit(self._search_idx)
        self._search_idx = (self._search_idx + 1) % len(self._hits)

    def _search_prev(self):
        keyword = self.search_var.get().strip()
        if not keyword:
            return
        if keyword != self._last_keyword:
            self._collect_hits(keyword)
        if not self._hits:
            self.status.configure(text="未找到: %s" % keyword)
            return
        self._search_idx = (self._search_idx - 1) % len(self._hits)
        self._goto_hit(self._search_idx)


class TemplateManagerDialog(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._filter_var = tk.StringVar()
        self._dirty = False
        self._editing_name = None
        self._syncing_preview = False
        self._op_log = []
        self.title("模版管理")
        self.geometry("980x720")
        self.minsize(760, 560)
        self.configure(bg=C["canvas"])
        self.transient(parent)
        self.grab_set()

        head = tk.Frame(self, bg=C["header_bg"], height=56)
        head.pack(fill=tk.X)
        head.pack_propagate(False)
        row = tk.Frame(head, bg=C["header_bg"])
        row.pack(side=tk.LEFT, padx=20, pady=14)
        badge = tk.Frame(row, bg=C["accent_soft"], width=28, height=28)
        badge.pack_propagate(False)
        badge.pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(badge, text=_icon_text(IC["template"], "T"), font=_icon_font(12), fg=C["accent"], bg=C["accent_soft"]).pack(expand=True)
        tk.Label(row, text="模版管理", font=C["section"], fg=C["header_fg"], bg=C["header_bg"]).pack(side=tk.LEFT)
        tk.Frame(head, bg=C["accent_glow"], height=2).pack(side=tk.BOTTOM, fill=tk.X)

        body = tk.Frame(self, bg=C["canvas"], padx=16, pady=16)
        body.pack(fill=tk.BOTH, expand=True)

        left_wrap, left = _card(body, pad=14, fill=tk.BOTH, expand=True)
        left_wrap.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left_wrap.pack_propagate(False)
        left_wrap.configure(width=280)
        left_scroll, left, self._left_canvas = _scrollable_frame(left, bg=C["surface"])
        left_scroll.pack(fill=tk.BOTH, expand=True)

        _section_head(left, "模版列表", "双击应用到当前窗口", icon=IC["template"])

        search_row = tk.Frame(left, bg=C["surface"])
        search_row.pack(fill=tk.X, pady=(0, 8))
        tk.Label(search_row, text=_icon_text(IC["search"], "搜"), font=_icon_font(11), fg=C["muted"], bg=C["surface"]).pack(side=tk.LEFT, padx=(0, 6))
        self.search_entry = ttk.Entry(search_row, textvariable=self._filter_var, font=C["ui"])
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        list_wrap = tk.Frame(left, bg=C["surface"])
        list_wrap.pack(fill=tk.BOTH, expand=True)
        self.listbox = tk.Listbox(
            list_wrap,
            height=12,
            font=C["ui"],
            bg=C["surface_alt"],
            fg=C["text"],
            selectbackground=C["accent"],
            selectforeground="#FFFFFF",
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=C["border"],
            activestyle="dotbox",
            exportselection=False,
        )
        lb_scroll = ttk.Scrollbar(list_wrap, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=lb_scroll.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lb_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)
        self.listbox.bind("<Double-Button-1>", lambda e: self._apply())
        self._filter_var.trace_add("write", lambda *_: self._reload_list())

        self.count_label = tk.Label(left, text="", font=C["ui_sm"], fg=C["muted"], bg=C["surface"], anchor=tk.W)
        self.count_label.pack(fill=tk.X, pady=(6, 0))

        btn_col = tk.Frame(left, bg=C["surface"])
        btn_col.pack(fill=tk.X, pady=(10, 0))
        for text, cmd, variant, icon in (
            ("新建", self._create_new, "outline", IC["add"]),
            ("从当前窗口保存", self._save_from_tab, "secondary", IC["payload"]),
            ("应用选中", self._apply, "primary", IC["apply"]),
            ("重命名", self._rename, "ghost", IC["edit"]),
            ("删除", self._delete, "ghost", IC["close"]),
        ):
            _flat_btn(btn_col, text, cmd, variant=variant, icon=icon).pack(fill=tk.X, pady=3)

        right_wrap, right = _card(body, pad=14, fill=tk.BOTH, expand=True)
        right_wrap.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        _section_head(right, "JSON 编辑", "可直接修改后保存", icon=IC["edit"])

        prev_wrap = tk.Frame(right, bg=C["surface"])
        prev_wrap.pack(fill=tk.BOTH, expand=True)
        prev_wrap.grid_rowconfigure(0, weight=1)
        prev_wrap.grid_columnconfigure(0, weight=1)
        self.preview = _styled_text(prev_wrap, wrap=tk.NONE, bg=C["code_bg"], fg=C["code_fg"], font=C["mono_fallback"])
        p_y = ttk.Scrollbar(prev_wrap, orient=tk.VERTICAL, command=self.preview.yview)
        p_x = ttk.Scrollbar(prev_wrap, orient=tk.HORIZONTAL, command=self.preview.xview)
        self.preview.configure(yscrollcommand=p_y.set, xscrollcommand=p_x.set)
        self.preview.grid(row=0, column=0, sticky="nsew")
        p_y.grid(row=0, column=1, sticky="ns")
        p_x.grid(row=1, column=0, sticky="ew")
        _bind_text_shortcuts(self.preview, on_after_paste=self._format_preview_json)
        self.preview.bind("<<Modified>>", self._on_preview_edit)
        self.preview.bind("<FocusIn>", lambda _e: self._restore_list_selection())
        self.preview.bind("<Button-1>", lambda _e: self.after_idle(self._restore_list_selection), add="+")

        edit_row = tk.Frame(right, bg=C["surface"])
        edit_row.pack(fill=tk.X, pady=(10, 0))
        _flat_btn(edit_row, "保存右侧编辑", self._save_json_edit, variant="primary", icon=IC["apply"]).pack(side=tk.LEFT, padx=(0, 6))
        _flat_btn(edit_row, "放弃未保存", self._revert_json_edit, variant="ghost").pack(side=tk.LEFT)
        self.edit_status = tk.Label(edit_row, text="", font=C["ui_sm"], fg=C["muted"], bg=C["surface"], anchor=tk.E)
        self.edit_status.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        tk.Frame(right, bg=C["border"], height=1).pack(fill=tk.X, pady=(12, 10))
        _section_head(right, "操作记录", "选中后可回撤到变更前", icon=IC["log"])

        op_wrap = tk.Frame(right, bg=C["surface"])
        op_wrap.pack(fill=tk.BOTH, expand=False)
        self.op_list = tk.Listbox(
            op_wrap,
            height=4,
            font=C["ui_sm"],
            bg=C["surface_alt"],
            fg=C["text"],
            selectbackground=C["accent"],
            selectforeground="#FFFFFF",
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=C["border"],
            activestyle="dotbox",
            exportselection=False,
            selectmode=tk.BROWSE,
        )
        op_scroll = ttk.Scrollbar(op_wrap, orient=tk.VERTICAL, command=self.op_list.yview)
        self.op_list.configure(yscrollcommand=op_scroll.set)
        self.op_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        op_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.op_list.bind("<Double-Button-1>", lambda _e: self._rollback_op())
        self.op_list.bind("<Button-1>", lambda _e: self.op_list.focus_set(), add="+")

        op_btn_row = tk.Frame(right, bg=C["surface"])
        op_btn_row.pack(fill=tk.X, pady=(8, 0))
        _flat_btn(op_btn_row, "回撤选中记录", self._rollback_op, variant="secondary", icon=IC["dock"]).pack(side=tk.LEFT)

        foot = tk.Frame(self, bg=C["canvas"])
        foot.pack(fill=tk.X, padx=16, pady=(0, 16))
        _flat_btn(foot, "关闭", self._close, variant="secondary").pack(side=tk.RIGHT)

        self._reload_list()
        if self.listbox.size():
            self.listbox.selection_set(0)
            self._on_select()
        self.after_idle(self._fit_initial_window)

    def _fit_initial_window(self):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        parent = self.master
        try:
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
        except tk.TclError:
            px = py = 0
            pw = ph = 0
        req_w = max(self.winfo_reqwidth(), 980)
        req_h = max(self.winfo_reqheight(), 720)
        w = min(req_w + 28, sw - 20)
        h = min(req_h + 36, sh - 40)
        w = max(w, 760)
        h = max(h, 560)
        if pw > 0 and ph > 0:
            x = px + max(0, (pw - w) // 2)
            y = py + max(0, (ph - h) // 2)
        else:
            x = max(0, (sw - w) // 2)
            y = max(0, (sh - h) // 2)
        if x + w > sw:
            x = max(0, sw - w - 12)
        if y + h > sh:
            y = max(0, sh - h - 12)
        self.geometry("%dx%d+%d+%d" % (w, h, x, y))
        for canvas in (getattr(self, "_left_canvas", None),):
            if canvas is not None:
                canvas.configure(scrollregion=canvas.bbox("all"))

    def _format_preview_json(self):
        if self._syncing_preview:
            return
        raw = self._preview_json_text().strip()
        if not raw:
            return
        try:
            body = json.loads(raw)
            pretty = json.dumps(body, ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            self._dirty = True
            self.edit_status.configure(text="JSON 无效", fg=C["error"])
            return
        if pretty == raw:
            self._dirty = True
            self.edit_status.configure(text="有未保存修改", fg=C["error"])
            return
        cursor = self.preview.index(tk.INSERT)
        self._syncing_preview = True
        self.preview.edit_separator()
        self.preview.delete("1.0", tk.END)
        self.preview.insert("1.0", pretty)
        try:
            self.preview.mark_set(tk.INSERT, cursor)
        except tk.TclError:
            self.preview.mark_set(tk.INSERT, tk.END)
        self.preview.edit_separator()
        self.preview.edit_modified(False)
        self._syncing_preview = False
        self._dirty = True
        self.edit_status.configure(text="已格式化", fg=C["success"])

    def _selected_name(self):
        sel = self.listbox.curselection()
        if not sel:
            return None
        return self.listbox.get(sel[0])

    def _filtered_names(self):
        keyword = self._filter_var.get().strip().lower()
        names = list(self.app.templates.keys())
        if not keyword:
            return names
        return [n for n in names if keyword in n.lower()]

    def _reload_list(self, select=None):
        prev = self._selected_name()
        target = select or prev or self._editing_name
        self.listbox.delete(0, tk.END)
        names = self._filtered_names()
        for n in names:
            self.listbox.insert(tk.END, n)
        total = len(self.app.templates)
        shown = len(names)
        if shown == total:
            self.count_label.configure(text="共 %d 个模版" % total)
        else:
            self.count_label.configure(text="显示 %d / %d 个模版" % (shown, total))
        if target and target in names:
            idx = names.index(target)
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(idx)
            self.listbox.see(idx)
        elif names:
            self.listbox.selection_set(0)
        if not self._dirty:
            self._load_preview()

    def _preview_json_text(self):
        return self.preview.get("1.0", "end-1c")

    def _push_op(self, action, name, before_body, extra=""):
        self._op_log.insert(
            0,
            {
                "time": time.strftime("%H:%M:%S"),
                "action": action,
                "name": name,
                "before": copy.deepcopy(before_body) if before_body is not None else None,
                "extra": extra,
            },
        )
        self._op_log = self._op_log[:50]
        self._render_op_log()

    def _render_op_log(self, keep_idx=None):
        sel = keep_idx
        if sel is None:
            cur = self.op_list.curselection()
            sel = cur[0] if cur else None
        self.op_list.delete(0, tk.END)
        for item in self._op_log:
            label = "%s  %s · %s" % (item["time"], item["action"], item["name"])
            if item.get("extra"):
                label += " (%s)" % item["extra"]
            self.op_list.insert(tk.END, label)
        if sel is not None and sel < self.op_list.size():
            self.op_list.selection_set(sel)
            self.op_list.see(sel)

    def _rollback_op(self):
        sel = self.op_list.curselection()
        if not sel:
            messagebox.showinfo("提示", "请先选中一条操作记录", parent=self)
            return
        item = self._op_log[sel[0]]
        name = item["name"]
        action = item["action"]
        if not messagebox.askyesno("回撤", "确定回撤「%s %s · %s」？" % (item["time"], action, name), parent=self):
            return
        if action == "新建":
            if name in self.app.templates:
                del self.app.templates[name]
            select = None
        elif action == "重命名":
            old = item.get("extra") or name
            if name in self.app.templates:
                del self.app.templates[name]
            self.app.templates[old] = copy.deepcopy(item["before"])
            select = old
        elif action == "删除":
            self.app.templates[name] = copy.deepcopy(item["before"])
            select = name
        else:
            if name not in self.app.templates:
                messagebox.showerror("回撤失败", "模版不存在: %s" % name, parent=self)
                return
            self.app.templates[name] = copy.deepcopy(item["before"])
            select = name
        self.app._persist_templates()
        self.app._refresh_template_combo(select or (next(iter(self.app.templates), None)))
        self._filter_var.set("")
        self._reload_list(select)
        self.app._append_log("已回撤模版操作: %s · %s" % (action, name))
        messagebox.showinfo("已回撤", "已恢复到 %s 之前" % action, parent=self)

    def _load_preview(self):
        name = self._selected_name()
        self._editing_name = name
        self._syncing_preview = True
        self.preview.delete("1.0", tk.END)
        if name and name in self.app.templates:
            text = json.dumps(self.app.templates[name], ensure_ascii=False, indent=2)
            self.preview.insert("1.0", text)
        self.preview.edit_modified(False)
        self.preview.edit_reset()
        self._syncing_preview = False
        self._dirty = False
        self.edit_status.configure(text="")
        self.preview.focus_set()

    def _restore_list_selection(self):
        if not self._editing_name:
            return
        names = self._filtered_names()
        if self._editing_name not in names:
            return
        if self._selected_name() == self._editing_name:
            return
        idx = names.index(self._editing_name)
        self.listbox.selection_clear(0, tk.END)
        self.listbox.selection_set(idx)
        self.listbox.see(idx)

    def _on_select(self, _event=None):
        if self.focus_get() == self.op_list:
            return
        name = self._selected_name()
        if not name:
            self._restore_list_selection()
            return
        if name == self._editing_name:
            return
        if self._dirty:
            if not messagebox.askyesno("未保存", "当前编辑未保存，是否放弃修改？", parent=self):
                self._restore_list_selection()
                return
        self._load_preview()

    def _on_preview_edit(self, _event=None):
        if self._syncing_preview:
            self.preview.edit_modified(False)
            return
        if self.preview.edit_modified():
            self._dirty = True
            self.edit_status.configure(text="有未保存修改", fg=C["error"])
            self.preview.edit_modified(False)

    def _save_json_edit(self):
        name = self._selected_name()
        if not name:
            messagebox.showinfo("提示", "请先选中模版", parent=self)
            return
        raw = self._preview_json_text().strip()
        if not raw:
            messagebox.showerror("保存失败", "JSON 不能为空", parent=self)
            return
        try:
            body = json.loads(raw)
        except json.JSONDecodeError as e:
            messagebox.showerror("保存失败", "JSON 格式错误:\n%s" % e, parent=self)
            return
        if not isinstance(body, dict):
            messagebox.showerror("保存失败", "模版内容必须是 JSON 对象", parent=self)
            return
        before = copy.deepcopy(self.app.templates.get(name))
        self.app.templates[name] = body
        self.app._persist_templates()
        self.app._refresh_template_combo(name)
        self._push_op("保存编辑", name, before)
        self._load_preview()
        self.edit_status.configure(text="已保存右侧编辑", fg=C["success"])
        self.app._append_log("已保存模版(右侧编辑): " + name)

    def _revert_json_edit(self):
        self._load_preview()

    def _create_new(self):
        name = simpledialog.askstring("新建模版", "模版名称", parent=self)
        if not name:
            return
        name = name.strip()
        if not name:
            return
        if name in self.app.templates:
            messagebox.showerror("失败", "名称已存在", parent=self)
            return
        self.app.templates[name] = {"name": "newMessage", "sn": "", "muid": "", "timestamp": "", "version": "v2.0.0", "data": {}}
        self.app._persist_templates()
        self.app._refresh_template_combo(name)
        self._push_op("新建", name, None)
        self._filter_var.set("")
        self._reload_list(name)
        self.app._append_log("已新建模版: " + name)

    def _save_from_tab(self):
        name = self._selected_name()
        if not name:
            messagebox.showinfo("提示", "请先选中模版", parent=self)
            return
        try:
            body = self.app.active_tab().read_json()
        except Exception as e:
            messagebox.showerror("保存失败", str(e), parent=self)
            return
        before = copy.deepcopy(self.app.templates.get(name))
        self.app.templates[name] = body
        self.app._persist_templates()
        self.app._refresh_template_combo(name)
        self._push_op("窗口保存", name, before)
        self._reload_list(name)
        self.app._append_log("已从当前窗口保存模版: " + name)

    def _apply(self):
        name = self._selected_name()
        if not name:
            return
        self.app.apply_template(name)
        self.app._refresh_template_combo(name)
        self.app._append_log("已应用模版: " + name)

    def _rename(self):
        old = self._selected_name()
        if not old:
            return
        name = simpledialog.askstring("重命名", "新名称", initialvalue=old, parent=self)
        if not name:
            return
        name = name.strip()
        if not name or name == old:
            return
        if name in self.app.templates:
            messagebox.showerror("失败", "名称已存在", parent=self)
            return
        before = copy.deepcopy(self.app.templates.get(old))
        self.app.templates[name] = self.app.templates.pop(old)
        self.app._persist_templates()
        self.app._refresh_template_combo(name)
        self._push_op("重命名", name, before, extra=old)
        self._reload_list(name)
        self.app._append_log("模版已重命名: %s -> %s" % (old, name))

    def _delete(self):
        name = self._selected_name()
        if not name:
            return
        if len(self.app.templates) <= 1:
            messagebox.showerror("删除失败", "至少保留一个模版", parent=self)
            return
        if not messagebox.askyesno("删除模版", "确定删除「%s」？" % name, parent=self):
            return
        before = copy.deepcopy(self.app.templates.get(name))
        del self.app.templates[name]
        self.app._persist_templates()
        self.app._refresh_template_combo()
        self._push_op("删除", name, before)
        self._reload_list()
        self.app._append_log("已删除模版: " + name)

    def _close(self):
        if self._dirty:
            if not messagebox.askyesno("未保存", "当前编辑未保存，确定关闭？", parent=self):
                return
        self.destroy()


class MqttToolApp:
    def __init__(
        self,
        root,
        initial_tab_raw=None,
        initial_tab_title=None,
        initial_connection=None,
        parent_app=None,
        window_subtitle=None,
    ):
        self.root = root
        self.parent_app = parent_app
        self._window_subtitle = window_subtitle
        self.root.title("MQTT 发送工具")
        self.root.geometry("1100x920")
        self.root.minsize(900, 680)
        self.root.configure(bg=C["canvas"])

        self._tab_counter = 0
        self._tabs = []
        self._active_tab_idx = 0
        self._child_apps = []
        self._history_widgets = {}
        self._log_viewer = None
        self._toast_win = None
        self._toast_job = None
        self.templates_path = os.path.join(_app_dir(), "templates.json")
        self.history_path = os.path.join(_app_dir(), "history.json")
        self.session_path = os.path.join(_app_dir(), "session.json")
        self.templates = self._load_templates()
        self.history = self._load_history()

        self._setup_styles()
        self._build_ui()

        session_applied = False
        session = None
        if initial_connection:
            self._apply_initial_connection(initial_connection)

        if initial_tab_raw is not None:
            if initial_tab_title:
                try:
                    self._tab_counter = int(initial_tab_title.replace("窗口", "").strip())
                except ValueError:
                    self._tab_counter = max(self._tab_counter, 1)
            self.add_payload_tab(initial_tab_title or "窗口 1")
            self.active_tab().fill_raw(initial_tab_raw)
        elif self.parent_app is None:
            session = self._load_session()
            if session and session.get("tabs"):
                self._apply_session(session)
                session_applied = True
        if not session_applied and initial_tab_raw is None:
            start = DEFAULT_TEMPLATE if DEFAULT_TEMPLATE in self.templates else next(iter(self.templates))
            self.template_combo.set(start)
            self.add_payload_tab("窗口 1")
            self.apply_template(start)

        if self.parent_app is None:
            self.root.protocol("WM_DELETE_WINDOW", self._on_main_close)

        if not (session_applied and session and session.get("geometry")):
            self.root.after_idle(self._fit_initial_window)

    def _fit_initial_window(self):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        req_w = max(self.root.winfo_reqwidth(), 980)
        req_h = max(self.root.winfo_reqheight(), 760)
        w = min(req_w + 32, sw - 24)
        h = min(req_h + 40, sh - 48)
        w = max(w, 900)
        h = max(h, 680)
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h) // 2)
        self.root.geometry("%dx%d+%d+%d" % (w, h, x, y))
        if getattr(self, "_sidebar_canvas", None):
            self._sidebar_canvas.configure(scrollregion=self._sidebar_canvas.bbox("all"))

    def _load_session(self):
        if not os.path.isfile(self.session_path):
            return None
        try:
            with open(self.session_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and isinstance(data.get("tabs"), list) and data["tabs"]:
                return data
        except Exception:
            pass
        return None

    def _collect_session_state(self):
        return {
            "version": 1,
            "geometry": self.root.geometry(),
            "connection": {
                "host": self._resolve_host(self.host.get()),
                "port": self.port.get().strip(),
                "user": self.user.get().strip(),
                "topic": self.topic.get().strip(),
                "pwd": self.pwd.get(),
            },
            "options": {
                "auto_sign": bool(self.auto_sign.get()),
                "auto_trigger_time": bool(self.auto_trigger_time.get()),
                "sync_sn": bool(self.sync_sn.get()),
                "pwd_show": bool(self.pwd_show.get()),
            },
            "template": self.template_combo.get().strip(),
            "tab_counter": self._tab_counter,
            "active_tab": self._active_tab_idx,
            "tabs": [{"title": t.title, "raw": t.get_raw_text()} for t in self._tabs],
        }

    def _save_session(self):
        if self.parent_app is not None:
            return
        with open(self.session_path, "w", encoding="utf-8") as f:
            json.dump(self._collect_session_state(), f, ensure_ascii=False, indent=2)

    def _apply_session(self, session):
        conn = session.get("connection") or {}
        self._apply_initial_connection(conn)
        opts = session.get("options") or {}
        self.auto_sign.set(opts.get("auto_sign", True))
        self.auto_trigger_time.set(opts.get("auto_trigger_time", True))
        self.sync_sn.set(opts.get("sync_sn", True))
        self.pwd_show.set(opts.get("pwd_show", False))
        self._toggle_pwd()
        tpl = (session.get("template") or "").strip()
        if tpl and tpl in self.templates:
            self.template_combo.set(tpl)
        try:
            self._tab_counter = int(session.get("tab_counter") or 0)
        except (TypeError, ValueError):
            self._tab_counter = len(session.get("tabs") or [])
        while self._tabs:
            tab = self._tabs.pop()
            tab.frame.destroy()
        self._active_tab_idx = 0
        for item in session.get("tabs") or []:
            title = (item.get("title") or "").strip() or None
            tab = self.add_payload_tab(title)
            raw = item.get("raw") or ""
            if str(raw).strip():
                tab.fill_raw(str(raw))
        if not self._tabs:
            self.add_payload_tab("窗口 1")
        active = session.get("active_tab", 0)
        try:
            active = int(active)
        except (TypeError, ValueError):
            active = 0
        if active < 0 or active >= len(self._tabs):
            active = max(0, len(self._tabs) - 1)
        self._select_tab(active)
        geo = session.get("geometry")
        if geo:
            self.root.after_idle(lambda g=geo: self.root.geometry(g))

    def _on_main_close(self):
        try:
            self._save_session()
        except Exception:
            pass
        self.root.destroy()

    def _apply_initial_connection(self, conn):
        if conn.get("host"):
            host = conn["host"].strip()
            self.host.set(self._host_label(host))
        if conn.get("port"):
            self.port.set(conn["port"])
        if conn.get("user"):
            self.user.set(conn["user"])
        if conn.get("topic"):
            self.topic.set(conn["topic"])
        if conn.get("pwd") is not None:
            self.pwd.delete(0, tk.END)
            self.pwd.insert(0, conn["pwd"])

    def _setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=C["canvas"])
        style.configure("TNotebook", background=C["surface"], borderwidth=0, tabmargins=[0, 0, 0, 0])
        style.configure(
            "TNotebook.Tab",
            background=C["surface_alt"],
            foreground=C["muted"],
            padding=[14, 8],
            font=C["ui"],
            borderwidth=0,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", C["surface"])],
            foreground=[("selected", C["accent"])],
            expand=[("selected", [1, 1, 1, 0])],
        )
        style.configure("TCombobox", fieldbackground=C["surface_alt"], padding=6)
        style.configure("TEntry", fieldbackground=C["surface_alt"], padding=6)
        style.configure("TCheckbutton", background=C["canvas"], foreground=C["text"], font=C["ui"])
        style.configure("Vertical.TScrollbar", background=C["surface_alt"], troughcolor=C["surface"])

    def _build_header(self):
        header = tk.Frame(self.root, bg=C["header_bg"], height=92)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Frame(header, bg=C["header_bg2"], height=1).pack(side=tk.TOP, fill=tk.X)
        inner = tk.Frame(header, bg=C["header_bg"])
        inner.pack(fill=tk.BOTH, expand=True, padx=24, pady=(14, 10))
        title_row = tk.Frame(inner, bg=C["header_bg"])
        title_row.pack(fill=tk.X)
        badge = tk.Frame(title_row, bg=C["accent"], width=46, height=46)
        badge.pack_propagate(False)
        badge.pack(side=tk.LEFT, padx=(0, 14))
        tk.Label(badge, text=_icon_text(IC["brand"], "M"), font=_icon_font(20), fg="#FFFFFF", bg=C["accent"]).pack(expand=True)
        title_block = tk.Frame(title_row, bg=C["header_bg"])
        title_block.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(title_block, text="MQTT 发送工具", font=C["hero"], fg=C["header_fg"], bg=C["header_bg"], anchor=tk.W).pack(fill=tk.X)
        self._subtitle_label = tk.Label(
            title_block,
            text=self._window_subtitle or "博享家设备上行 · 多窗口编辑 · 自动签名",
            font=C["hero_sub"],
            fg=C["header_sub"],
            bg=C["header_bg"],
            anchor=tk.W,
        )
        self._subtitle_label.pack(fill=tk.X, pady=(2, 0))
        if self.parent_app:
            _flat_btn(
                title_row,
                "收回主界面",
                self._dock_to_parent,
                variant="outline",
                icon=IC["dock"],
                padx=14,
                pady=8,
            ).pack(side=tk.RIGHT)
        tk.Frame(header, bg=C["accent_glow"], height=3).pack(side=tk.BOTTOM, fill=tk.X)

    def _dock_to_parent(self):
        parent = self.parent_app
        if not parent:
            return
        try:
            if not parent.root.winfo_exists():
                messagebox.showerror("无法收回", "主窗口已关闭", parent=self.root)
                return
        except tk.TclError:
            return
        tabs_data = [(t.title, t.get_raw_text()) for t in self._tabs]
        if not tabs_data:
            if self in parent._child_apps:
                parent._child_apps.remove(self)
            self.root.destroy()
            return
        for title, raw in tabs_data:
            try:
                n = int(title.replace("窗口", "").strip())
                parent._tab_counter = max(parent._tab_counter, n)
            except ValueError:
                pass
        first_idx = len(parent._tabs)
        for title, raw in tabs_data:
            tab = parent.add_payload_tab(title)
            tab.fill_raw(raw)
        parent._select_tab(first_idx)
        parent._append_log("已收回 %d 个发送窗口到主界面" % len(tabs_data))
        if self in parent._child_apps:
            parent._child_apps.remove(self)
        self.root.destroy()
        try:
            parent.root.lift()
            parent.root.focus_force()
        except tk.TclError:
            pass

    def _build_ui(self):
        self._build_header()
        outer = tk.Frame(self.root, bg=C["canvas"], padx=20, pady=18)
        outer.pack(fill=tk.BOTH, expand=True)

        body = tk.Frame(outer, bg=C["canvas"])
        body.pack(fill=tk.BOTH, expand=True)

        sidebar_scroll, sidebar, self._sidebar_canvas = _scrollable_frame(body, width=C["sidebar_w"])
        sidebar_scroll.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 14))

        conn_wrap, conn = _card(sidebar, pad=16, accent=True)
        conn_wrap.pack(fill=tk.X, pady=(0, 12))
        _section_head(conn, "连接", "Broker 与主题", icon=IC["connection"])

        self.host = self._add_host_field(conn, "192.168.110.19")
        self.port = self._add_history_field(conn, "port", "Port", "1883")
        self.user = self._add_history_field(conn, "user", "User", "test")

        _field_label(conn, "Password")
        pwd_wrap = tk.Frame(conn, bg=C["surface"])
        pwd_wrap.pack(fill=tk.X, pady=(0, 10))
        self.pwd = ttk.Entry(pwd_wrap, show="*", font=C["ui"])
        self.pwd.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
        self.pwd.insert(0, "Tt4@0#kA8")
        self.pwd_show = tk.BooleanVar(value=False)
        tk.Checkbutton(
            pwd_wrap,
            text="显示",
            variable=self.pwd_show,
            command=self._toggle_pwd,
            bg=C["surface"],
            fg=C["muted"],
            activebackground=C["surface"],
            selectcolor=C["surface_alt"],
            font=C["ui_sm"],
        ).pack(side=tk.LEFT, padx=(8, 0))

        self.topic = self._add_history_field(conn, "topic", "主题 Topic", "cloud/TD0TD204FC3T9751")

        tpl_wrap, tpl = _card(sidebar, pad=16, accent=True)
        tpl_wrap.pack(fill=tk.X)
        _section_head(tpl, "模版", "快速载入报文结构", icon=IC["template"])

        _field_label(tpl, "选择模版")
        self.template_combo = ttk.Combobox(tpl, state="readonly", values=list(self.templates.keys()), font=C["ui"])
        self.template_combo.pack(fill=tk.X, pady=(0, 10))

        _flat_btn(tpl, "应用到当前窗口", self._apply_selected_template, variant="primary", icon=IC["apply"]).pack(fill=tk.X, pady=(0, 6))
        row_tpl = tk.Frame(tpl, bg=C["surface"])
        row_tpl.pack(fill=tk.X)
        _flat_btn(row_tpl, "新增", self._create_template_quick, variant="outline", icon=IC["add"], padx=10).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        _flat_btn(row_tpl, "管理", self._open_template_manager, variant="secondary", icon=IC["manage"], padx=10).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))

        main = tk.Frame(body, bg=C["canvas"])
        main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        payload_wrap, payload = _card(main, pad=14, fill=tk.BOTH, expand=True)
        payload_wrap.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        top_bar = tk.Frame(payload, bg=C["surface"])
        top_bar.pack(fill=tk.X, pady=(0, 8))
        title_left = tk.Frame(top_bar, bg=C["surface"])
        title_left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        title_row2 = tk.Frame(title_left, bg=C["surface"])
        title_row2.pack(fill=tk.X)
        badge2 = tk.Frame(title_row2, bg=C["accent_soft"], width=26, height=26)
        badge2.pack_propagate(False)
        badge2.pack(side=tk.LEFT, padx=(0, 8))
        tk.Label(badge2, text=_icon_text(IC["payload"], "{}"), font=_icon_font(11), fg=C["accent"], bg=C["accent_soft"]).pack(expand=True)
        tk.Label(title_row2, text="发送内容", font=C["section"], fg=C["text"], bg=C["surface"]).pack(side=tk.LEFT)
        tk.Label(title_left, text="双击标签可重命名 · 拖拽分离 · 独立窗口可收回", font=C["ui_sm"], fg=C["muted"], bg=C["surface"]).pack(anchor=tk.W, pady=(4, 0))

        self.tab_row = tk.Frame(payload, bg=C["surface_alt"], highlightbackground=C["border"], highlightthickness=1)
        self.tab_row.pack(fill=tk.X, pady=(0, 0))
        self.tab_bar = tk.Frame(self.tab_row, bg=C["surface_alt"])
        self.tab_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4, pady=4)
        self.tab_plus = tk.Frame(self.tab_row, bg=C["accent"], cursor="hand2")
        self.tab_plus.pack(side=tk.RIGHT, padx=6, pady=6)
        self._tab_plus_lbl = tk.Label(
            self.tab_plus,
            text=_icon_text(IC["add"], "+"),
            font=_icon_font(14),
            fg="#FFFFFF",
            bg=C["accent"],
            padx=10,
            pady=4,
            cursor="hand2",
        )
        self._tab_plus_lbl.pack()
        for w in (self.tab_plus, self._tab_plus_lbl):
            w.bind("<Button-1>", lambda e: self.add_payload_tab())
            w.bind("<Enter>", lambda e: (self.tab_plus.configure(bg=C["accent_hover"]), self._tab_plus_lbl.configure(bg=C["accent_hover"])))
            w.bind("<Leave>", lambda e: (self.tab_plus.configure(bg=C["accent"]), self._tab_plus_lbl.configure(bg=C["accent"])))
        tk.Frame(payload, bg=C["border"], height=1).pack(fill=tk.X)

        self.content_stack = tk.Frame(payload, bg=C["surface"])
        self.content_stack.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

        act_wrap, act = _card(main, pad=14)
        act_wrap.pack(fill=tk.X, pady=(0, 12))
        self.auto_sign = tk.BooleanVar(value=True)
        self.auto_trigger_time = tk.BooleanVar(value=True)
        self.sync_sn = tk.BooleanVar(value=True)
        opts = tk.Frame(act, bg=C["surface"])
        opts.pack(side=tk.LEFT, fill=tk.X, expand=True)
        for text, var in (
            ("自动 muid + sign", self.auto_sign),
            ("触发时间取当前", self.auto_trigger_time),
            ("sn 跟随主题", self.sync_sn),
        ):
            tk.Checkbutton(
                opts,
                text=text,
                variable=var,
                bg=C["surface"],
                fg=C["text"],
                activebackground=C["surface"],
                selectcolor=C["accent_soft"],
                font=C["ui"],
            ).pack(side=tk.LEFT, padx=(0, 18))
        self.send_btn = _flat_btn(act, "发送当前窗口", self._send, variant="primary", icon=IC["send"], padx=22, pady=10)
        self.send_btn.pack(side=tk.RIGHT)

        log_wrap, log_box = _card(main, pad=12, accent=True)
        log_wrap.pack(fill=tk.X)
        log_title_row = tk.Frame(log_box, bg=C["surface"])
        log_title_row.pack(fill=tk.X)
        _section_head(log_title_row, "运行日志", "发送结果与错误信息", icon=IC["log"])
        log_actions = tk.Frame(log_box, bg=C["surface"])
        log_actions.pack(fill=tk.X, pady=(0, 8))
        tk.Label(log_actions, text=_icon_text(IC["search"], "搜"), font=_icon_font(12), fg=C["muted"], bg=C["surface"]).pack(side=tk.LEFT)
        self.log_search_var = tk.StringVar()
        self.log_search_entry = ttk.Entry(log_actions, textvariable=self.log_search_var, font=C["ui"], width=24)
        self.log_search_entry.pack(side=tk.LEFT, padx=(6, 6), fill=tk.X, expand=True)
        self.log_search_entry.bind("<Return>", lambda e: self._log_search_next())
        _flat_btn(log_actions, "查找", self._log_search_next, variant="ghost", icon=IC["search"], padx=8, pady=4).pack(side=tk.LEFT, padx=(0, 6))
        _flat_btn(log_actions, "放大查看", self._open_log_viewer, variant="outline", icon=IC["log"], padx=10, pady=6).pack(side=tk.RIGHT)
        self._log_hits = []
        self._log_hit_idx = 0
        log_text_wrap = tk.Frame(log_box, bg=C["surface"])
        log_text_wrap.pack(fill=tk.X)
        self.log = _styled_text(
            log_text_wrap,
            height=6,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg=C["log_bg"],
            fg=C["text"],
            font=C["mono_fallback"],
        )
        log_vscroll = ttk.Scrollbar(log_text_wrap, orient=tk.VERTICAL, command=self.log.yview)
        self.log.configure(yscrollcommand=log_vscroll.set)
        self.log.tag_configure("log_hit", background="#FEF3C7")
        self.log.tag_configure("log_ok", foreground=C["success"])
        self.log.tag_configure("log_err", foreground=C["error"])
        self.log.tag_configure("log_info", foreground=C["text"])
        self.log.tag_configure("log_detail", foreground=C["muted"])
        self.log.tag_configure("log_sep", foreground=C["border"])
        self.log.pack(side=tk.LEFT, fill=tk.X, expand=True)
        log_vscroll.pack(side=tk.RIGHT, fill=tk.Y)

    def _add_history_field(self, parent, key, label, default, width=None):
        _field_label(parent, label)
        row = tk.Frame(parent, bg=C["surface"])
        row.pack(fill=tk.X, pady=(0, 10))
        values = self.history.get(key) or [default]
        combo = ttk.Combobox(row, values=values, font=C["ui"])
        if width:
            combo.configure(width=width)
        combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        combo.set(values[0] if values else default)
        del_btn = _flat_btn(row, "×", lambda k=key: self._delete_history(k), variant="ghost", padx=6, pady=4)
        del_btn.pack(side=tk.RIGHT, padx=(6, 0))
        del_btn.configure(width=2, font=("Segoe UI", 11))
        self._history_widgets[key] = combo
        self._bind_history_combo(combo, key)
        return combo

    def _host_label(self, host):
        host = (host or "").strip()
        if not host:
            return ""
        alias = (self.history.get("host_alias") or {}).get(host, "").strip()
        return ("%s · %s" % (alias, host)) if alias else host

    def _resolve_host(self, value):
        value = (value or "").strip()
        if not value:
            return ""
        if " · " in value:
            return value.rsplit(" · ", 1)[-1].strip()
        return value

    def _refresh_host_combo(self, keep_host=None):
        combo = self._history_widgets.get("host")
        if not combo:
            return
        hosts = list(self.history.get("host") or [])
        labels = [self._host_label(h) for h in hosts]
        combo.configure(values=labels)
        target = keep_host or self._resolve_host(combo.get())
        if target and target in hosts:
            combo.set(self._host_label(target))
        elif labels:
            combo.set(labels[0])

    def _add_host_field(self, parent, default):
        _field_label(parent, "Host")
        row = tk.Frame(parent, bg=C["surface"])
        row.pack(fill=tk.X, pady=(0, 10))
        hosts = self.history.get("host") or [default]
        labels = [self._host_label(h) for h in hosts]
        combo = ttk.Combobox(row, values=labels, font=C["ui"])
        combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        combo.set(labels[0] if labels else default)
        _flat_btn(row, "别名", self._set_host_alias, variant="ghost", padx=8, pady=4).pack(side=tk.RIGHT, padx=(6, 0))
        del_btn = _flat_btn(row, "×", lambda: self._delete_history("host"), variant="ghost", padx=6, pady=4)
        del_btn.pack(side=tk.RIGHT, padx=(6, 0))
        del_btn.configure(width=2, font=("Segoe UI", 11))
        self._history_widgets["host"] = combo
        self._bind_history_combo(combo, "host")
        return combo

    def _set_host_alias(self):
        host = self._resolve_host(self.host.get())
        if not host:
            messagebox.showinfo("提示", "请先选择或输入 Host", parent=self.root)
            return
        current = (self.history.get("host_alias") or {}).get(host, "")
        alias = simpledialog.askstring(
            "Host 别名",
            "为 %s 设置别名（留空则清除）" % host,
            initialvalue=current,
            parent=self.root,
        )
        if alias is None:
            return
        alias = alias.strip()
        if "host_alias" not in self.history or not isinstance(self.history["host_alias"], dict):
            self.history["host_alias"] = {}
        if alias:
            self.history["host_alias"][host] = alias
        elif host in self.history["host_alias"]:
            del self.history["host_alias"][host]
        self._remember("host", host)
        self._refresh_host_combo(keep_host=host)
        self._append_log("Host 别名已更新: %s" % self._host_label(host))

    def _on_tab_content_change(self):
        tab = self.active_tab()
        if tab:
            tab.schedule_format(self.root)

    def _on_tab_sn_change(self, sn):
        self._set_topic_sn(sn)

    def _is_auto_tab_title(self, title):
        return bool(re.match(r"^窗口\s*\d+$", (title or "").strip()))

    def _unique_tab_title(self, base, exclude_idx=None):
        base = (base or "").strip() or "未命名"
        taken = {t.title for i, t in enumerate(self._tabs) if i != exclude_idx}
        if base not in taken:
            return base
        n = 2
        while "%s (%d)" % (base, n) in taken:
            n += 1
        return "%s (%d)" % (base, n)

    def _update_window_caption(self):
        tab = self.active_tab()
        if not tab:
            return
        if self.parent_app:
            self.root.title("MQTT · %s" % tab.title)
            self._window_subtitle = "独立实例 · %s" % tab.title
        if hasattr(self, "_subtitle_label"):
            self._subtitle_label.configure(
                text=self._window_subtitle or "博享家设备上行 · 多窗口编辑 · 自动签名"
            )

    def _rename_tab(self, idx):
        if idx < 0 or idx >= len(self._tabs):
            return
        tab = self._tabs[idx]
        new = simpledialog.askstring(
            "重命名窗口",
            "输入窗口名称，便于区分多个编辑窗口",
            initialvalue=tab.title,
            parent=self.root,
        )
        if new is None:
            return
        new = new.strip()
        if not new or new == tab.title:
            return
        if any(i != idx and t.title == new for i, t in enumerate(self._tabs)):
            messagebox.showerror("失败", "该名称已被其他窗口使用", parent=self.root)
            return
        tab.title = new
        self._render_tab_bar()
        if idx == self._active_tab_idx:
            self._update_window_caption()
        self._append_log("窗口已重命名: " + new)

    def _tab_context_menu(self, idx):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="重命名", command=lambda: self._rename_tab(idx))
        if len(self._tabs) > 1:
            menu.add_command(label="关闭", command=lambda: self._close_tab(idx))
            menu.add_separator()
            menu.add_command(label="分离为独立窗口", command=lambda: self._detach_tab(idx))
        else:
            menu.add_command(label="关闭", state=tk.DISABLED)
        return menu

    def _render_tab_bar(self):
        for w in self.tab_bar.winfo_children():
            w.destroy()
        for i, tab in enumerate(self._tabs):
            active = i == self._active_tab_idx
            chip_bg = C["surface"] if active else C["canvas"]
            chip_fg = C["accent"] if active else C["muted"]
            chip_border = C["accent"] if active else C["border"]
            chip = tk.Frame(
                self.tab_bar,
                bg=chip_bg,
                highlightbackground=chip_border,
                highlightthickness=2 if active else 1,
            )
            chip.pack(side=tk.LEFT, padx=(0, 6), pady=2)
            tab.chip = chip

            lbl = tk.Label(
                chip,
                text=tab.title,
                font=C["ui_bold"] if active else C["ui"],
                fg=chip_fg,
                bg=chip_bg,
                padx=10,
                pady=6,
                cursor="hand2",
            )
            lbl.pack(side=tk.LEFT)

            edit = tk.Label(
                chip,
                text=_icon_text(IC["edit"], "✎"),
                font=_icon_font(11),
                fg=C["muted"] if not active else C["accent"],
                bg=chip_bg,
                padx=4,
                pady=4,
                cursor="hand2",
            )
            edit.pack(side=tk.LEFT)

            def _edit_click(e, rename_idx=i):
                self._rename_tab(rename_idx)
                return "break"

            edit.bind("<Button-1>", _edit_click)
            edit.bind("<Enter>", lambda e, w=edit: w.configure(fg=C["accent"]))
            edit.bind("<Leave>", lambda e, w=edit, a=active: w.configure(fg=C["accent"] if a else C["muted"]))

            def _dbl_rename(e, rename_idx=i):
                self._rename_tab(rename_idx)
                return "break"

            lbl.bind("<Double-Button-1>", _dbl_rename)

            menu = self._tab_context_menu(i)

            def _popup(e, m=menu):
                m.tk_popup(e.x_root, e.y_root)
                return "break"

            chip.bind("<Button-3>", _popup)
            lbl.bind("<Button-3>", _popup)

            self._bind_tab_drag(chip, lbl, edit, i, active)

            if len(self._tabs) > 1:
                close = tk.Label(
                    chip,
                    text=_icon_text(IC["close"], "×"),
                    font=_icon_font(10),
                    fg=C["muted"] if not active else C["accent"],
                    bg=chip_bg,
                    padx=6,
                    pady=4,
                    cursor="hand2",
                )
                close.pack(side=tk.LEFT, padx=(0, 4))

                def _close_click(e, close_idx=i):
                    self._close_tab(close_idx)
                    return "break"

                close.bind("<Button-1>", _close_click)
                close.bind("<Enter>", lambda e, w=close: w.configure(fg=C["error"]))
                close.bind("<Leave>", lambda e, w=close, a=active: w.configure(fg=C["accent"] if a else C["muted"]))

    def _bind_tab_drag(self, chip, lbl, edit, idx, active):
        drag = {"moved": False, "sx": 0, "sy": 0}
        border = C["accent"] if active else C["border"]

        def _press(e):
            drag["sx"] = e.x_root
            drag["sy"] = e.y_root
            drag["moved"] = False

        def _motion(e):
            if abs(e.x_root - drag["sx"]) + abs(e.y_root - drag["sy"]) > 18:
                drag["moved"] = True
                chip.configure(highlightbackground=C["accent"], highlightthickness=2)

        def _release(e):
            chip.configure(highlightbackground=border, highlightthickness=2 if active else 1)
            if drag["moved"]:
                self._detach_tab(idx)
            else:
                self._select_tab(idx)

        for w in (chip, lbl):
            w.bind("<ButtonPress-1>", _press)
            w.bind("<B1-Motion>", _motion)
            w.bind("<ButtonRelease-1>", _release)

    def _remove_tab_at(self, idx):
        tab = self._tabs.pop(idx)
        tab.frame.destroy()
        if self._active_tab_idx >= len(self._tabs):
            self._active_tab_idx = max(0, len(self._tabs) - 1)
        elif idx < self._active_tab_idx:
            self._active_tab_idx -= 1
        for t in self._tabs:
            t.hide()
        if self._tabs:
            self._tabs[self._active_tab_idx].show()
        self._render_tab_bar()

    def _detach_tab(self, idx):
        if idx < 0 or idx >= len(self._tabs):
            return
        if len(self._tabs) <= 1:
            messagebox.showinfo("提示", "至少保留一个窗口在主界面", parent=self.root)
            return
        tab = self._tabs[idx]
        raw = tab.get_raw_text()
        title = tab.title
        conn = {
            "host": self._resolve_host(self.host.get()),
            "port": self.port.get().strip(),
            "user": self.user.get().strip(),
            "pwd": self.pwd.get(),
            "topic": self.topic.get().strip(),
        }
        self._remove_tab_at(idx)
        win = tk.Toplevel(self.root)
        child = MqttToolApp(
            win,
            initial_tab_raw=raw,
            initial_tab_title=title,
            initial_connection=conn,
            parent_app=self,
            window_subtitle="独立实例 · %s" % title,
        )
        self._child_apps.append(child)
        win.protocol("WM_DELETE_WINDOW", lambda c=child, w=win: self._close_child_app(c, w))
        self._append_log("已打开独立窗口: " + title)

    def _close_child_app(self, child, win):
        if child._tabs:
            choice = messagebox.askyesnocancel(
                "关闭独立窗口",
                "是否先收回主界面？\n\n是 = 收回合并\n否 = 直接关闭\n取消 = 返回",
                parent=win,
            )
            if choice is None:
                return
            if choice:
                child._dock_to_parent()
                return
        if child in self._child_apps:
            self._child_apps.remove(child)
        win.destroy()

    def _open_log_viewer(self):
        viewer = getattr(self, "_log_viewer", None)
        try:
            if viewer is not None and viewer.winfo_exists():
                viewer.lift()
                viewer.focus_force()
                viewer._reload()
                return
        except tk.TclError:
            pass
        self._log_viewer = LogViewerDialog(self.root, self)
        self._log_viewer.bind("<Destroy>", lambda _e: setattr(self, "_log_viewer", None))

    def _show_toast(self, message, kind="info", duration=2600):
        if self._toast_job:
            try:
                self.root.after_cancel(self._toast_job)
            except tk.TclError:
                pass
            self._toast_job = None
        if self._toast_win:
            try:
                if self._toast_win.winfo_exists():
                    self._toast_win.destroy()
            except tk.TclError:
                pass
            self._toast_win = None
        styles = {
            "ok": (C["success_bg"], C["success"], C["success"]),
            "err": (C["error_bg"], C["error"], C["error"]),
            "info": (C["accent_soft"], C["text"], C["accent"]),
        }
        bg, fg, border = styles.get(kind, styles["info"])
        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        try:
            win.attributes("-topmost", True)
        except tk.TclError:
            pass
        shell = tk.Frame(win, bg=border)
        shell.pack(padx=1, pady=1)
        inner = tk.Frame(shell, bg=bg, padx=16, pady=10)
        inner.pack()
        tk.Label(inner, text=message, font=C["ui_bold"], fg=fg, bg=bg, justify=tk.LEFT).pack()
        win.update_idletasks()
        tw = win.winfo_reqwidth()
        th = win.winfo_reqheight()
        x = self.root.winfo_rootx() + max(self.root.winfo_width() - tw - 24, 8)
        y = self.root.winfo_rooty() + max(self.root.winfo_height() - th - 72, 8)
        win.geometry("+%d+%d" % (x, y))
        self._toast_win = win

        def _hide():
            try:
                if self._toast_win and self._toast_win.winfo_exists():
                    self._toast_win.destroy()
            except tk.TclError:
                pass
            self._toast_win = None
            self._toast_job = None

        self._toast_job = self.root.after(duration, _hide)

    def _refresh_log_display(self):
        try:
            self.log.see("1.0")
            self.log.update_idletasks()
        except tk.TclError:
            pass
        viewer = getattr(self, "_log_viewer", None)
        try:
            if viewer is not None and viewer.winfo_exists():
                viewer._reload()
        except tk.TclError:
            self._log_viewer = None

    def _log_clear_hits(self):
        self.log.tag_remove("log_hit", "1.0", tk.END)
        self._log_hits = []
        self._log_hit_idx = 0

    def _log_search_next(self):
        keyword = self.log_search_var.get().strip()
        if not keyword:
            return
        self._log_clear_hits()
        start = "1.0"
        while True:
            pos = self.log.search(keyword, start, stopindex=tk.END, nocase=True)
            if not pos:
                break
            end = "%s+%dc" % (pos, len(keyword))
            self.log.tag_add("log_hit", pos, end)
            self._log_hits.append(pos)
            start = end
        if not self._log_hits:
            return
        pos = self._log_hits[self._log_hit_idx % len(self._log_hits)]
        self.log.see(pos)
        self._log_hit_idx = (self._log_hit_idx + 1) % len(self._log_hits)

    def _select_tab(self, idx):
        if idx < 0 or idx >= len(self._tabs):
            return
        for tab in self._tabs:
            tab.hide()
        self._active_tab_idx = idx
        self._tabs[idx].show()
        self._render_tab_bar()
        self._update_window_caption()

    def add_payload_tab(self, title=None, data=None):
        self._tab_counter += 1
        title = title or ("窗口 %d" % self._tab_counter)
        for tab in self._tabs:
            tab.hide()
        tab = PayloadTab(
            self.content_stack,
            title,
            on_change=self._on_tab_content_change,
            on_sn_change=self._on_tab_sn_change,
        )
        self._tabs.append(tab)
        self._active_tab_idx = len(self._tabs) - 1
        tab.show()
        self._render_tab_bar()
        if data is not None:
            tab.fill(data)
        return tab

    def _close_tab(self, idx):
        if len(self._tabs) <= 1:
            messagebox.showinfo("提示", "至少保留一个发送窗口", parent=self.root)
            return
        tab = self._tabs.pop(idx)
        tab.frame.destroy()
        if self._active_tab_idx >= len(self._tabs):
            self._active_tab_idx = len(self._tabs) - 1
        elif idx < self._active_tab_idx:
            self._active_tab_idx -= 1
        for t in self._tabs:
            t.hide()
        self._tabs[self._active_tab_idx].show()
        self._render_tab_bar()

    def _close_active_tab(self):
        self._close_tab(self._active_tab_idx)

    def active_tab(self):
        if not self._tabs:
            return None
        return self._tabs[self._active_tab_idx]

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
            "host_alias": {},
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
                        if key == "host_alias":
                            raw = data.get(key)
                            if isinstance(raw, dict):
                                defaults[key] = {str(k): str(v) for k, v in raw.items() if str(k).strip() and str(v).strip()}
                            continue
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
        if key == "host":
            value = self._resolve_host(value)
        items = list(self.history.get(key) or [])
        if value in items:
            items.remove(value)
        items.insert(0, value)
        self.history[key] = items[:50]
        combo = self._history_widgets.get(key)
        if combo:
            if key == "host":
                self._refresh_host_combo(keep_host=value)
            else:
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
        if key == "host":
            host = self._resolve_host(value)
            items = list(self.history.get(key) or [])
            if host in items:
                items.remove(host)
                self.history[key] = items
                aliases = self.history.get("host_alias") or {}
                if host in aliases:
                    del aliases[host]
                self._persist_history()
                self._refresh_host_combo(keep_host=items[0] if items else None)
                self._append_log("已删除历史: " + self._host_label(host))
            return
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

    def _refresh_template_combo(self, select=None):
        names = list(self.templates.keys())
        self.template_combo.configure(values=names)
        if select and select in self.templates:
            self.template_combo.set(select)
        elif self.template_combo.get() not in self.templates and names:
            self.template_combo.set(names[0])

    def _open_template_manager(self):
        TemplateManagerDialog(self.root, self)

    def _create_template_quick(self):
        name = simpledialog.askstring("新增模版", "模版名称", parent=self.root)
        if not name:
            return
        name = name.strip()
        if not name:
            return
        if name in self.templates:
            if not messagebox.askyesno("覆盖", "模版已存在，是否用当前窗口内容覆盖？", parent=self.root):
                return
        try:
            body = self.active_tab().read_json()
        except Exception:
            body = {"name": "newMessage", "sn": "", "muid": "", "timestamp": "", "version": "v2.0.0", "data": {}}
        self.templates[name] = body
        self._persist_templates()
        self._refresh_template_combo(name)
        self._append_log("已新增模版: " + name)

    def _apply_selected_template(self):
        name = self.template_combo.get().strip()
        if name:
            self.apply_template(name)

    def apply_template(self, name):
        data = self.templates.get(name)
        if not data:
            return
        payload = json.loads(json.dumps(data, ensure_ascii=False))
        if self.sync_sn.get() and "sn" in payload:
            sn = self._topic_sn()
            if sn:
                payload["sn"] = sn
        tab = self.active_tab()
        if tab:
            tab.fill(payload)
            if self._is_auto_tab_title(tab.title):
                tab.title = self._unique_tab_title(name)
                self._render_tab_bar()
                self._update_window_caption()

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

    def _append_log(self, msg, level=None, detail=None):
        if level is None:
            if msg.startswith("发送成功"):
                level = "ok"
            elif "失败" in msg or "无效" in msg:
                level = "err"
            else:
                level = "info"
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        badges = {"ok": "成功", "err": "错误", "info": "信息", "warn": "警告"}
        badge = badges.get(level, "信息")
        tag = "log_ok" if level == "ok" else ("log_err" if level == "err" else "log_info")
        lines = [
            ("", None),
            ("─" * 58, "log_sep"),
            ("%s    %-4s    %s" % (ts, badge, msg), tag),
        ]
        if detail:
            text = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False, indent=2)
            for dl in text.splitlines():
                lines.append(("    " + dl, "log_detail"))
        self.log.configure(state=tk.NORMAL)
        for content, line_tag in reversed(lines):
            if line_tag:
                self.log.insert("1.0", content + "\n", line_tag)
            else:
                self.log.insert("1.0", content + "\n")
        self.log.see("1.0")
        self.log.configure(state=tk.DISABLED)
        self._log_clear_hits()

    def _send(self):
        tab = self.active_tab()
        if tab:
            self._send_tab(tab, tab.title, self.send_btn)

    def _send_tab(self, tab, title=None, done_btn=None):
        if not tab:
            return
        title = title or getattr(tab, "title", "窗口")
        try:
            body = tab.read_json()
        except json.JSONDecodeError as e:
            self._append_log("JSON 无效: " + str(e))
            tab._set_status("JSON 无效 · %s" % e.msg, "err")
            return
        except ValueError as e:
            self._append_log(str(e))
            return
        host = self._resolve_host(self.host.get())
        topic = self.topic.get().strip()
        user = self.user.get().strip()
        pwd = self.pwd.get()
        try:
            port = int(self.port.get().strip())
        except ValueError:
            self._append_log("Port 必须是数字", level="err")
            return
        if not host or not topic:
            self._append_log("Host / 主题不能为空", level="err")
            return
        self._remember("host", host)
        self._remember("port", str(port))
        self._remember("user", user)
        self._remember("topic", topic)
        btn = done_btn or self.send_btn
        btn.configure(state=tk.DISABLED)
        self._append_log("正在发送 [%s] -> %s  %s" % (title, self._host_label(host), topic))
        threading.Thread(
            target=self._do_send,
            args=(host, port, topic, user, pwd, body, tab, self.auto_sign.get(), self.auto_trigger_time.get(), btn),
            daemon=True,
        ).start()

    def _do_send(self, host, port, topic, user, pwd, body, tab, auto_sign, auto_trigger_time, done_btn=None):
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
            self.root.after(0, lambda t=tab, p=pretty, m=message, b=done_btn: self._on_send_done(True, t, m, p, b))
        except Exception as e:
            err = str(e)
            self.root.after(0, lambda t=tab, m=err, b=done_btn: self._on_send_done(False, t, m, None, b))

    def _on_send_done(self, ok, tab, detail, pretty=None, done_btn=None):
        btn = done_btn or self.send_btn
        btn.configure(state=tk.NORMAL)
        title = getattr(tab, "title", "窗口") if tab else "窗口"
        if ok:
            if pretty and tab:
                tab.fill(json.loads(pretty))
                tab._set_status("发送成功", "ok")
            self._append_log("发送成功", level="ok", detail=pretty or detail)
            self._refresh_log_display()
            self._show_toast("「%s」发送成功" % title, kind="ok")
        else:
            if tab:
                tab._set_status("发送失败", "err")
            self._append_log("发送失败: " + detail, level="err")
            self._refresh_log_display()
            self._show_toast("发送失败: %s" % detail, kind="err")


if __name__ == "__main__":
    root = tk.Tk()
    MqttToolApp(root)
    root.mainloop()
