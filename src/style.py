"""CSS theme and helpers."""

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk

colors = {
    "main_blue": "#0b57d0",
}


CSS = b"""
@define-color main_blue #0b57d0;
window {
    background-color: #ffffff;
    color: #1f2328;
}
.header-box {
    background-color: #f6f8fa;
    padding: 10px 14px;
    border-bottom: 1px solid #d0d7de;
}
.title-label {
    color: @main_blue;
    font-size: 15px;
    font-weight: bold;
    letter-spacing: 0.5px;
}
.icon-btn {
    background: transparent;
    border: none;
    border-radius: 6px;
    color: @main_blue;
    padding: 4px 6px;
    min-width: 0;
    min-height: 0;
}
.icon-btn:hover {
    color: #1f2328;
    background-color: #e8ecf0;
}
.add-btn {
    background-color: white;
    color: @main_blue;
    border-radius: 8px;
    padding: 5px 12px;
    font-weight: bold;
    font-size: 13px;
}
.add-btn:hover {
    background-color: #1729e6;
}
.task-area,
.task-area > viewport,
scrolledwindow,
viewport {
    background-color: #ffffff;
    border: none;
}
listbox {
    background-color: #ffffff;
    border: none;
}
listboxrow {
    background-color: #ffffff;
    border-bottom: 1px solid #eaeef2;
    padding: 2px 0;
    transition: background-color 150ms;
}
listboxrow:hover {
    background-color: #f6f8fa;
}
.task-check {
    color: #1f2328;
    font-size: 13px;
    padding: 6px 10px;
}
.task-check check {
    background-color: #ffffff;
    border: 1.5px solid #d0d7de;
    border-radius: 4px;
    min-width: 16px;
    min-height: 16px;
}
.task-check:checked check {
    background-color: #2da44e;
    border-color: #2da44e;
}
.task-check:checked label {
    color: #8c959f;
    text-decoration-line: line-through;
}
.status-label {
    color: #8c959f;
    font-size: 11px;
    padding: 6px 0 4px;
}
.empty-label {
    color: #57606a;
    font-size: 13px;
    padding: 30px 10px;
}
.footer-bar {
    background-color: #f6f8fa;
    border-top: 1px solid #d0d7de;
    padding: 6px 14px;
}
dialog {
    background-color: #ffffff;
}
.dialog-entry {
    background-color: #f6f8fa;
    color: #1f2328;
    border: 1.5px solid #d0d7de;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    caret-color: #0969da;
}
.dialog-entry:focus {
    border-color: #0969da;
}
"""


WHITE = Gdk.RGBA(1, 1, 1, 1)
NEAR_WHITE = Gdk.RGBA(0.965, 0.973, 0.980, 1)  # #f6f8fa
DARK = Gdk.RGBA(0.122, 0.137, 0.157, 1)  # #1f2328


def apply_css() -> None:
    settings = Gtk.Settings.get_default()
    settings.set_property("gtk-application-prefer-dark-theme", False)
    try:
        settings.set_property("gtk-theme-name", "Adwaita")
    except Exception:
        pass

    provider = Gtk.CssProvider()
    provider.load_from_data(CSS)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(),
        provider,
        Gtk.STYLE_PROVIDER_PRIORITY_USER,
    )


def force_white(widget: Gtk.Widget) -> None:
    """Programmatically override background for widgets the theme keeps hijacking."""
    widget.override_background_color(Gtk.StateFlags.NORMAL, WHITE)
