from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


from instrument import Instrument
from interface.general_tkiner_classes import Scrollable
from interface.visualization_plotting import plot_type_dict, plot_func_type


class PlotFrame(ttk.Frame):
    def __init__(self, parent, instrument: Instrument):
        super(PlotFrame, self).__init__(parent)
        self.instrument = instrument
        # header fixed to the top of the screen
        self.header = PlotHeader(self)
        self.header.pack(fill='x', expand=False, side="top")
        # Scrollable for the plots (for if there are more than can fit vertically on the screen)
        self.scroll_area = Scrollable(self)
        self.scroll_area.pack(fill='both', expand=True, side="bottom")
        # plot body for all plots to be placed - also the creator of said plots
        self.plot_body = PlotBody(self.scroll_area, self.instrument)
        self.plot_body.pack(fill='both', expand=True, side="bottom")

    def create_plot(self, name: str):
        self.plot_body.new_plot(name)

    def update_plots(self):
        self.plot_body.update_plots()


class PlotHeader(ttk.Frame):
    def __init__(self, parent: PlotFrame):
        super(PlotHeader, self).__init__(parent)
        self.parent = parent
        max_cols = 4

        # add plot buttons
        for n, key in enumerate(plot_type_dict.keys()):
            button = ttk.Button(self, text=key,
                                command=lambda key=key: self.parent.create_plot(key))
            button.grid(row=n // max_cols, column=n % max_cols)

        # Update all
        button = ttk.Button(self, text="Update\nAll", command=self.parent.update_plots)
        button.grid(row=0, rowspan=15, column=max_cols + 1)


class PlotBody(ttk.Frame):
    def __init__(self, parent, instrument:Instrument):
        super(PlotBody, self).__init__(parent)
        self.instrument = instrument
        self.plots: dict[str: tk.Canvas] = dict()

    def new_plot(self, name='Tension'):
        if name in self.plots:
            # destroy previous version
            self.plots[name].destroy()

        fig: plot_func_type = plot_type_dict[name](self.instrument,(1920,800))
        canvas = FigureCanvasTkAgg(fig, self)
        widget = canvas.get_tk_widget()
        widget.pack(fill='x', expand=True, side="top")
        self.plots[name] = widget

    def update_plots(self):
        for key in list(self.plots.keys()):
            self.new_plot(name=key)
