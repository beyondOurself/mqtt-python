# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk

from mqtt_tool.ui.theme import C, IC, _icon_font, _icon_text, _mono_font

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


class _FlowFrame(tk.Frame):
    def __init__(self, parent, bg, gap_x=16, gap_y=8, **kw):
        tk.Frame.__init__(self, parent, bg=bg, **kw)
        self._bg = bg
        self._gap_x = gap_x
        self._gap_y = gap_y
        self._items = []
        self._busy = False
        self.pack_propagate(False)
        self.bind("<Configure>", self._reflow)

    def add(self, widget):
        self._items.append(widget)
        widget.place(x=0, y=0)
        self.after_idle(self._reflow)

    def _reflow(self, event=None):
        if self._busy:
            return
        width = self.winfo_width()
        if width <= 1:
            return
        self._busy = True
        try:
            x = 0
            y = 0
            row_h = 0
            for widget in self._items:
                widget.update_idletasks()
                iw = widget.winfo_reqwidth()
                ih = widget.winfo_reqheight()
                if x > 0 and x + iw > width:
                    x = 0
                    y += row_h + self._gap_y
                    row_h = 0
                widget.place(x=x, y=y)
                x += iw + self._gap_x
                row_h = max(row_h, ih)
            need_h = max(y + row_h, 1)
            if int(self.cget("height") or 0) != need_h:
                self.configure(height=need_h)
        finally:
            self._busy = False


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

