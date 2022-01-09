import typing

import matplotlib
import numpy

from matplotlib.figure import Figure
from matplotlib.axes import Axes
from interface.instrument_class import Instrument, Note
matplotlib.use('TkAgg')

plot_func_type = typing.Callable[[Instrument, typing.Optional[tuple[int, int]]], Figure]
plot_type_dict: dict[str:plot_func_type] = dict()


class WireColour:
    def __init__(self, *args):
        self.wire_dict = {}
        self._colours = list('rgbkcmy')
        self._i = 0
        if args:
            self._colours = args

    def __call__(self, note: Note):
        code = note.get_wire_type().name
        if code not in self.wire_dict:
            self.wire_dict[code] = self.next_colour()
        return self.wire_dict[code]

    def next_colour(self):
        item = self._colours[self._i % len(self._colours)]
        self._i += 1
        return item


_base_wire_colour_ = WireColour()


def poly_fit(x, y):
    z = numpy.polyfit(x, y, 1)
    p = numpy.poly1d(z)
    return p(x)


def plotter_tension(instrument: Instrument, fig_size_px=(1200, 800)) -> Figure:
    dpi = 150
    fig = Figure(dpi=dpi,
                 figsize=(fig_size_px[0] / dpi,
                          fig_size_px[1] / dpi))
    ax: Axes = fig.subplots()
    marker = 'd'
    plot_x = []
    plot_y = []
    plot_c = []
    _x_tick_numbers = []
    _x_tick_names = []

    for note in instrument.iter_notes():
        x = note.get_std_note_number()
        plot_x.append(x)
        plot_y.append(note.get_force().kg_force())
        plot_c.append(_base_wire_colour_(note))
        if x % 12 in {1, 4, 8, 11}:
            _x_tick_numbers.append(x)
            _x_tick_names.append(note.get_std_note_name())

    ax.scatter(x=plot_x, y=plot_y, c=plot_c, marker=marker)
    ax.plot(plot_x, poly_fit(plot_x, plot_y), '.k')
    ax.set_xticks(_x_tick_numbers)
    ax.set_xticklabels(_x_tick_names)

    ax = string_change_markers(ax, instrument)
    x_min, x_max, y_min, y_max = ax.axis()

    ax.set_xlim(left=instrument.note_list()[0].get_std_note_number() - 1)
    ax.set_ylim(bottom=0)
    ax.text(x_min - 0.5, y_max + 0.5, 'Kgf', horizontalalignment='right')
    return fig


plot_type_dict['Tension'] = plotter_tension


def string_change_markers(ax: Axes, instrument: Instrument):
    notes = instrument.note_list()
    change = [notes[0]]
    change.extend([b for a, b in zip(notes[:-1], notes[1:]) if
                   a.get_wire_type().code != b.get_wire_type().code])
    for note in change:
        ax.axvline(x=note.get_std_note_number() - 0.5,
                   ymin=0,
                   ymax=1,
                   color="Grey")
        ax.annotate(note.get_wire_type().name.replace(' ', '\n'),
                    xy=(note.get_std_note_number(),
                        0.2),
                    xycoords=('data', 'figure fraction'),
                    color=_base_wire_colour_(note))
    return ax
