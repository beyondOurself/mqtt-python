# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk

from mqtt_tool.ui.theme import C, IC, _icon_font, _icon_text
from mqtt_tool.ui.widgets import _flat_btn, _styled_text

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

