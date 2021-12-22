from hashlib import sha1

import numpy
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator

import definitions
from instrument.instrument_classes import Instrument, Force


def poly_fit(x, y):
    z = numpy.polyfit(x, y, 1)
    p = numpy.poly1d(z)
    return p(x)


def numpy_hash(arr: numpy.ndarray) -> str:
    return sha1(arr.view(numpy.uint8)).hexdigest()


def plot_instrument(inst: Instrument) -> str:
    """
    :param inst: instrument to use as a base for the plot
    :return: string containing the url of the file
    """
    assert isinstance(inst, Instrument)
    fig, ax = plt.subplots()
    ax: plt.Axes
    fig: plt.Figure
    fig.set_size_inches(21/2,9/2)
    _x_tick_numbers = []
    _x_tick_names = []
    for note in inst.iter_notes():
        x = note.std_note
        y:Force = note.force()
        y=y.kg_force()

        ax.plot(x, y, marker=f'${chr(9679)}$', color="Black")
        # ax.plot(x, poly_fit(x, y), color="Grey")
        _x_tick_numbers.append(x)
        _x_tick_names.append(note.name())
    ax.set_xticks(_x_tick_numbers[6::12])
    ax.set_xticklabels(_x_tick_names[6::12])

    itnotes = [i for i in inst.iter_notes()]
    string_changes = [a for a, b in zip(itnotes[1:], itnotes[:-1])
                      if a.wire_material.code != b.wire_material.code]

    note_pos = 0.75

    ax.annotate(itnotes[0].wire_material.name, xy=(1.5,0.75))
    for st in string_changes:
        ax.axvline(x=st.std_note + 0.5, ymin=0.25, ymax=note_pos, color="Grey")
        ax.annotate(st.wire_material.name, xy=(st.std_note + 0.5, note_pos))

    ax.xaxis.set_minor_locator(MultipleLocator(1))
    xmin, xmax, ymin, ymax = plt.axis()
    ax.text(xmin - 0.5, ymax + 2.5, 'Kgf', horizontalalignment='right')
    filename = f'image_cache/{hash(f"inst.note_dictionary()")}.jpg'
    plt.savefig(definitions.ROOT_DIR / filename, dpi=150)
    return filename


if __name__ == '__main__':
    basic = {'lowest_key': 'F1', 'highest_key': 'B2', 'pitch': '440'}
    output = [['21', 'F1', '87.307058', '1', '1230', '0.5', '2', ''],
              ['22', 'F♯1', '92.498606', '2', '1230', '0.5', '1', ''],
              ['23', 'G1', '97.998859', '1', '1230', '0.5', '2', ''],
              ['24', 'G♯1', '103.826174', '2', '1230', '0.5', '1'''],
              ['25', 'A2', '110.000000', '1', '1230', '0.5', '2', ''],
              ['26', 'A2', '110.000000', '1', '1230', '0.5', '2', ''],
              ['27', 'A2', '110.000000', '1', '1230', '0.5', '2', ''],
              ['' ,'','']
              ]
    instrument = Instrument(**basic)
    instrument.update_notes_from_lists(output)
    plot_instrument(instrument)
