from __future__ import annotations

import tkinter as tk

from ttkthemes import ThemedStyle

from interface.general_tkiner_classes import Scrollable, Menu
from interface.instrument_class import Instrument
from interface.visualization import PlotFrame

def run_interface() -> tk.Tk:
    root = tk.Tk()
    root.title("Stringing Calculator")
    root.geometry("600x600")

    scroll_area = Scrollable(root)
    scroll_area.pack(fill='both', expand=True, side=tk.LEFT)
    app = Instrument(scroll_area)
    app.pack(fill='both', expand=0)# , side=tk.LEFT)

    plt = PlotFrame(root, app)
    plt.pack(fill='both', expand=True, side=tk.RIGHT)

    top = root.winfo_toplevel()
    menu_bar = Menu(top, app)
    top['menu'] = menu_bar

    style = ThemedStyle(root)
    style.set_theme("black")
    style.configure('TEntry', bg="#4f5358", fg="#4f5358")
    style.configure('TCombobox', bg="#4f5358", fg="#4f5358")
    return root


if __name__ == '__main__':
    program_root = run_interface()
    program_root.mainloop()
