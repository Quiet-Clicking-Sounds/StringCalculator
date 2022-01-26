import typing

import matplotlib
import numpy
from matplotlib import cm as matplotlib_cm
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from interface.instrument_class import Instrument, Note

matplotlib.use('TkAgg')

plot_func_type = typing.Callable[[Instrument, typing.Optional[tuple[int, int]]], Figure]
plot_type_dict: dict[str:plot_func_type] = dict()
marker = 'd'


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


class PlotCache:
    def __init__(self, colour_map: str = "viridis"):
        self._x = list()
        self._y = list()
        self._z = list()
        self._c = list()
        self._m = list()
        self._x_tick_mark = list()
        self._x_tick_name = list()
        self.colour_map: str = colour_map
        self._val_dict = dict()

    @property
    def x(self) -> list:
        return self._x

    @x.setter
    def x(self, value: int | float):
        self._x.append(value)

    @property
    def y(self) -> list:
        return self._y

    @y.setter
    def y(self, value: int | float):
        self._y.append(value)

    @property
    def z(self) -> list:
        return self._z

    @z.setter
    def z(self, value: int | float):
        self._z.append(value)

    @property
    def c(self) -> list:
        self._val_dict = dict.fromkeys(self._c)
        colour_count = len(self._val_dict)
        try:
            cmap = matplotlib_cm.get_cmap(self.colour_map)
        except ValueError:
            print(f"Error in cmap name, no cmap '{self.colour_map}' available, using 'viridis'")
            cmap = matplotlib_cm.get_cmap("viridis")
        self._val_dict = {key: cmap(1 / colour_count * val) for val, key in enumerate(list(self._val_dict))}
        return [self._val_dict[val] for val in self._c]

    @c.setter
    def c(self, value: str | int | float):
        self._c.append(value)

    @property
    def colour_dict(self) -> dict:
        return self._val_dict

    @property
    def poly_fit(self) -> numpy.ndarray:
        _fit = numpy.polyfit(self._x, self._y, 1)
        _poly = numpy.poly1d(_fit)
        return _poly(self._x)

    @property
    def x_tick_mark(self) -> list:
        return self._x_tick_mark

    @x_tick_mark.setter
    def x_tick_mark(self, value):
        self._x_tick_mark.append(value)

    @property
    def x_tick_name(self) -> list:
        return self._x_tick_name

    @x_tick_name.setter
    def x_tick_name(self, value):
        self._x_tick_name.append(value)

    def get_note_colour(self, note: Note):
        return self._val_dict[note.get_wire_type().name]


def poly_fit(x: list[float], y: list[int | float]) -> numpy.ndarray:
    z = numpy.polyfit(x, y, 1)
    p = numpy.poly1d(z)
    return p(x)


def fig_setup(fig_size_px=(1200, 800)) -> tuple[Figure, Axes, PlotCache]:
    dpi = 150
    fig = Figure(dpi=dpi,
                 figsize=(fig_size_px[0] / dpi,
                          fig_size_px[1] / dpi))
    ax: Axes = fig.subplots()
    fig.set_facecolor("darkgrey")
    ax.set_facecolor("darkgrey")
    cache = PlotCache()
    return fig, ax, cache


def _scatter(ax: Axes, cache: PlotCache, z=False, m: str | None = None, colour: str | tuple | None = None, **kwargs):
    ax.scatter(x=cache.x,
               y=cache.z if z else cache.y,
               c=cache.c if colour is None else colour,
               marker=marker if m is None else m,
               **kwargs)


def _bar(ax: Axes, cache: PlotCache, z=False, colour: str | tuple | None = None, **kwargs):
    ax.bar(x=cache.x,
           height=cache.z if z else cache.y,
           color=cache.c if colour is None else colour,
           **kwargs)


def _plot(ax: Axes, cache: PlotCache, z=False, m: str | None = None, colour: str | tuple | None = None, **kwargs):
    ax.plot(x=cache.x,
            y=cache.z if z else cache.y,
            c=cache.c if colour is None else colour,
            marker=marker if m is None else m,
            **kwargs)


def _poly(ax: Axes, cache: PlotCache, **kwargs):
    ax.plot(cache.x, cache.poly_fit, '-k', linewidth=0.5, **kwargs)


def _ticks(ax: Axes, cache: PlotCache):
    ax.set_xticks(cache.x_tick_mark)
    ax.set_xticklabels(cache.x_tick_name)


def _axis_callouts(ax: Axes, x: str | None = None, y: str | None = None, x2: str | None = None, y2: str | None = None):
    x_min, x_max, y_min, y_max = ax.axis()
    if x is not None:
        ax.text(x_min - 0.5, y_max + 0.5, x, horizontalalignment='right')
    if y is not None:
        ax.text(x_max + 0.5, y_min - 1.0, y, horizontalalignment='left')
    if x2 is not None:
        ax.text(x_max + 0.5, y_max + 0.5, x2, horizontalalignment='left')
    if y2 is not None:
        ax.text(x_max + 0.5, y_max + 1.0, y2, horizontalalignment='right')


def _colour_legend(ax: Axes, cache: PlotCache):
    (label_list, colour_list) = zip(*cache.colour_dict.items())
    ax.legend(label_list, labelcolor=colour_list, handlelength=0)


def _string_change_markers(ax: Axes, instrument: Instrument, p_cache: PlotCache | None = None):
    notes = instrument.note_list()
    change = [notes[0]]
    change.extend([b for a, b in zip(notes[:-1], notes[1:]) if
                   a.get_wire_type().code != b.get_wire_type().code])
    for note in change:
        annotate_colour = p_cache.get_note_colour(note) if p_cache is not None else "Black"
        ax.axvline(x=note.get_std_note_number() - 0.5,
                   ymin=0,
                   ymax=1,
                   color="Grey")
        ax.annotate(note.get_wire_type().name.replace(' ', '\n'),
                    xy=(note.get_std_note_number(),
                        0.2),
                    xycoords=('data', 'figure fraction'),
                    color=annotate_colour)


def plotter_tension(instrument: Instrument, fig_size_px=(1200, 800)) -> Figure:
    fig, ax, cache = fig_setup(fig_size_px)

    for note in instrument.iter_notes():
        x = note.get_std_note_number()
        cache.x = x
        cache.y = note.get_force().kg_force()
        cache.c = note.get_wire_type().name
        if x % 12 in {4}:
            cache.x_tick_mark = x
            cache.x_tick_name = note.get_std_note_name()

    # ax.scatter(x=cache.x, y=cache.y, c=cache.c, marker=marker)
    _scatter(ax, cache)
    _poly(ax, cache)
    _ticks(ax, cache)

    _string_change_markers(ax, instrument, cache)
    ax.set_ylim(bottom=0)
    _axis_callouts(ax, x="Kg-f", y="Note")

    _colour_legend(ax, cache)
    return fig


plot_type_dict['Tension'] = plotter_tension


def plotter_tension_diameter(instrument: Instrument, fig_size_px=(1200, 800)) -> Figure:
    fig, ax, cache = fig_setup(fig_size_px)

    for note in instrument.iter_notes():
        x = note.get_std_note_number()
        cache.x = x
        cache.y = note.get_force().kg_force()
        cache.z = note.get_diameter().mm()
        cache.c = note.get_wire_type().name
        if x % 12 in {4}:
            cache.x_tick_mark = x
            cache.x_tick_name = note.get_std_note_name()

    ax2 = ax.twinx()
    _scatter(ax2, cache, True, m='.', zorder=2)
    _scatter(ax, cache, colour="Black", zorder=1)
    _poly(ax, cache, zorder=3)
    _ticks(ax, cache)

    _string_change_markers(ax, instrument)
    ax.set_ylim(bottom=0)
    ax2.set_ylim(bottom=0)
    _axis_callouts(ax, x="Tension", y="Note", x2="Diameter")

    return fig


plot_type_dict['Tension & Diameter'] = plotter_tension_diameter


def plotter_string_diameter(instrument: Instrument, fig_size_px=(1200, 800)) -> Figure:
    fig, ax, cache = fig_setup(fig_size_px)

    for note in instrument.iter_notes():
        x = note.get_std_note_number()
        cache.x = x
        cache.y = note.get_diameter().mm()
        cache.c = note.get_force().kg_force()
        if x % 12 in {1, 4, 8, 11}:
            cache.x_tick_mark = x
            cache.x_tick_name = note.get_std_note_name()

    _scatter(ax, cache)
    _poly(ax, cache)
    _ticks(ax, cache)

    _string_change_markers(ax, instrument)
    ax.set_ylim(bottom=0)
    _axis_callouts(ax, x="Diameter", y="Note")

    # _colour_legend(ax, cache)
    return fig


plot_type_dict['Diameter'] = plotter_string_diameter
