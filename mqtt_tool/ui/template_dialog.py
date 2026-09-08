# -*- coding: utf-8 -*-
import copy
import json
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from mqtt_tool.ui.theme import C, IC, _icon_font, _icon_text
from mqtt_tool.ui.widgets import (
    _bind_text_shortcuts,
    _card,
    _flat_btn,
    _scrollable_frame,
    _section_head,
    _styled_text,
)

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

