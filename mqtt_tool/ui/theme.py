# -*- coding: utf-8 -*-
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

