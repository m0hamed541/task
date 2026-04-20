"""TasksWindow — floating overlay GTK3 window."""

import threading

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

from api import complete_task, create_task, fetch_tasks
from style import force_white


class TasksWindow(Gtk.Window):
    def __init__(self) -> None:
        super().__init__(title="Tasks")
        self._setup_window()
        self._setup_ui()
        self._setup_tray()
        self._refresh_tasks()

    def _setup_window(self) -> None:
        self.set_default_size(300, 460)
        self.set_keep_above(True)
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_resizable(True)
        self.move(60, 60)
        self.connect("delete-event", lambda *_: self.hide() or True)

    def _setup_ui(self) -> None:
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(outer)
        outer.pack_start(self._build_header(), False, False, 0)
        outer.pack_start(self._build_task_area(), True, True, 0)
        outer.pack_end(self._build_footer(), False, False, 0)

    def _build_header(self) -> Gtk.Box:
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header.get_style_context().add_class("header-box")

        title = Gtk.Label(label="My Tasks")
        title.get_style_context().add_class("title-label")
        title.set_halign(Gtk.Align.START)
        header.pack_start(title, True, True, 0)

        for label, tooltip, callback in [
            ("↻", "Refresh", lambda _: self._refresh_tasks()),
            ("⌄", "Hide window", lambda _: self.hide()),
        ]:
            btn = Gtk.Button(label=label)
            btn.get_style_context().add_class("icon-btn")
            btn.set_tooltip_text(tooltip)
            btn.connect("clicked", callback)
            header.pack_end(btn, False, False, 0)

        return header

    def _build_task_area(self) -> Gtk.ScrolledWindow:
        scroll = Gtk.ScrolledWindow()
        scroll.get_style_context().add_class("task-area")
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        force_white(scroll)

        self._task_list = Gtk.ListBox()
        self._task_list.set_selection_mode(Gtk.SelectionMode.NONE)
        force_white(self._task_list)
        scroll.add(self._task_list)
        return scroll

    def _build_footer(self) -> Gtk.Box:
        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        footer.get_style_context().add_class("footer-bar")

        self._status_label = Gtk.Label(label="Loading…")
        self._status_label.get_style_context().add_class("status-label")
        self._status_label.set_halign(Gtk.Align.START)
        footer.pack_start(self._status_label, True, True, 0)

        add_btn = Gtk.Button(label="+ Add task")
        add_btn.get_style_context().add_class("add-btn")
        add_btn.connect("clicked", self._on_add_task)
        footer.pack_end(add_btn, False, False, 0)

        return footer

    def _setup_tray(self) -> None:
        self._tray = Gtk.StatusIcon()
        self._tray.set_from_icon_name("checkbox-checked-symbolic")
        self._tray.set_tooltip_text("Tasks — click to show/hide")
        self._tray.connect("activate", lambda _: self.toggle_visibility())
        self._tray.connect("popup-menu", self._on_tray_menu)

    def _on_tray_menu(self, _icon, button, time) -> None:
        menu = Gtk.Menu()

        show_item = Gtk.MenuItem(label="Show / Hide")
        show_item.connect("activate", lambda _: self.toggle_visibility())
        menu.append(show_item)
        menu.append(Gtk.SeparatorMenuItem())

        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", lambda _: Gtk.main_quit())
        menu.append(quit_item)

        menu.show_all()
        menu.popup(None, None, None, None, button, time)

    def toggle_visibility(self) -> None:
        if self.get_visible():
            self.hide()
        else:
            self.present()

    def _on_add_task(self, _) -> None:
        dialog = Gtk.Dialog(title="New Task", transient_for=self, modal=True)
        dialog.set_default_size(260, 120)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        ok_btn = dialog.add_button("Add", Gtk.ResponseType.OK)
        ok_btn.get_style_context().add_class("add-btn")
        dialog.set_default_response(Gtk.ResponseType.OK)

        entry = Gtk.Entry()
        entry.get_style_context().add_class("dialog-entry")
        entry.set_placeholder_text("Task title…")
        entry.set_activates_default(True)
        entry.set_margin_top(12)
        entry.set_margin_bottom(4)
        entry.set_margin_start(14)
        entry.set_margin_end(14)

        dialog.get_content_area().pack_start(entry, True, True, 0)
        dialog.show_all()

        response = dialog.run()
        title = entry.get_text().strip()
        dialog.destroy()

        if response == Gtk.ResponseType.OK and title:
            self._status_label.set_text("Adding…")
            threading.Thread(
                target=self._create_task_thread, args=(title,), daemon=True
            ).start()

    def _create_task_thread(self, title: str) -> None:
        try:
            create_task(title)
            GLib.idle_add(self._refresh_tasks)
        except Exception as e:
            GLib.idle_add(self._status_label.set_text, f"Error: {e}")

    def _refresh_tasks(self) -> None:
        self._status_label.set_text("Refreshing…")
        threading.Thread(target=self._load_tasks_thread, daemon=True).start()

    def _load_tasks_thread(self) -> None:
        try:
            tasks = fetch_tasks()
            GLib.idle_add(self._populate_tasks, tasks)
        except Exception as e:
            GLib.idle_add(self._status_label.set_text, f"Error: {e}")

    def _populate_tasks(self, tasks: list[dict]) -> bool:
        for child in self._task_list.get_children():
            self._task_list.remove(child)

        if not tasks:
            row = Gtk.ListBoxRow()
            lbl = Gtk.Label(label="No pending tasks")
            lbl.get_style_context().add_class("empty-label")
            lbl.set_halign(Gtk.Align.CENTER)
            row.add(lbl)
            self._task_list.add(row)
            self._status_label.set_text("All done!")
        else:
            self._status_label.set_text(f"{len(tasks)} pending task(s)")
            for task in tasks:
                self._task_list.add(self._make_task_row(task))

        self._task_list.show_all()
        return False

    def _make_task_row(self, task: dict) -> Gtk.ListBoxRow:
        row = Gtk.ListBoxRow()
        check = Gtk.CheckButton(label=task.get("title", "(no title)"))
        check.get_style_context().add_class("task-check")
        check.set_margin_top(2)
        check.set_margin_bottom(2)
        check.connect("toggled", self._on_task_toggled, task.get("id", ""), row)
        row.add(check)
        return row

    def _on_task_toggled(
        self, check: Gtk.CheckButton, task_id: str, row: Gtk.ListBoxRow
    ) -> None:
        if not check.get_active():
            return
        check.set_sensitive(False)
        threading.Thread(
            target=self._complete_task_thread, args=(task_id, row), daemon=True
        ).start()

    def _complete_task_thread(self, task_id: str, row: Gtk.ListBoxRow) -> None:
        try:
            complete_task(task_id)
            GLib.idle_add(self._remove_row, row)
        except Exception as e:
            GLib.idle_add(self._status_label.set_text, f"Error: {e}")

    def _remove_row(self, row: Gtk.ListBoxRow) -> bool:
        self._task_list.remove(row)
        remaining = len(self._task_list.get_children())
        if remaining == 0:
            self._populate_tasks([])
        else:
            self._status_label.set_text(f"{remaining} pending task(s)")
        return False
