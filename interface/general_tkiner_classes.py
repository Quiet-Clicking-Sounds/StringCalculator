from __future__ import annotations

import json
import pathlib
import tkinter as tk
from tkinter import filedialog as tkFile
from tkinter import ttk

from ttkthemes import ThemedStyle

import definitions
from interface.instrument_class import Instrument
from interface.visualization import PlotFrame


class TkInterface(tk.Tk):
    scroll_area: Scrollable
    instrument: Instrument
    plt: PlotFrame

    def __init__(self, title="Stringing Calculator", geometry="900x900"):
        """
        Usage::
            program_root = TkInterface()\n
            program_root.mainloop()
        """
        super(TkInterface, self).__init__()
        self.title(title)
        self.geometry(geometry)

        self.width_breakpoint = 1200
        self._current_layout_ = None

        self.scroll_area = Scrollable(self, bind_mousewheel=True)
        self.instrument = Instrument(self.scroll_area)
        self.instrument.pack(fill='x', expand=0)
        self.plt = PlotFrame(self, self.instrument)

        # set positions of self.scroll_area & self.plt based on the size of the window
        if self.winfo_width() < self.width_breakpoint:
            self.set_vertical_layout()
        else:
            self.set_horizontal_layout()

        self.bind("<Control-l>", self.__swap_layout)
        self.bind("<Control-L>", self.__swap_layout)

        top = self.winfo_toplevel()
        menu_bar = Menu(top, self.instrument)
        top['menu'] = menu_bar

        style = ThemedStyle(self)
        style.set_theme("black")
        style.configure('TEntry', bg="#4f5358", fg="#4f5358")
        style.configure('TCombobox', bg="#4f5358", fg="#4f5358")

    def __forget_packing(self):
        for item in [self.scroll_area, self.plt]:
            try:
                item.pack_forget()
            except Exception as e:
                raise e

    def __swap_layout(self, *args):
        if self._current_layout_ == 0:
            self.set_horizontal_layout()
        else:
            self.set_vertical_layout()

    def set_vertical_layout(self):
        """ set the layout to vertical with the graphing output below the instrument """
        self.__forget_packing()
        try:
            self.scroll_area.pack(fill='both', expand=True, side=tk.TOP)
            self.plt.pack(fill='both', expand=True, side=tk.BOTTOM)
        finally:
            self._current_layout_ = 0

    def set_horizontal_layout(self):
        """ set the layout to horizontal with the graphing output right of the instrument """
        self.__forget_packing()
        try:
            self.scroll_area.pack(fill='both', expand=True, side=tk.LEFT)
            self.plt.pack(fill='both', expand=True, side=tk.RIGHT)
        finally:
            self._current_layout_ = 1


class Menu(tk.Menu):
    parent: TkInterface
    instrument: Instrument

    def __init__(self, parent: TkInterface, instrument: Instrument):
        super(Menu, self).__init__(parent)
        self.parent = parent
        self.instrument = instrument
        self.option_add('*tearOff', False)
        self._add_file_menu()
        self._add_layout_menu()

    def _add_file_menu(self):
        menu = tk.Menu(self)
        self.add_cascade(label="File", menu=menu)

        menu.add_command(label="Open Ctrl+O", command=self.__open_handler)
        self.parent.bind("<Control-o>", self.__open_handler)
        self.parent.bind("<Control-O>", self.__open_handler)
        menu.add_command(label="Save Ctrl+S", command=self.__save_handler)
        self.parent.bind("<Control-s>", self.__save_handler)
        self.parent.bind("<Control-S>", self.__save_handler)
        menu.add_command(label="Save as Ctrl+Shift+S", command=self.__save_as_handler)
        self.parent.bind("<Control-Shift-s>", self.__save_as_handler)
        self.parent.bind("<Control-Shift-S>", self.__save_as_handler)

    def _add_layout_menu(self):
        menu = tk.Menu(self)
        self.add_cascade(label="Layout", menu=menu)
        menu.add_command(label="Vertical Layout", command=self.parent.set_vertical_layout)
        menu.add_command(label="Horizontal Layout", command=self.parent.set_horizontal_layout)

    def __open_handler(self, *arg):
        """ Open a file dialogue, to import previous instance of the program """
        file = tkFile.askopenfilename(title="Open File", initialdir="/", filetypes=definitions.file_types)
        if not file:
            return
        file = pathlib.Path(file)
        if not file.suffix:
            file = file.with_suffix('.json')
        with open(file, 'r') as f:
            import_data = json.loads(f.read())
        self.instrument.state_import(import_data)

    def __save_handler(self, *arg, force_new_save=False):
        """ Open a file dialogue, to export the current instance of the program """
        if force_new_save or self.instrument.file_uri is None:
            file = tkFile.asksaveasfilename(title="Open File", initialdir="/", filetypes=definitions.file_types)
            if not file:
                return
            file = pathlib.Path(file)
        else:
            file = self.instrument.file_uri
        if not file.suffix:
            file = file.with_suffix('.json')
        export_data = self.instrument.state_export()
        with open(file, 'w' if file.exists() else 'x') as f:
            f.write(json.dumps(export_data))

    def __save_as_handler(self, *arg):
        return self.__save_handler(force_new_save=True)


class Scrollable(ttk.Frame):
    frame: ttk.Frame
    canvas: tk.Canvas
    scroll: ttk.Scrollbar

    def __init__(self, parent, bind_mousewheel=False):
        """
        frame > [canvas > **self** | scroll]
        This frame is set to accept the positioning arguments listed below,
        these apply to the **parent frame** not the instance of Scrollable::
            .grid(), .grid_configure(), .grid_columnconfigure(), .grid_rowconfigure(),
            .pack(), .pack_configure(), .pack_info()
        """
        # If this breaks have another look at https://stackoverflow.com/q/3085696
        self.frame = ttk.Frame(parent)
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        self.grid = self.frame.grid
        self.grid_configure = self.frame.grid_configure
        self.grid_columnconfigure = self.frame.grid_columnconfigure
        self.grid_rowconfigure = self.frame.grid_rowconfigure
        self.pack = self.frame.pack
        self.pack_configure = self.frame.pack_configure
        self.pack_info = self.frame.pack_info

        self.canvas = tk.Canvas(self.frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scroll = ttk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.scroll.set, bg="blue")
        self.scroll.configure(command=self.canvas.yview)

        super(Scrollable, self).__init__(self.canvas)
        self.window_item = self.canvas.create_window(0, 0, window=self, anchor=tk.NW)

        self.bind("<Configure>", self.on_configure)
        if bind_mousewheel:
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind('<Configure>', self.__fill_canvas)

    def on_configure(self, event):
        """Set the scroll region to encompass the scrolled frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_mousewheel(self, event):
        """ move the canvas based on the event.delta given (for mousewheel or similar) """
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def __fill_canvas(self, event):
        """Enlarge the windows item to the canvas width"""
        canvas_width = event.width
        self.canvas.itemconfig(self.window_item, width=canvas_width)
