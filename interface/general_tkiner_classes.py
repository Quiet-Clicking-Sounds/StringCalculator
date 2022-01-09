from __future__ import annotations

import json
import pathlib
import tkinter as tk
from tkinter import filedialog as tkFile
from tkinter import ttk

import definitions
from interface.instrument_class import Instrument


class Menu(tk.Menu):
    parent: tk.Tk
    instrument: Instrument

    def __init__(self, parent, instrument: Instrument):
        super(Menu, self).__init__(parent)
        self.parent = parent
        self.instrument = instrument

        self.add_file_menu()

    def add_file_menu(self):
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
    """"""
    frame: ttk.Frame
    canvas: tk.Canvas
    scroll: ttk.Scrollbar

    def __init__(self, parent):
        """ frame > [canvas > **self** | scroll]"""
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
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind('<Configure>', self.__fill_canvas)

    def on_configure(self, event):
        """Set the scroll region to encompass the scrolled frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def __fill_canvas(self, event):
        """Enlarge the windows item to the canvas width"""
        canvas_width = event.width
        self.canvas.itemconfig(self.window_item, width=canvas_width)
