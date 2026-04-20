"""Entry point."""

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from style import apply_css
from window import TasksWindow


def main() -> None:
    apply_css()
    win = TasksWindow()
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
